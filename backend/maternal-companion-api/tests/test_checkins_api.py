import uuid

from tests.conftest import PASSWORD, auth, onboard


async def test_high_risk_checkin_creates_one_alert_even_when_resubmitted(client, make_chp):
    chp_id = await make_chp("chp1@example.org")
    mother_id, headers = await onboard(client)
    cid = str(uuid.uuid4())
    body = {"id": cid, "symptoms": {"severe_headache": True, "swelling_face_hands": True}}

    first = await client.post("/v1/checkins", json=body, headers=headers)
    assert first.status_code == 200
    assert first.json()["risk_tier"] == "high"
    assert first.json()["alert_created"] is True
    assert first.json()["duplicate"] is False

    again = await client.post("/v1/checkins", json=body, headers=headers)  # offline-sync retry
    assert again.json()["duplicate"] is True

    alerts = await client.get("/v1/chp/alerts", headers=auth(chp_id, "chp"))
    assert len(alerts.json()) == 1
    assert alerts.json()[0]["tier"] == "high"


async def test_low_risk_checkin_creates_no_alert(client, make_chp):
    chp_id = await make_chp("chp1@example.org")
    _, headers = await onboard(client)
    resp = await client.post(
        "/v1/checkins",
        json={"id": str(uuid.uuid4()), "symptoms": {"fever": False}},
        headers=headers,
    )
    assert resp.json()["risk_tier"] == "low"
    assert resp.json()["alert_created"] is False
    assert (await client.get("/v1/chp/alerts", headers=auth(chp_id, "chp"))).json() == []


async def test_unknown_symptom_rejected(client):
    _, headers = await onboard(client)
    resp = await client.post(
        "/v1/checkins",
        json={"id": str(uuid.uuid4()), "symptoms": {"made_up": True}},
        headers=headers,
    )
    assert resp.status_code == 422


async def test_checkin_requires_mother_token(client, make_chp):
    chp_id = await make_chp("chp1@example.org")
    body = {"id": str(uuid.uuid4()), "symptoms": {}}
    assert (await client.post("/v1/checkins", json=body)).status_code == 401
    assert (
        await client.post("/v1/checkins", json=body, headers=auth(chp_id, "chp"))
    ).status_code == 403


async def test_chp_cannot_see_or_touch_another_chps_mothers_or_alerts(client, make_chp):
    chp_a = await make_chp("a@example.org", county="Siaya")
    chp_b = await make_chp("b@example.org", county="Garissa")
    _, headers = await onboard(client, county="Siaya")  # assigned to A
    await client.post(
        "/v1/checkins",
        json={"id": str(uuid.uuid4()), "symptoms": {"vaginal_bleeding": True}},
        headers=headers,
    )

    a_alerts = (await client.get("/v1/chp/alerts", headers=auth(chp_a, "chp"))).json()
    assert len(a_alerts) == 1 and a_alerts[0]["tier"] == "emergency"

    assert (await client.get("/v1/chp/alerts", headers=auth(chp_b, "chp"))).json() == []
    assert (await client.get("/v1/chp/cohort", headers=auth(chp_b, "chp"))).json() == []
    stolen = await client.post(
        f"/v1/chp/alerts/{a_alerts[0]['id']}/acknowledge", headers=auth(chp_b, "chp")
    )
    assert stolen.status_code == 404


async def test_phone_only_visible_to_chp_with_consent_and_revocable(client, make_chp):
    chp_id = await make_chp("chp1@example.org")
    _, consenting = await onboard(client, phone="0712345678", consent=True)
    _, private = await onboard(client, phone="0722222222", consent=False)
    h = auth(chp_id, "chp")

    items = (await client.get("/v1/chp/cohort", headers=h)).json()
    phones = sorted(str(i["phone"]) for i in items)
    assert phones == ["+254712345678", "None"]

    await client.put(
        "/v1/mothers/me/consents",
        json={"scope": "chp_contact", "granted": False},
        headers=consenting,
    )
    items = (await client.get("/v1/chp/cohort", headers=h)).json()
    assert all(i["phone"] is None for i in items)


async def test_cohort_sorted_by_risk(client, make_chp):
    chp_id = await make_chp("chp1@example.org")
    _, low = await onboard(client, phone="0711111111")
    _, high = await onboard(client, phone="0722222222")
    for headers, symptoms in ((low, {"fever": False}), (high, {"severe_abdominal_pain": True})):
        await client.post(
            "/v1/checkins", json={"id": str(uuid.uuid4()), "symptoms": symptoms}, headers=headers
        )
    items = (await client.get("/v1/chp/cohort", headers=auth(chp_id, "chp"))).json()
    assert [i["latest_tier"] for i in items] == ["high", "low"]


async def test_alert_lifecycle(client, make_chp):
    chp_id = await make_chp("chp1@example.org")
    _, headers = await onboard(client)
    await client.post(
        "/v1/checkins",
        json={"id": str(uuid.uuid4()), "symptoms": {"vaginal_bleeding": True}},
        headers=headers,
    )
    h = auth(chp_id, "chp")
    alert_id = (await client.get("/v1/chp/alerts", headers=h)).json()[0]["id"]
    assert (await client.post(f"/v1/chp/alerts/{alert_id}/acknowledge", headers=h)).json()[
        "status"
    ] == "acknowledged"
    resolved = await client.post(
        f"/v1/chp/alerts/{alert_id}/resolve",
        json={"note": "Referred, mother at facility"},
        headers=h,
    )
    assert resolved.json()["status"] == "resolved"
    assert (await client.get("/v1/chp/alerts", headers=h)).json() == []
    assert (
        await client.post(f"/v1/chp/alerts/{alert_id}/resolve", json={"note": "x"}, headers=h)
    ).status_code == 409


async def test_duplicate_phone_rejected_and_bad_phone_rejected(client):
    await onboard(client, phone="0712345678")
    dup = await client.post(
        "/v1/mothers",
        json={"phone": "+254 712 345 678", "age": 17, "gestation_weeks": 10, "county": "Siaya"},
    )
    assert dup.status_code == 409
    bad = await client.post(
        "/v1/mothers", json={"phone": "12345", "age": 17, "gestation_weeks": 10, "county": "Siaya"}
    )
    assert bad.status_code == 400


async def test_chp_login(client, make_chp):
    await make_chp("chp1@example.org")
    ok = await client.post(
        "/v1/auth/chp/login", json={"email": "CHP1@example.org", "password": PASSWORD}
    )
    assert ok.status_code == 200 and ok.json()["access_token"]
    bad = await client.post(
        "/v1/auth/chp/login", json={"email": "chp1@example.org", "password": "wrong"}
    )
    assert bad.status_code == 401
    ghost = await client.post(
        "/v1/auth/chp/login", json={"email": "nobody@example.org", "password": PASSWORD}
    )
    assert ghost.status_code == 401


async def test_phone_is_not_stored_in_plaintext(client, session_factory):
    from sqlalchemy import select

    from app.modules.mothers.models import Mother

    await onboard(client, phone="0712345678")
    async with session_factory() as s:
        m = (await s.execute(select(Mother))).scalar_one()
    assert b"712345678" not in m.phone_enc
    assert "712345678" not in m.phone_hash
