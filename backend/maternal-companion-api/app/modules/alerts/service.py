import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit
from app.core.errors import ConflictError, NotFoundError
from app.core.time import utcnow
from app.modules.alerts.models import Alert


async def list_open_for_chp(session: AsyncSession, chp_id: uuid.UUID) -> list[Alert]:
    result = await session.execute(
        select(Alert).where(Alert.chp_id == chp_id, Alert.status != "resolved")
    )
    alerts = list(result.scalars())
    # emergency first, then oldest first
    rank = {"emergency": 0, "high": 1}
    alerts.sort(key=lambda a: (rank.get(a.tier, 9), a.created_at))
    return alerts


async def _get_owned(session: AsyncSession, alert_id: uuid.UUID, chp_id: uuid.UUID) -> Alert:
    alert = await session.get(Alert, alert_id)
    # 404 (not 403) for other CHPs' alerts: don't reveal that the id exists.
    if alert is None or alert.chp_id != chp_id:
        raise NotFoundError("Alert not found")
    return alert


async def acknowledge(session: AsyncSession, alert_id: uuid.UUID, chp_id: uuid.UUID) -> Alert:
    alert = await _get_owned(session, alert_id, chp_id)
    if alert.status == "resolved":
        raise ConflictError("Alert already resolved")
    if alert.status == "open":
        alert.status = "acknowledged"
        alert.acknowledged_at = utcnow()
        audit(
            session,
            actor_id=chp_id,
            actor_role="chp",
            action="alert_acknowledged",
            resource_type="alert",
            resource_id=alert.id,
        )
        await session.commit()
    return alert


async def resolve(
    session: AsyncSession, alert_id: uuid.UUID, chp_id: uuid.UUID, note: str
) -> Alert:
    alert = await _get_owned(session, alert_id, chp_id)
    if alert.status == "resolved":
        raise ConflictError("Alert already resolved")
    now: datetime = utcnow()
    alert.status = "resolved"
    alert.resolved_at = now
    alert.acknowledged_at = alert.acknowledged_at or now
    alert.resolution_note = note
    audit(
        session,
        actor_id=chp_id,
        actor_role="chp",
        action="alert_resolved",
        resource_type="alert",
        resource_id=alert.id,
    )
    await session.commit()
    return alert
