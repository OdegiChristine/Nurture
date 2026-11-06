import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.time import utcnow

STATUSES = ("open", "acknowledged", "resolved")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    mother_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mothers.id"), index=True)
    # unique => at most one alert per check-in, even under retries
    checkin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("checkins.id"), unique=True)
    chp_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chps.id"), index=True)
    tier: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    resolution_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
