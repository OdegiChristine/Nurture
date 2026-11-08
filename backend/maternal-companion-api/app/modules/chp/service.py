import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.alerts.models import Alert
from app.modules.chp.models import Chp
from app.modules.mothers.models import Mother


async def create_chp(
    session: AsyncSession, *, name: str, email: str, password: str, county: str, role: str = "chp"
) -> Chp:
    chp = Chp(
        name=name,
        email=email.lower(),
        password_hash=hash_password(password),
        county=county,
        role=role,
    )
    session.add(chp)
    await session.flush()
    if role == "chp":
        await claim_orphans(session, chp)
    await session.commit()
    return chp


async def claim_orphans(session: AsyncSession, chp: Chp) -> int:
    """A new CHP adopts mothers in her county who were registered before any CHP existed,
    along with those mothers' unrouted open alerts."""
    ids = list(
        (
            await session.execute(
                select(Mother.id).where(Mother.chp_id.is_(None), Mother.county == chp.county)
            )
        ).scalars()
    )
    if not ids:
        return 0
    await session.execute(update(Mother).where(Mother.id.in_(ids)).values(chp_id=chp.id))
    await session.execute(
        update(Alert)
        .where(Alert.mother_id.in_(ids), Alert.chp_id.is_(None), Alert.status != "resolved")
        .values(chp_id=chp.id)
    )
    return len(ids)


async def pick_alert_recipient(session: AsyncSession, mother: Mother) -> uuid.UUID | None:
    """Who must see this mother's alerts: her CHP; else a supervisor (same county first);
    else nobody (the alert is 'unrouted' and surfaces on the oversight endpoint).
    An alert must never be silently dropped just because a mother has no CHP."""
    if mother.chp_id:
        return mother.chp_id
    base = (
        select(Chp.id)
        .where(Chp.is_active.is_(True), Chp.role == "supervisor")
        .order_by(Chp.created_at)
        .limit(1)
    )
    for stmt in (base.where(Chp.county == mother.county), base):
        found = (await session.execute(stmt)).scalar_one_or_none()
        if found:
            return found
    return None


async def assign_chp(session: AsyncSession, county: str) -> uuid.UUID | None:
    """Least-loaded active CHP in the mother's county. None if the county has no CHP yet.

    Replace with ward/village-level assignment once you have the CHU register.
    """
    load = (
        select(Chp.id, func.count(Mother.id).label("load"))
        .outerjoin(Mother, Mother.chp_id == Chp.id)
        .where(Chp.county == county, Chp.is_active.is_(True), Chp.role == "chp")
        .group_by(Chp.id)
        .order_by("load")
        .limit(1)
    )
    row = (await session.execute(load)).first()
    return row.id if row else None
