"""USSD menu. Pure rules + database: no LLM calls on this path (screens must answer in seconds).

Africa's Talking posts the *whole* input path so far in `text` ("1*2*2"), so the handler is a
pure function of (phone, text) and needs no server-side session store. Keep screens short
(~160 chars) and the menu shallow; sessions are time-limited by the operators.

All Kiswahili strings need native-speaker and clinical review before the pilot.
"""

import uuid

from fastapi import APIRouter, Depends, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import normalize_msisdn
from app.modules.checkins.service import submit_checkin
from app.modules.mothers.service import create_mother, get_mother_by_phone

router = APIRouter(tags=["ussd"])

QUESTIONS = [
    "severe_headache",
    "visual_disturbance",
    "swelling_face_hands",
    "vaginal_bleeding",
    "reduced_fetal_movement",
    "fever",
]
COUNTIES = {"1": "Garissa", "2": "Tana River", "3": "Siaya", "4": "Other"}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "menu": "Welcome back\n1. Symptom check\n2. Eating well tip",
        "yes_no": "1. Yes\n2. No",
        "invalid": "Invalid choice. Please dial again.",
        "tip": "Eat iron-rich foods like omena, sukuma wiki and beans. "
        "Take your iron/folic tablets as given at the clinic.",
        "reg_weeks": "How many weeks pregnant are you? (1-42)",
        "reg_age": "Your age?",
        "reg_county": "County:\n1. Garissa\n2. Tana River\n3. Siaya\n4. Other",
        "reg_consent": "May your health worker contact you?\n1. Yes\n2. No",
        "reg_done": "You are registered. Dial again for the menu.",
        "severe_headache": "Do you have a severe headache?",
        "visual_disturbance": "Blurred vision or seeing spots?",
        "swelling_face_hands": "Swelling of face or hands?",
        "vaginal_bleeding": "Any bleeding from the vagina?",
        "reduced_fetal_movement": "Is the baby moving less than usual?",
        "fever": "Do you have fever or chills?",
    },
    "sw": {
        "menu": "Karibu tena\n1. Kagua dalili\n2. Ushauri wa lishe",
        "yes_no": "1. Ndiyo\n2. Hapana",
        "invalid": "Chaguo si sahihi. Tafadhali piga tena.",
        "tip": "Kula vyakula vyenye chuma kama omena, sukuma wiki na maharagwe. "
        "Meza vidonge vya chuma/folic ulivyopewa kliniki.",
        "reg_weeks": "Una mimba ya wiki ngapi? (1-42)",
        "reg_age": "Umri wako?",
        "reg_county": "Kaunti:\n1. Garissa\n2. Tana River\n3. Siaya\n4. Nyingine",
        "reg_consent": "Mhudumu wa afya akupigie simu?\n1. Ndiyo\n2. Hapana",
        "reg_done": "Umesajiliwa. Piga tena kupata menyu.",
        "severe_headache": "Una maumivu makali ya kichwa?",
        "visual_disturbance": "Macho yanaona ukungu au madoa?",
        "swelling_face_hands": "Uso au mikono imevimba?",
        "vaginal_bleeding": "Unatokwa na damu ukeni?",
        "reduced_fetal_movement": "Mtoto anacheza kidogo kuliko kawaida?",
        "fever": "Una homa au kutetemeka?",
    },
}
LANG_PROMPT = "Welcome / Karibu\n1. English\n2. Kiswahili"


def _con(text: str) -> str:
    return f"CON {text}"


def _end(text: str) -> str:
    return f"END {text}"


def _bad(lang: str = "en") -> str:
    return _end(STRINGS[lang]["invalid"])


def _int_in(value: str, lo: int, hi: int) -> int | None:
    return int(value) if value.isdigit() and lo <= int(value) <= hi else None


async def handle_ussd(session: AsyncSession, *, session_id: str, phone: str, text: str) -> str:
    try:
        msisdn = normalize_msisdn(phone)
    except ValueError:
        return _bad()
    steps = text.split("*") if text else []
    mother = await get_mother_by_phone(session, msisdn)
    if mother is None:
        return await _register(session, msisdn, steps)

    lang = mother.language if mother.language in STRINGS else "en"
    t = STRINGS[lang]
    if not steps:
        return _con(t["menu"])
    if steps[0] == "2" and len(steps) == 1:
        return _end(t["tip"])
    if steps[0] != "1":
        return _bad(lang)

    answers = steps[1:]
    if any(a not in {"1", "2"} for a in answers) or len(answers) > len(QUESTIONS):
        return _bad(lang)
    if len(answers) < len(QUESTIONS):
        return _con(f"{t[QUESTIONS[len(answers)]]}\n{t['yes_no']}")

    symptoms = {q: a == "1" for q, a in zip(QUESTIONS, answers, strict=True)}
    # Deterministic id from the USSD session id: operator/aggregator retries can't double-submit.
    checkin_id = uuid.uuid5(uuid.NAMESPACE_URL, f"ussd:{session_id}")
    result = await submit_checkin(
        session, mother, checkin_id=checkin_id, symptoms=symptoms, channel="ussd"
    )
    return _end(result.advice)


async def _register(session: AsyncSession, msisdn: str, steps: list[str]) -> str:
    if not steps:
        return _con(LANG_PROMPT)
    lang = {"1": "en", "2": "sw"}.get(steps[0])
    if lang is None:
        return _bad()
    t = STRINGS[lang]
    if len(steps) == 1:
        return _con(t["reg_weeks"])
    weeks = _int_in(steps[1], 1, 42)
    if weeks is None:
        return _bad(lang)
    if len(steps) == 2:
        return _con(t["reg_age"])
    age = _int_in(steps[2], 10, 55)
    if age is None:
        return _bad(lang)
    if len(steps) == 3:
        return _con(t["reg_county"])
    county = COUNTIES.get(steps[3])
    if county is None:
        return _bad(lang)
    if len(steps) == 4:
        return _con(t["reg_consent"])
    if steps[4] not in {"1", "2"} or len(steps) > 5:
        return _bad(lang)

    # TODO(legal): minors' consent/assent. Pseudonymous by default on USSD: no name is collected.
    await create_mother(
        session,
        msisdn=msisdn,
        age=age,
        gestation_weeks=weeks,
        county=county,
        language=lang,
        consents={"chp_contact": steps[4] == "1"},
    )
    return _end(t["reg_done"])


@router.post("/ussd/callback", response_class=PlainTextResponse)
async def ussd_callback(
    sessionId: str = Form(...),  # noqa: N803  (field names are fixed by the aggregator)
    phoneNumber: str = Form(...),  # noqa: N803
    text: str = Form(""),
    session: AsyncSession = Depends(get_session),
):
    # TODO(security): restrict to the aggregator's IPs and/or a shared secret in the callback URL.
    return PlainTextResponse(
        await handle_ussd(session, session_id=sessionId, phone=phoneNumber, text=text)
    )
