# Maternal Companion API

FastAPI backend for the AI Continuity of Maternal Health Companion: USSD + WhatsApp + app
channels, deterministic danger-sign triage, CHP alerting, consent-aware data access.

A **modular monolith**: one deployable app, separate packages per domain, so modules can be
split into services later without a rewrite.

## Quick start

```bash
cp .env.example .env
docker compose up -d db redis          # Postgres (pgvector image) + Redis
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload          # docs at http://localhost:8000/docs (local only)
pytest -q && ruff check .
```

No Docker? `DATABASE_URL=sqlite+aiosqlite:///dev.db python -m scripts.seed_dev` creates a
throwaway SQLite database and a demo CHP (`chp@example.org` / `change-me-now`).

## Layout

```
app/
  main.py                  app factory, health/ready, router wiring
  models.py                imports every model (Alembic + tests)
  core/                    config, db, security (Argon2, JWT, phone hash + encryption),
                           deps/RBAC, errors, logging (structlog + request id), audit log
  modules/
    mothers/               onboarding, profile, consent (withdrawable)
    chp/                   CHP accounts, login, cohort dashboard API (cohort-scoped, consent-gated)
    checkins/              check-in submission: idempotent, runs triage, raises alerts
    alerts/                alert lifecycle (open -> acknowledged -> resolved), notify stub
    triage/                rules engine + rules/ruleset.yaml (versioned, data not code)
    channels/              ussd.py, whatsapp.py (webhook), gateway.py (outbound Protocol)
    ai/                    guardrails.py (diagnosis/dosage filter); RAG goes here
    reminders/             placeholder
  workers/                 Celery app + task stubs (pip install -e ".[workers]")
alembic/                   async migrations (0001 = initial schema)
tests/                     triage cases, API, USSD flows, webhook, config
scripts/seed_dev.py
```

## Endpoints

| Method | Path | Who |
|---|---|---|
| POST | `/v1/mothers` | public (OTP verification is a TODO) |
| GET | `/v1/mothers/me` | mother |
| PUT | `/v1/mothers/me/consents` | mother |
| POST | `/v1/checkins` | mother (client-generated UUID = idempotency key) |
| POST | `/v1/auth/chp/login` | CHP |
| GET | `/v1/chp/cohort` | CHP (own cohort only; phone shown only with consent) |
| GET | `/v1/chp/alerts` | CHP |
| POST | `/v1/chp/alerts/{id}/acknowledge` and `/resolve` | CHP |
| POST | `/ussd/callback` | USSD aggregator (form: sessionId, phoneNumber, text) |
| GET/POST | `/webhooks/whatsapp` | Meta (handshake / signed events) |
| GET | `/health`, `/ready` | ops |

## Design decisions worth knowing

- **Triage is deterministic.** Rules live in `ruleset.yaml`, are validated at load, and every
  decision stores the rule version and triggered rule ids. A future model can only escalate
  (`combine_tiers`), never de-escalate.
- **Unknown gestation over-escalates** (rules still apply if weeks are unknown).
- **Phone numbers** are stored Fernet-encrypted and looked up through an HMAC hash; never logged.
- **Idempotency where it matters:** check-in id, one alert per check-in (unique constraint),
  USSD check-in id derived from the session id, WhatsApp message-id dedupe table.
- **CHP access is scoped in the query**, other CHPs get 404, and phone reveals are audit-logged.
- **No LLM on the USSD path.** USSD is pure rules + DB so screens answer in seconds.
- Outside `local`, the app refuses to start with the dev default secrets.

## What is NOT done yet (read before piloting)

1. **Triage rules are illustrative placeholders.** Replace them with rules from the MoH
   guidelines, signed off by your clinical advisor, and replace the cases in
   `tests/test_triage.py`.
2. **Kiswahili strings** (USSD + advice) need native-speaker and clinical review.
3. **Mother authentication:** onboarding issues a token without verifying phone ownership. Add
   SMS OTP and rate limiting before exposing it publicly.
4. **Minors:** confirm consent/assent requirements for under-18 users with legal counsel.
5. **Outbound delivery:** `alerts/notify.py` only logs. Implement `ChannelGateway` for SMS
   and WhatsApp templates, run it from Celery with retries, a dead-letter queue and supervisor
   escalation for unacknowledged Emergency alerts.
6. **WhatsApp conversation handling** (`handle_inbound`) is a stub; wire it to the
   orchestrator. Check Meta's current terms on how Business API data may be used, especially
   for model training.
7. **USSD callback** should be restricted to the aggregator (IP allowlist / shared secret).
8. **RAG + nutrition assistant:** add pgvector tables, ingest the MoH/WHO/KFCT/UNICEF sources,
   and pass all generated text through `ai.guardrails.enforce`.
9. **Not built:** reminders (ANC visits, supplements), disengagement flags, and the offline
   sync batch endpoint.
10. **Keys:** move to a secrets manager and plan key rotation (Fernet `MultiFernet`).
