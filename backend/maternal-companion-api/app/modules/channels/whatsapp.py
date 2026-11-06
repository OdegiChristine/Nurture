"""WhatsApp Cloud API webhook: verification handshake, signature check, dedupe, hand-off.

Return 200 fast and do the real work in the background -- Meta retries slow or failed webhooks.
Never log message bodies or phone numbers.
"""

import hashlib
import hmac
import json
from typing import Any

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.errors import AppError, ForbiddenError
from app.modules.channels.models import InboundMessage

log = structlog.get_logger()
router = APIRouter(prefix="/webhooks/whatsapp", tags=["whatsapp"])


def verify_signature(raw_body: bytes, header: str | None, app_secret: str) -> bool:
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def extract_messages(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Flatten Meta's entry[].changes[].value.messages[] into [{id, from, type, text}]."""
    out: list[dict[str, str]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                out.append(
                    {
                        "id": msg.get("id", ""),
                        "from": msg.get("from", ""),
                        "type": msg.get("type", ""),
                        "text": msg.get("text", {}).get("body", ""),
                    }
                )
    return out


@router.get("", response_class=PlainTextResponse)
async def verify_webhook(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
):
    expected = get_settings().whatsapp_verify_token.get_secret_value()
    if mode != "subscribe" or not hmac.compare_digest(token, expected):
        raise ForbiddenError("Verification failed")
    return PlainTextResponse(challenge)


async def handle_inbound(message_id: str, msg_type: str) -> None:
    """Hand-off point to the conversation orchestrator (onboarding / check-in / nutrition Q&A).

    Remember: WhatsApp-initiated replies inside the 24h window are free-form; reminders outside it
    need approved templates. LLM answers must pass app.modules.ai.guardrails.enforce.
    """
    log.info("whatsapp_inbound", message_id=message_id, type=msg_type)


@router.post("")
async def receive(
    request: Request,
    background: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    raw = await request.body()
    secret = get_settings().whatsapp_app_secret.get_secret_value()
    if not verify_signature(raw, request.headers.get("x-hub-signature-256"), secret):
        raise ForbiddenError("Bad signature")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AppError("Invalid JSON") from exc

    for msg in extract_messages(payload):
        if not msg["id"]:
            continue
        session.add(InboundMessage(provider="whatsapp", provider_message_id=msg["id"]))
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()  # already seen: Meta retried
            continue
        background.add_task(handle_inbound, msg["id"], msg["type"])
    return {"status": "ok"}
