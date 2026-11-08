import uuid
from dataclasses import dataclass
from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit
from app.core.errors import ConflictError
from app.core.time import utcnow
from app.modules.alerts.models import Alert
from app.modules.checkins.models import CheckIn
from app.modules.chp.service import pick_alert_recipient
from app.modules.mothers.models import Mother
from app.modules.triage.engine import ALERT_TIERS, Tier, evaluate, load_ruleset

log = structlog.get_logger()


@dataclass
class SubmitResult:
    checkin: CheckIn
    alert: Alert | None
    duplicate: bool
    language: str = "en"

    @property
    def advice(self) -> str:
        return load_ruleset().advice_for(Tier(self.checkin.risk_tier), self.language)


async def submit_checkin(
    session: AsyncSession,
    mother: Mother,
    *,
    checkin_id: uuid.UUID,
    symptoms: dict[str, bool],
    submitted_at: datetime | None = None,
    channel: str = "app",
) -> SubmitResult:
    existing = await session.get(CheckIn, checkin_id)
    if existing is not None:
        if existing.mother_id != mother.id:
            raise ConflictError("Check-in id already used")
        alert = await _alert_for(session, existing.id)
        return SubmitResult(existing, alert, duplicate=True, language=mother.language)

    triage = evaluate(symptoms, mother.current_gestation_weeks())
    checkin = CheckIn(
        id=checkin_id,
        mother_id=mother.id,
        symptoms=symptoms,
        risk_tier=triage.tier.value,
        triggered_rules=list(triage.triggered_rules),
        rule_version=triage.rule_version,
        channel=channel,
        submitted_at=submitted_at or utcnow(),
    )
    session.add(checkin)
    alert: Alert | None = None
    if triage.tier in ALERT_TIERS:
        recipient = await pick_alert_recipient(session, mother)
        alert = Alert(
            mother_id=mother.id, checkin_id=checkin_id, chp_id=recipient, tier=triage.tier.value
        )
        session.add(alert)
        if recipient is None:
            log.error("alert_unrouted", checkin_id=str(checkin_id), tier=triage.tier.value)
        elif recipient != mother.chp_id:
            log.warning("alert_routed_to_supervisor", checkin_id=str(checkin_id))
    audit(
        session,
        actor_id=mother.id,
        actor_role="mother",
        action="checkin_submitted",
        resource_type="checkin",
        resource_id=checkin_id,
        detail={"tier": triage.tier.value, "rules": list(triage.triggered_rules)},
    )
    try:
        await session.commit()
    except IntegrityError:
        # Concurrent retry won the race; return what it stored.
        await session.rollback()
        existing = await session.get(CheckIn, checkin_id)
        if existing is None:
            raise
        return SubmitResult(
            existing,
            await _alert_for(session, checkin_id),
            duplicate=True,
            language=mother.language,
        )
    return SubmitResult(checkin, alert, duplicate=False, language=mother.language)


async def _alert_for(session: AsyncSession, checkin_id: uuid.UUID) -> Alert | None:
    result = await session.execute(select(Alert).where(Alert.checkin_id == checkin_id))
    return result.scalar_one_or_none()
