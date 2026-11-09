"""Rule-based nutrition tips (v1): trimester focus + foods typical of the mother's county.

Deliberately NO nutrient numbers: those must come from the Kenya Food Composition Tables once
loaded. All wording (including Kiswahili) is illustrative and needs dietitian + native review.
Tips are short enough for a USSD screen and are checked against the output guardrails in tests.
"""

_LEAD = {
    "en": {
        1: "Early weeks: eat greens and beans for folate.",
        2: "Baby is growing fast: add iron and protein to meals.",
        3: "Late pregnancy: iron, protein and calcium help you and baby.",
    },
    "sw": {
        1: "Mwanzo wa ujauzito: kula mboga za majani na maharagwe.",
        2: "Mtoto anakua haraka: ongeza vyakula vyenye chuma na protini.",
        3: "Ujauzito wa mwisho: chuma, protini na kalsiamu zinasaidia.",
    },
}
_TRY = {"en": "Try:", "sw": "Jaribu:"}
_FOODS = {
    "en": {
        "siaya": "omena, kunde, sukuma wiki, beans, millet porridge",
        "garissa": "goat meat, cowpeas, boiled camel milk, dates, greens",
        "tana river": "fish, cowpeas, greens, mangoes, banana",
        "default": "beans, greens, eggs, fish if available, fruit",
    },
    "sw": {
        "siaya": "omena, kunde, sukuma wiki, maharagwe, uji wa ulezi",
        "garissa": "mbuzi, kunde, maziwa ya ngamia (yachemshwe), tende",
        "tana river": "samaki, kunde, mboga za majani, maembe, ndizi",
        "default": "maharagwe, mboga za majani, mayai, samaki, matunda",
    },
}


def trimester(weeks: int) -> int:
    return 1 if weeks <= 13 else 2 if weeks <= 27 else 3


def nutrition_tip(weeks: int, county: str, language: str = "en") -> str:
    lang = language if language in _LEAD else "en"
    foods = _FOODS[lang].get(county.strip().lower(), _FOODS[lang]["default"])
    return f"{_LEAD[lang][trimester(weeks)]} {_TRY[lang]} {foods}."
