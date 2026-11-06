import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.modules.triage.engine import load_ruleset


class CheckInCreate(BaseModel):
    id: uuid.UUID  # generated on the device; resubmitting the same id is safe
    symptoms: dict[str, bool]
    submitted_at: datetime | None = None

    @field_validator("symptoms")
    @classmethod
    def _known_symptoms(cls, value: dict[str, bool]) -> dict[str, bool]:
        unknown = set(value) - set(load_ruleset().symptoms)
        if unknown:
            raise ValueError(f"Unknown symptoms: {sorted(unknown)}")
        return value


class CheckInOut(BaseModel):
    id: uuid.UUID
    risk_tier: str
    advice: str
    triggered_rules: list[str]
    alert_created: bool
    duplicate: bool
