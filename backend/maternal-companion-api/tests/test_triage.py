"""Clinical case suite. A rule change that breaks one of these must be reviewed by the clinician.

NOTE: the cases mirror the ILLUSTRATIVE placeholder rules; replace with clinician-approved cases.
"""

import pytest

from app.modules.triage.engine import Tier, combine_tiers, evaluate, load_ruleset


@pytest.mark.parametrize(
    ("symptoms", "weeks", "expected"),
    [
        ({}, 28, Tier.LOW),
        ({"fever": True}, 28, Tier.MODERATE),
        ({"severe_headache": True}, 28, Tier.MODERATE),
        ({"severe_headache": True, "swelling_face_hands": True}, 28, Tier.HIGH),
        ({"severe_headache": True, "visual_disturbance": True}, 28, Tier.EMERGENCY),
        ({"vaginal_bleeding": True}, 12, Tier.EMERGENCY),
        ({"convulsions": True}, 30, Tier.EMERGENCY),
        ({"reduced_fetal_movement": True}, 30, Tier.HIGH),
        ({"reduced_fetal_movement": True}, 12, Tier.LOW),  # too early to feel movement
        ({"reduced_fetal_movement": True}, None, Tier.HIGH),  # unknown weeks => over-escalate
        ({"fever": False, "severe_headache": False}, 28, Tier.LOW),
    ],
)
def test_clinical_cases(symptoms, weeks, expected):
    assert evaluate(symptoms, weeks).tier == expected


def test_highest_tier_wins_and_rules_are_reported():
    result = evaluate({"severe_headache": True, "visual_disturbance": True, "fever": True}, 30)
    assert result.tier == Tier.EMERGENCY
    assert "EMERG_HEADACHE_VISUAL" in result.triggered_rules
    assert result.rule_version


def test_model_can_escalate_but_never_deescalate():
    assert combine_tiers(Tier.MODERATE, Tier.HIGH) == Tier.HIGH
    assert combine_tiers(Tier.EMERGENCY, Tier.LOW) == Tier.EMERGENCY
    assert combine_tiers(Tier.HIGH, None) == Tier.HIGH


def test_advice_exists_for_every_tier_and_language_and_fits_a_ussd_screen():
    rs = load_ruleset()
    for tier in Tier:
        for lang in ("en", "sw"):
            text = rs.advice_for(tier, lang)
            assert text
            assert len(text) <= 150, f"{tier}/{lang} too long for USSD: {len(text)}"
