import hashlib
import hmac
import json

SECRET = "test-app-secret"


def signed(payload: dict) -> tuple[bytes, dict[str, str]]:
    raw = json.dumps(payload).encode()
    sig = "sha256=" + hmac.new(SECRET.encode(), raw, hashlib.sha256).hexdigest()
    return raw, {"x-hub-signature-256": sig, "content-type": "application/json"}


def payload(message_id: str) -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": message_id,
                                    "from": "254712345678",
                                    "type": "text",
                                    "text": {"body": "hello"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }


async def test_verification_handshake(client):
    ok = await client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": "1234",
        },
    )
    assert ok.status_code == 200 and ok.text == "1234"
    bad = await client.get(
        "/webhooks/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "nope", "hub.challenge": "1234"},
    )
    assert bad.status_code == 403


async def test_rejects_missing_or_bad_signature(client):
    raw = json.dumps(payload("wamid.1")).encode()
    assert (await client.post("/webhooks/whatsapp", content=raw)).status_code == 403
    bad = await client.post(
        "/webhooks/whatsapp", content=raw, headers={"x-hub-signature-256": "sha256=deadbeef"}
    )
    assert bad.status_code == 403


async def test_accepts_signed_payload_and_dedupes_retries(client, session_factory):
    from sqlalchemy import func, select

    from app.modules.channels.models import InboundMessage

    raw, headers = signed(payload("wamid.ABC"))
    assert (
        await client.post("/webhooks/whatsapp", content=raw, headers=headers)
    ).status_code == 200
    assert (
        await client.post("/webhooks/whatsapp", content=raw, headers=headers)
    ).status_code == 200  # retry
    async with session_factory() as s:
        count = (await s.execute(select(func.count()).select_from(InboundMessage))).scalar_one()
    assert count == 1
