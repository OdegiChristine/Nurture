import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.time import as_utc, utcnow


class Mother(Base):
    __tablename__ = "mothers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # Never query or log by plaintext phone. Lookup via keyed hash; value stored encrypted.
    phone_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    phone_enc: Mapped[bytes] = mapped_column(LargeBinary)
    pseudonym: Mapped[str | None] = mapped_column(String(80))  # pseudonymous onboarding allowed
    age: Mapped[int] = mapped_column(Integer)
    gestation_weeks_at_enrolment: Mapped[int] = mapped_column(Integer)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    county: Mapped[str] = mapped_column(String(80), index=True)
    language: Mapped[str] = mapped_column(String(5), default="en")
    dietary_preferences: Mapped[list] = mapped_column(JSON, default=list)
    conditions: Mapped[list] = mapped_column(JSON, default=list)
    chp_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chps.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    def display_label(self) -> str:
        """Safe name for dashboards: the pseudonym, or an anonymous tag (no phone digits)."""
        return self.pseudonym or f"Anonymous #{str(self.id)[:4].upper()}"

    def current_gestation_weeks(self) -> int:
        elapsed_weeks = (utcnow() - as_utc(self.enrolled_at)).days // 7
        return self.gestation_weeks_at_enrolment + max(elapsed_weeks, 0)


class Consent(Base):
    """Current consent state per (mother, scope). History lives in the audit log."""

    __tablename__ = "consents"
    __table_args__ = (UniqueConstraint("mother_id", "scope"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    mother_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mothers.id"), index=True)
    scope: Mapped[str] = mapped_column(String(40))
    granted: Mapped[bool] = mapped_column(Boolean)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


CONSENT_SCOPES = ("chp_contact", "aggregate_analytics")
