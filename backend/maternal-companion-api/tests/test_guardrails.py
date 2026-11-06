import pytest

from app.modules.ai.guardrails import SAFE_FALLBACK, check_output, enforce


@pytest.mark.parametrize(
    "text",
    [
        "You have pre-eclampsia.",
        "This is probably anaemia, so rest.",
        "Take 2 tablets every morning.",
        "Take 400 mcg of folic acid daily.",
        "I can diagnose this for you.",
    ],
)
def test_blocks_diagnosis_and_dosage(text):
    assert not check_output(text).allowed
    assert enforce(text) == SAFE_FALLBACK


@pytest.mark.parametrize(
    "text",
    [
        "Omena, sukuma wiki and beans are good sources of iron.",
        "Please visit your clinic if you feel unwell.",
        "Take your iron and folic acid tablets as given at the clinic.",
    ],
)
def test_allows_safe_guidance(text):
    assert check_output(text).allowed
    assert enforce(text) == text
