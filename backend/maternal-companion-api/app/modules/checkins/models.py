import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.time import utcnow


class CheckIn(Base):
    __tablename__ = "checkins"

    # Client-generated UUID doubles as the idempotency key for offline sync / webhook retries.
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    mother_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mothers.id"), index=True)
    symptoms: Mapped[dict] = mapped_column(JSON)
    risk_tier: Mapped[str] = mapped_column(String(20), index=True)
    triggered_rules: Mapped[list] = mapped_column(JSON, default=list)
    rule_version: Mapped[str] = mapped_column(String(40))
    channel: Mapped[str] = mapped_column(String(20), default="app")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
