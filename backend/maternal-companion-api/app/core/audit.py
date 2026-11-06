"""Append-only record of who touched identifiable data. Never log PII or message bodies here."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.time import utcnow


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, index=True)
    actor_role: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(60))
    resource_type: Mapped[str] = mapped_column(String(40))
    resource_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, index=True)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)


def audit(
    session: AsyncSession,
    *,
    actor_id: uuid.UUID | None,
    actor_role: str,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | None = None,
    detail: dict | None = None,
) -> None:
    """Adds to the session; commits together with the caller's transaction."""
    session.add(
        AuditLog(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail or {},
        )
    )
