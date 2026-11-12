"""Demo-only HTTP entry to the chat engine. Registered ONLY when ENVIRONMENT=local, because it
lets the caller speak as any phone number (the real webhook authenticates via Meta's signature)."""

import uuid
from dataclasses import asdict

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.errors import AppError
from app.core.security import normalize_msisdn
from app.modules.chat.engine import handle_message

router = APIRouter(prefix="/chat", tags=["chat-simulator"])


class SimIn(BaseModel):
    phone: str
    text: str
    message_id: str | None = None
    reset: bool = False


@router.post("/simulate")
async def simulate(body: SimIn, session: AsyncSession = Depends(get_session)):
    try:
        msisdn = normalize_msisdn(body.phone)
    except ValueError as exc:
        raise AppError(str(exc)) from exc
    replies = await handle_message(
        session,
        msisdn=msisdn,
        text=body.text,
        message_id=body.message_id or str(uuid.uuid4()),
        reset=body.reset,
    )
    return {"messages": [asdict(r) for r in replies]}
