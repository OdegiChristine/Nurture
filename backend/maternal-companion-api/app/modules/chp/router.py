import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit
from app.core.db import get_session
from app.core.deps import Principal, chp_only
from app.core.errors import UnauthorizedError
from app.core.security import create_access_token, decrypt_field, hash_password, verify_password
from app.core.time import as_utc, utcnow
from app.modules.alerts import service as alert_service
from app.modules.alerts.models import Alert
from app.modules.checkins.models import CheckIn
from app.modules.chp.models import Chp
from app.modules.mothers.models import Mother
from app.modules.mothers.service import consented_mother_ids
from app.modules.triage.engine import Tier

router = APIRouter(tags=["chp"])

# Burn CPU on unknown emails too, so login timing doesn't reveal which emails exist.
_DUMMY_HASH = hash_password("not-a-real-password")


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


@router.post("/v1/auth/chp/login", response_model=TokenOut)
async def login(body: LoginIn, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Chp).where(Chp.email == body.email.lower()))
    chp = result.scalar_one_or_none()
    ok = verify_password(chp.password_hash if chp else _DUMMY_HASH, body.password)
    if not chp or not ok or not chp.is_active:
        raise UnauthorizedError("Invalid credentials")
    return TokenOut(access_token=create_access_token(str(chp.id), chp.role))


class CohortItem(BaseModel):
    mother_id: uuid.UUID
    pseudonym: str | None
    county: str
    gestation_weeks: int
    latest_tier: str | None
    last_checkin_at: datetime | None
    days_since_contact: int | None
    open_alerts: int
    phone: str | None  # only present if the mother consented to CHP contact


# Mothers who have never checked in sort like "moderate": they need a nudge before low-risk ones.
_UNKNOWN_RANK = Tier.MODERATE.rank


@router.get("/v1/chp/cohort", response_model=list[CohortItem])
async def cohort(
    principal: Principal = chp_only,
    session: AsyncSession = Depends(get_session),
):
    # Cohort scoping is enforced in the query itself, not just in the endpoint.
    mothers = list(
        (await session.execute(select(Mother).where(Mother.chp_id == principal.id))).scalars()
    )
    ids = [m.id for m in mothers]
    if not ids:
        return []

    ranked = (
        select(
            CheckIn.mother_id,
            CheckIn.risk_tier,
            CheckIn.received_at,
            func.row_number()
            .over(partition_by=CheckIn.mother_id, order_by=CheckIn.received_at.desc())
            .label("rn"),
        )
        .where(CheckIn.mother_id.in_(ids))
        .subquery()
    )
    latest = {
        r.mother_id: r
        for r in (await session.execute(select(ranked).where(ranked.c.rn == 1))).all()
    }
    open_counts = dict(
        (
            await session.execute(
                select(Alert.mother_id, func.count())
                .where(Alert.mother_id.in_(ids), Alert.status != "resolved")
                .group_by(Alert.mother_id)
            )
        ).all()
    )
    reveal = await consented_mother_ids(session, ids, "chp_contact")

    items: list[CohortItem] = []
    now = utcnow()
    for m in mothers:
        last = latest.get(m.id)
        phone = decrypt_field(m.phone_enc) if m.id in reveal else None
        if phone:
            audit(
                session,
                actor_id=principal.id,
                actor_role="chp",
                action="phone_revealed",
                resource_type="mother",
                resource_id=m.id,
            )
        items.append(
            CohortItem(
                mother_id=m.id,
                pseudonym=m.pseudonym,
                county=m.county,
                gestation_weeks=m.current_gestation_weeks(),
                latest_tier=last.risk_tier if last else None,
                last_checkin_at=last.received_at if last else None,
                days_since_contact=(now - as_utc(last.received_at)).days if last else None,
                open_alerts=open_counts.get(m.id, 0),
                phone=phone,
            )
        )
    await session.commit()

    def sort_key(i: CohortItem):
        rank = Tier(i.latest_tier).rank if i.latest_tier else _UNKNOWN_RANK
        stale_first = -(i.days_since_contact if i.days_since_contact is not None else 10_000)
        return (-rank, stale_first)

    items.sort(key=sort_key)
    return items


class AlertOut(BaseModel):
    id: uuid.UUID
    mother_id: uuid.UUID
    tier: str
    status: str
    created_at: datetime


class ResolveIn(BaseModel):
    note: str


def _alert_out(a: Alert) -> AlertOut:
    return AlertOut(
        id=a.id, mother_id=a.mother_id, tier=a.tier, status=a.status, created_at=a.created_at
    )


@router.get("/v1/chp/alerts", response_model=list[AlertOut])
async def my_alerts(
    principal: Principal = chp_only,
    session: AsyncSession = Depends(get_session),
):
    return [_alert_out(a) for a in await alert_service.list_open_for_chp(session, principal.id)]


@router.post("/v1/chp/alerts/{alert_id}/acknowledge", response_model=AlertOut)
async def acknowledge(
    alert_id: uuid.UUID,
    principal: Principal = chp_only,
    session: AsyncSession = Depends(get_session),
):
    return _alert_out(await alert_service.acknowledge(session, alert_id, principal.id))


@router.post("/v1/chp/alerts/{alert_id}/resolve", response_model=AlertOut)
async def resolve(
    alert_id: uuid.UUID,
    body: ResolveIn,
    principal: Principal = chp_only,
    session: AsyncSession = Depends(get_session),
):
    return _alert_out(await alert_service.resolve(session, alert_id, principal.id, body.note))
