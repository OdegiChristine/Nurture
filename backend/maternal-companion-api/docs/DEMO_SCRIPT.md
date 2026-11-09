# Demo script

**Audience takeaway:** a teenage mother's danger sign reaches her health worker in seconds, on a
channel that needs no smartphone and no data bundle.

Status key: ✅ works today · 🔨 being built (Sat/Sun) · ⏳ stretch

## 0. Setup

```bash
export DATABASE_URL=sqlite+aiosqlite:///demo.db     # PowerShell: $env:DATABASE_URL="sqlite+aiosqlite:///demo.db"
python -m scripts.seed_demo --reset                 # fresh, identical data every run
uvicorn app.main:app                                # leave running
```

Accounts (password for all: `demo-pass-2026`): `grace@demo.org` (CHP, Siaya),
`hawa@demo.org` (CHP, Garissa), `supervisor@demo.org`.
Unregistered number for the live registration: **0700000001**.


## 1. The problem

- Maternal mortality in Kenya remains high; the "Three Delays".
- Teenage mothers avoid clinics because of stigma; care happens in episodes, and CHPs have no way
  to tell who needs them most today.
- Our answer: a **continuous, private channel** between mother and CHP.

## 2. Live: the mother's phone, 3 minutes

**Registration ✅** (a feature phone could do this). Use the phone simulator at **/simulator** ✅ (its Auto-play buttons type the inputs for you), or curl:

```bash
curl -s -X POST localhost:8000/ussd/callback -d "sessionId=demo1&phoneNumber=0700000001&text=1*28*17*3*1"
```

Inputs in order: `1` English → `28` weeks → `17` age → `3` Siaya → `1` allow CHP contact.
Say: *"No name collected. She chooses whether her health worker can see her number."*

**Danger-sign check ✅**: dial again, `1` Symptom check, then answer: headache **Yes**, blurred
vision **Yes**, swelling No, bleeding No, baby movement No, fever No.

```bash
curl -s -X POST localhost:8000/ussd/callback -d "sessionId=demo2&phoneNumber=0700000001&text=1*1*1*2*2*2*2"
```

Expected: **"This is an emergency. Go to the nearest hospital NOW…"**
Say: *"The rule that fired is on record. The system never diagnoses; it routes her to care."*

## 3. Live: the CHP's screen, 3 minutes (dashboard ✅ at /dashboard)

1. Log in as **Grace**. The new mother is at the **top, marked emergency**. Others sort below by risk.
2. Point out: Achieng's open **high** alert; **Auma** has not checked in for 9 days; **Anyango**
   never has. *"Her list is prioritised; she doesn't have to guess who to visit."*
3. **Acknowledge**, then **Resolve** with a note. Say: *"Every action is logged: who, what, when."*
4. Phone numbers: show that Adhiambo's is hidden (she did not consent).

**Safety net:** log in as the **supervisor**. Zawadi (Tana River, no CHP there yet) has an
emergency here. *"An alert is never dropped because a county has no health worker."*

## 4. Nutrition, 1 minute ✅

On USSD: `2`. Expected (28 weeks, Siaya): late-pregnancy tip with omena, kunde, sukuma wiki. It changes with trimester and county.
Say: *"Hyper-local, not generic advice. Next step: exact nutrient data from the Kenya Food
Composition Tables."*

## 5. Architecture and roadmap, 1 minute (slides)

Show the architecture diagram. Built: USSD, triage engine, alerts, CHP APIs, audit trail, WhatsApp
webhook. Next: SMS delivery to CHPs, reminders, WhatsApp conversations, offline Android app,
retrieval-grounded Q&A.

## To be done:

- Triage rules are **illustrative placeholders**; a clinician must validate them before any pilot.
- Kiswahili text needs **native and clinical review**.
- Nutrition tips are rule-based for now; nutrient figures will come from KFCT, not from an AI model.
- This is a **working prototype**, not a validated or pilot-ready system.

## Likely questions

| Question | Answer |
|---|---|
| Is this a diagnosis tool? | No. It gives a risk tier and says "go to care". Rules are transparent and clinician-owned. |
| Teenager privacy? | No name needed; phone stored encrypted; CHP sees a number only with consent; every access is logged. Minors' consent rules are going to legal review. |
| Why USSD? | Works on any phone, no data bundle. Each session costs the user a small telco charge, so sponsorship is a pilot question. |
| What if the AI is wrong? | Triage is rule-based and auditable. AI is only for content, and its output is filtered. A model may only *raise* risk, never lower it. |
| Who validates it? | Clinical advisor sign-off on rules is the gate before a pilot. |
| What about no CHP assigned? | Alert routes to a supervisor; if none, it appears on an oversight list. |

## If something breaks

1. Server won't start → `python -m scripts.seed_demo --reset` then restart `uvicorn`.
2. Dashboard blank → re-seed; check you are logged in as Grace.
3. Anything else → play the backup recording and continue with slides.
