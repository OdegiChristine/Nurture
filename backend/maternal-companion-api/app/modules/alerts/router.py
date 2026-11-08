# Oversight endpoints: list unrouted alerts and assign one to a CHP (supervisor/admin only)
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import Principal, oversight_only
from app.modules.alerts import service

router = APIRouter(prefix="/v1/admin/alerts", tags=["oversight"])


class UnroutedAlert(BaseModel):
    id: uuid.UUID
    mother_id: uuid.UUID
    tier: str
    status: str
    created_at: datetime


class AssignIn(BaseModel):
    chp_id: uuid.UUID


@router.get("/unrouted", response_model=list[UnroutedAlert])
async def unrouted(_: Principal = oversight_only, session: AsyncSession = Depends(get_session)):
    alerts = await service.list_unrouted(session)
    return [
        UnroutedAlert(
            id=a.id, mother_id=a.mother_id, tier=a.tier, status=a.status, created_at=a.created_at
        )
        for a in alerts
    ]


@router.post("/{alert_id}/assign", response_model=UnroutedAlert)
async def assign(
    alert_id: uuid.UUID,
    body: AssignIn,
    principal: Principal = oversight_only,
    session: AsyncSession = Depends(get_session),
):
    a = await service.assign(
        session, alert_id, body.chp_id, actor_id=principal.id, actor_role=principal.role.value
    )
    return UnroutedAlert(
        id=a.id, mother_id=a.mother_id, tier=a.tier, status=a.status, created_at=a.created_at
    )
