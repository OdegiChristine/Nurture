"""Channel-agnostic chat engine (drives the WhatsApp-style simulator; the webhook can call it too).

A small state machine: registration (language, weeks, age, county, nickname, condition, consent),
then a menu with the danger-sign check and nutrition tip. Replies carry quick-reply buttons
(WhatsApp allows at most 3 reply buttons, 10 list rows; check Meta's current limits).

LIMITATION: state is held in memory (lost on restart, not shared across workers). Move it to
the database/Redis before real use. All Kiswahili needs native + clinical review.
"""

import uuid
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.alerts.notify import notify_chp_of_alert
from app.modules.channels.ussd import QUESTIONS, STRINGS
from app.modules.checkins.service import submit_checkin
from app.modules.mothers.service import create_mother, get_mother_by_phone
from app.modules.nutrition.service import nutrition_tip

COUNTIES = ["Garissa", "Tana River", "Siaya", "Other"]
CONDITIONS = [[], ["anaemia"], ["diabetes"]]
WELCOME = "Welcome to Maternal Companion / Karibu. Choose your language:"

M = {
    "en": {
        "weeks": "How many weeks pregnant are you? (1-42)",
        "age": "How old are you?",
        "county": "Which county do you live in?",
        "nick": "What should we call you? Type a nickname or tap Skip. No real name needed.",
        "skip": "Skip",
        "cond": "Do you have a health condition we should know about?",
        "conds": ["None", "Anaemia", "Diabetes"],
        "consent": "May your health worker contact you if a check shows a danger sign?",
        "yn": ["Yes", "No"],
        "done": "You are registered. What would you like to do?",
        "menu": "What would you like to do?",
        "menu_btn": ["Symptom check", "Nutrition tip"],
        "bad_num": "Please send a number.",
        "bad_choice": "Please choose one of the options.",
        "intro": "Let's check for danger signs. Answer Yes or No.",
    },
    "sw": {
        "weeks": "Una mimba ya wiki ngapi? (1-42)",
        "age": "Una umri gani?",
        "county": "Unaishi kaunti gani?",
        "nick": "Tukuite nani? Andika jina la utani, au gusa Ruka. Hatuhitaji jina lako halisi.",
        "skip": "Ruka",
        "cond": "Una hali yoyote ya kiafya tunayopaswa kujua?",
        "conds": ["Hakuna", "Upungufu wa damu", "Kisukari"],
        "consent": "Mhudumu wa afya akupigie simu ukigundulika dalili hatari?",
        "yn": ["Ndiyo", "Hapana"],
        "done": "Umesajiliwa. Ungependa kufanya nini?",
        "menu": "Ungependa kufanya nini?",
        "menu_btn": ["Kagua dalili", "Ushauri wa lishe"],
        "bad_num": "Tafadhali tuma namba.",
        "bad_choice": "Tafadhali chagua mojawapo ya chaguo.",
        "intro": "Tukague dalili hatari. Jibu Ndiyo au Hapana.",
    },
}


@dataclass
class Reply:
    text: str
    buttons: list[str] = field(default_factory=list)


STORE: dict[str, dict] = {}


def _pick(text: str, options: list[str]) -> int | None:
    t = text.strip().lower()
    if t.isdigit() and 1 <= int(t) <= len(options):
        return int(t) - 1
    return next((i for i, o in enumerate(options) if o.lower() == t), None)


def _num(text: str, lo: int, hi: int) -> int | None:
    t = text.strip()
    return int(t) if t.isdigit() and lo <= int(t) <= hi else None


