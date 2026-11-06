import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.time import utcnow


class InboundMessage(Base):
    """Dedupe table: Meta retries webhooks, so we record each provider message id once.

    Deliberately stores no message content or phone number.
    """

    __tablename__ = "inbound_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(20))
    provider_message_id: Mapped[str] = mapped_column(String(200), unique=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
