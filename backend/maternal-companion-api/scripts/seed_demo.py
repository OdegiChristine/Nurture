"""Seed a believable demo dataset (LOCAL/dev only).

    python -m scripts.seed_demo --reset

All people are fictional. Check-in history is back-dated so the dashboard looks lived-in:
risk tiers are computed by the real triage engine, and alerts follow the real routing rules,
including the "no CHP in this county" fallback to a supervisor.
"""

import argparse
import asyncio
import sys
import uuid
from datetime import timedelta

from sqlalchemy import func, select

import app.models  # noqa: F401
from app.core.config import get_settings
from app.core.db import Base, SessionLocal, engine
from app.core.security import normalize_msisdn
from app.core.time import utcnow
from app.modules.alerts.models import Alert
from app.modules.checkins.models import CheckIn
from app.modules.chp.models import Chp
from app.modules.chp.service import create_chp, pick_alert_recipient
from app.modules.mothers.service import create_mother
from app.modules.triage.engine import ALERT_TIERS, evaluate

PASSWORD = "demo-pass-2026"  # noqa: S105  (fictional demo accounts, local only)

STAFF = [
    ("Grace Achieng", "grace@demo.org", "Siaya", "chp"),
    ("Hawa Mohamed", "hawa@demo.org", "Garissa", "chp"),
    ("Peter Odhiambo", "supervisor@demo.org", "Siaya", "supervisor"),
]

# (pseudonym, phone, county, age, weeks, consent_chp_contact, history)
# history: list of (hours_ago, symptoms, alert_state) ; alert_state in None/"open"/"resolved"
MOTHERS = [
    (
        "Achieng",
        "0711000001",
        "Siaya",
        16,
        30,
        True,
        [(50, {}, None), (3, {"severe_headache": True, "swelling_face_hands": True}, "open")],
    ),
    (
        "Akinyi",
        "0711000002",
        "Siaya",
        17,
        34,
        True,
        [(30, {"vaginal_bleeding": True}, "resolved"), (4, {}, None)],
    ),
    ("Atieno", "0711000003", "Siaya", 18, 22, True, [(26, {}, None)]),
    ("Adhiambo", "0711000004", "Siaya", 15, 12, False, [(50, {}, None)]),
    ("Awuor", "0711000005", "Siaya", 19, 38, True, [(20, {"fever": True}, None)]),
    ("Anyango", "0711000006", "Siaya", 16, 28, False, []),  # enrolled, never checked in
    ("Auma", "0711000007", "Siaya", 17, 26, True, [(9 * 24, {}, None)]),  # gone quiet 9 days
    ("Halima", "0722000001", "Garissa", 17, 20, True, [(24, {}, None)]),
    (
        "Fatuma",
        "0722000002",
        "Garissa",
        18,
        32,
        True,
        [(5, {"reduced_fetal_movement": True}, "open")],
    ),
    ("Amina", "0722000003", "Garissa", 16, 14, False, [(70, {"fever": True}, None)]),
    # No CHP in Tana River: the emergency must route to the supervisor, not vanish.
    (
        "Zawadi",
        "0733000001",
        "Tana River",
        17,
        24,
        True,
        [(2, {"severe_headache": True, "visual_disturbance": True}, "open")],
    ),
]


async def main(reset: bool) -> None:
    if get_settings().environment != "local":
        sys.exit("Refusing to seed outside ENVIRONMENT=local")

    async with engine.begin() as conn:
        if reset:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as s:
        if (await s.execute(select(func.count()).select_from(Chp))).scalar_one():
            sys.exit("Database already has data. Re-run with --reset to wipe and reseed.")

        chp_ids: dict[str, uuid.UUID] = {}
        for name, email, county, role in STAFF:
            chp = await create_chp(
                s, name=name, email=email, password=PASSWORD, county=county, role=role
            )
            chp_ids[email] = chp.id

        now = utcnow()
        for pseudonym, phone, county, age, weeks, consent, history in MOTHERS:
            mother = await create_mother(
                s,
                msisdn=normalize_msisdn(phone),
                age=age,
                gestation_weeks=weeks,
                county=county,
                pseudonym=pseudonym,
                consents={"chp_contact": consent},
            )
            for hours_ago, symptoms, alert_state in history:
                when = now - timedelta(hours=hours_ago)
                triage = evaluate(symptoms, weeks)
                checkin = CheckIn(
                    id=uuid.uuid4(),
                    mother_id=mother.id,
                    symptoms=symptoms,
                    risk_tier=triage.tier.value,
                    triggered_rules=list(triage.triggered_rules),
                    rule_version=triage.rule_version,
                    channel="ussd",
                    submitted_at=when,
                    received_at=when,
                )
                s.add(checkin)
                await s.flush()
                if triage.tier in ALERT_TIERS:
                    resolved = alert_state == "resolved"
                    s.add(
                        Alert(
                            mother_id=mother.id,
                            checkin_id=checkin.id,
                            chp_id=await pick_alert_recipient(s, mother),
                            tier=triage.tier.value,
                            status="resolved" if resolved else "open",
                            resolution_note=(
                                "Referred to Siaya County Referral Hospital; mother admitted "
                                "and stable."
                                if resolved
                                else None
                            ),
                            created_at=when,
                            acknowledged_at=when + timedelta(minutes=12) if resolved else None,
                            resolved_at=when + timedelta(hours=2) if resolved else None,
                        )
                    )
            await s.commit()

    print("\nDemo data ready. All logins use password:", PASSWORD)
    for name, email, county, role in STAFF:
        print(f"  {role:<11} {email:<22} {name} ({county})")
    print("\nRegistered demo mothers (USSD phone numbers):")
    for pseudonym, phone, county, _age, weeks, *_ in MOTHERS:
        print(f"  {phone}  {pseudonym:<9} {county:<11} {weeks}w")
    print("\nFor the LIVE registration demo, dial from an unregistered number, e.g. 0700 000 001")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="drop all tables first")
    asyncio.run(main(parser.parse_args().reset))
