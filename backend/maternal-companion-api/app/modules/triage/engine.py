"""Deterministic, auditable triage. Rules are data (YAML); this file only evaluates them.

A learned classifier may later *raise* a tier via `combine_tiers`, never lower one set by rules.
The system never diagnoses: output is a risk tier plus a recommendation to seek care.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, model_validator

RULES_PATH = Path(__file__).parent / "rules" / "ruleset.yaml"


class Tier(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EMERGENCY = "emergency"

    @property
    def rank(self) -> int:
        return _RANK[self]


_RANK = {Tier.LOW: 0, Tier.MODERATE: 1, Tier.HIGH: 2, Tier.EMERGENCY: 3}
ALERT_TIERS = frozenset({Tier.HIGH, Tier.EMERGENCY})


class Rule(BaseModel):
    id: str
    tier: Tier
    all_of: list[str] = []
    any_of: list[str] = []
    min_weeks: int | None = None
    max_weeks: int | None = None

    @model_validator(mode="after")
    def _needs_condition(self) -> "Rule":
        if not (self.all_of or self.any_of):
            raise ValueError(f"Rule {self.id} needs all_of or any_of")
        return self


class RuleSet(BaseModel):
    version: str
    symptoms: list[str]
    advice: dict[Tier, dict[str, str]]
    rules: list[Rule]

    @model_validator(mode="after")
    def _consistent(self) -> "RuleSet":
        known = set(self.symptoms)
        for rule in self.rules:
            unknown = (set(rule.all_of) | set(rule.any_of)) - known
            if unknown:
                raise ValueError(f"Rule {rule.id} references unknown symptoms: {sorted(unknown)}")
        if len({r.id for r in self.rules}) != len(self.rules):
            raise ValueError("Duplicate rule ids")
        missing = set(Tier) - set(self.advice)
        if missing:
            raise ValueError(f"Missing advice for tiers: {sorted(missing)}")
        return self

    def advice_for(self, tier: Tier, language: str) -> str:
        texts = self.advice[tier]
        return texts.get(language) or texts["en"]


@dataclass(frozen=True)
class TriageResult:
    tier: Tier
    triggered_rules: tuple[str, ...]
    rule_version: str


@lru_cache
def load_ruleset(path: Path = RULES_PATH) -> RuleSet:
    return RuleSet.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def _applies(rule: Rule, positives: set[str], weeks: int | None) -> bool:
    if weeks is not None:
        if rule.min_weeks is not None and weeks < rule.min_weeks:
            return False
        if rule.max_weeks is not None and weeks > rule.max_weeks:
            return False
    if rule.all_of and not set(rule.all_of) <= positives:
        return False
    if rule.any_of and not (set(rule.any_of) & positives):
        return False
    return True


def evaluate(
    answers: Mapping[str, bool], gestation_weeks: int | None, ruleset: RuleSet | None = None
) -> TriageResult:
    ruleset = ruleset or load_ruleset()
    positives = {name for name, present in answers.items() if present}
    matched = [r for r in ruleset.rules if _applies(r, positives, gestation_weeks)]
    tier = max((r.tier for r in matched), key=lambda t: t.rank, default=Tier.LOW)
    return TriageResult(
        tier=tier,
        triggered_rules=tuple(r.id for r in matched),
        rule_version=ruleset.version,
    )


def combine_tiers(rule_tier: Tier, model_tier: Tier | None) -> Tier:
    """A model may escalate, never de-escalate."""
    if model_tier is None:
        return rule_tier
    return max(rule_tier, model_tier, key=lambda t: t.rank)
