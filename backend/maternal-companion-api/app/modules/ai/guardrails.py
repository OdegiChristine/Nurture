"""First-line output filter for LLM-generated text (nutrition tips, education).

This is deliberately blunt. It is ONE layer: pair it with retrieval-grounded prompts, citation
requirements, and clinician review of the generated-content test set.
"""

import re
from dataclasses import dataclass

_DIAGNOSIS = re.compile(
    r"\byou (have|likely have|probably have|are suffering from|suffer from)\b"
    r"|\b(this is|it is|it's) (definitely|probably|likely)?\s*(pre-?eclampsia|eclampsia|anaemia|"
    r"anemia|gestational diabetes|miscarriage|malaria)\b"
    r"|\bdiagnos(e|ed|is)\b",
    re.IGNORECASE,
)
_DOSAGE = re.compile(
    r"\b\d+(\.\d+)?\s*(mg|mcg|µg|g|ml|iu|tablets?|pills?|capsules?)\b"
    r"|\b(take|swallow)\s+(one|two|three|\d+)\s+(tablets?|pills?|capsules?)\b",
    re.IGNORECASE,
)

SAFE_FALLBACK = (
    "I can't answer that safely. Please speak to your community health worker or visit your clinic."
)


@dataclass(frozen=True)
class GuardrailResult:
    allowed: bool
    reason: str | None = None


def check_output(text: str) -> GuardrailResult:
    if _DIAGNOSIS.search(text):
        return GuardrailResult(False, "diagnostic_language")
    if _DOSAGE.search(text):
        return GuardrailResult(False, "dosage_language")
    return GuardrailResult(True)


def enforce(text: str) -> str:
    """Return the text if it passes, otherwise the safe fallback."""
    return text if check_output(text).allowed else SAFE_FALLBACK
