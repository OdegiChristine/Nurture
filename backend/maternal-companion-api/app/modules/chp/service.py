import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
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
    await session.commit()
    return chp


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