async def handle_message(
    session: AsyncSession, *, msisdn: str, text: str, message_id: str, reset: bool = False
) -> list[Reply]:
    if reset:
        STORE.pop(msisdn, None)
    st = STORE.setdefault(msisdn, {})
    mother = await get_mother_by_phone(session, msisdn)
    if mother is None:
        return await _register(session, msisdn, st, text)
    lang = mother.language if mother.language in M else "en"
    t = M[lang]
    if text.strip().lower() in {"menu", "cancel", "stop"}:
        st.clear()
    if st.get("step") == "check":
        return await _check(session, mother, st, text, message_id, lang)
    choice = _pick(text, t["menu_btn"])
    if choice == 1:
        weeks = mother.current_gestation_weeks()
        return [Reply(nutrition_tip(weeks, mother.county, lang), t["menu_btn"])]
    if choice == 0:
        st.update(step="check", i=0, ans={})
        return [Reply(t["intro"]), Reply(STRINGS[lang][QUESTIONS[0]], t["yn"])]
    return [Reply(t["menu"], t["menu_btn"])]


async def _check(session, mother, st, text, message_id, lang) -> list[Reply]:
    t = M[lang]
    pick = _pick(text, t["yn"])
    if pick is None:
        return [Reply(t["bad_choice"]), Reply(STRINGS[lang][QUESTIONS[st["i"]]], t["yn"])]
    st["ans"][QUESTIONS[st["i"]]] = pick == 0
    st["i"] += 1
    if st["i"] < len(QUESTIONS):
        return [Reply(STRINGS[lang][QUESTIONS[st["i"]]], t["yn"])]
    answers = st["ans"]
    st.clear()
    result = await submit_checkin(
        session,
        mother,
        checkin_id=uuid.uuid5(uuid.NAMESPACE_URL, f"chat:{message_id}"),
        symptoms=answers,
        channel="whatsapp",
    )
    if result.alert is not None and not result.duplicate:
        await notify_chp_of_alert(result.alert.id)
    return [Reply(result.advice, t["menu_btn"])]


async def _register(session, msisdn: str, st: dict, text: str) -> list[Reply]:
    lang = st.get("lang", "en")
    t = M[lang]
    step = st.get("step")
    if step is None:
        st["step"] = "lang"
        return [Reply(WELCOME, ["English", "Kiswahili"])]
    if step == "lang":
        pick = _pick(text, ["English", "Kiswahili"])
        if pick is None:
            return [Reply(WELCOME, ["English", "Kiswahili"])]
        lang = "en" if pick == 0 else "sw"
        st.update(lang=lang, step="weeks")
        return [Reply(M[lang]["weeks"])]
    if step in {"weeks", "age"}:
        n = _num(text, 1, 42) if step == "weeks" else _num(text, 10, 55)
        if n is None:
            return [Reply(f"{t['bad_num']} {t[step]}")]
        st[step] = n
        st["step"] = "age" if step == "weeks" else "county"
        return [Reply(t["age"])] if step == "weeks" else [Reply(t["county"], COUNTIES)]
    if step == "county":
        pick = _pick(text, COUNTIES)
        if pick is None:
            return [Reply(t["bad_choice"]), Reply(t["county"], COUNTIES)]
        st.update(county=COUNTIES[pick], step="nick")
        return [Reply(t["nick"], [t["skip"]])]
    if step == "nick":
        skipped = text.strip().lower() in {t["skip"].lower(), "skip", "-", ""}
        st.update(nick=None if skipped else text.strip()[:40], step="cond")
        return [Reply(t["cond"], t["conds"])]
    if step == "cond":
        pick = _pick(text, t["conds"])
        if pick is None:
            return [Reply(t["bad_choice"]), Reply(t["cond"], t["conds"])]
        st.update(conditions=CONDITIONS[pick], step="consent")
        return [Reply(t["consent"], t["yn"])]
    pick = _pick(text, t["yn"])  # step == "consent"
    if pick is None:
        return [Reply(t["bad_choice"]), Reply(t["consent"], t["yn"])]
    await create_mother(
        session,
        msisdn=msisdn,
        age=st["age"],
        gestation_weeks=st["weeks"],
        county=st["county"],
        language=lang,
        pseudonym=st["nick"],
        conditions=st["conditions"],
        consents={"chp_contact": pick == 0},
    )
    st.clear()
    return [Reply(t["done"], t["menu_btn"])]
