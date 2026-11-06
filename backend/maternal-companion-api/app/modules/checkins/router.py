from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import Principal, mother_only
from app.core.errors import NotFoundError
from app.modules.alerts.notify import notify_chp_of_alert
from app.modules.checkins import service
from app.modules.checkins.schemas import CheckInCreate, CheckInOut
from app.modules.mothers.models import Mother

router = APIRouter(prefix="/v1/checkins", tags=["checkins"])


@router.post("", response_model=CheckInOut)
async def submit(
    body: CheckInCreate,
    background: BackgroundTasks,
    principal: Principal = mother_only,
    session: AsyncSession = Depends(get_session),
):
    mother = await session.get(Mother, principal.id)
    if mother is None:
        raise NotFoundError("Mother not found")
    result = await service.submit_checkin(
        session,
        mother,
        checkin_id=body.id,
        symptoms=body.symptoms,
        submitted_at=body.submitted_at,
    )
    if result.alert is not None and not result.duplicate:
        background.add_task(notify_chp_of_alert, result.alert.id)
    return CheckInOut(
        id=result.checkin.id,
        risk_tier=result.checkin.risk_tier,
        advice=result.advice,
        triggered_rules=result.checkin.triggered_rules,
        alert_created=result.alert is not None,
        duplicate=result.duplicate,
    )
