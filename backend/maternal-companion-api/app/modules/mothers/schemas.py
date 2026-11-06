import uuid
from typing import Literal

from pydantic import BaseModel, Field


class MotherCreate(BaseModel):
    phone: str
    # TODO(legal): confirm consent/assent rules for under-18 users before the pilot.
    age: int = Field(ge=10, le=55)
    gestation_weeks: int = Field(ge=1, le=42)
    county: str = Field(min_length=2, max_length=80)
    language: Literal["en", "sw"] = "en"
    pseudonym: str | None = Field(default=None, max_length=80)
    dietary_preferences: list[str] = []
    conditions: list[str] = []
    consent_chp_contact: bool = False


class MotherOut(BaseModel):
    id: uuid.UUID
    pseudonym: str | None
    age: int
    gestation_weeks: int
    county: str
    language: str
    has_chp: bool


class OnboardedOut(BaseModel):
    mother: MotherOut
    access_token: str


class ConsentUpdate(BaseModel):
    scope: Literal["chp_contact", "aggregate_analytics"]
    granted: bool
