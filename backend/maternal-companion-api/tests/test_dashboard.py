import uuid

from tests.conftest import auth, onboard


async def test_dashboard_page_is_served(client):
    resp = await client.get("/dashboard")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Maternal Companion" in resp.text


async def test_alerts_and_cohort_carry_safe_display_labels(client, make_chp):
    chp = await make_chp("chp@example.org")
    _, named = await onboard(client, phone="0711111111", pseudonym="Achieng")
    _, anon = await onboard(client, phone="0722222222")
    for headers in (named, anon):
        await client.post(
            "/v1/checkins",
            json={"id": str(uuid.uuid4()), "symptoms": {"vaginal_bleeding": True}},
            headers=headers,
        )
    h = auth(chp, "chp")
    alerts = (await client.get("/v1/chp/alerts", headers=h)).json()
    labels = sorted(a["label"] for a in alerts)
    assert labels[0] == "Achieng" and labels[1].startswith("Anonymous #")
    assert all(a["county"] == "Siaya" and a["gestation_weeks"] == 28 for a in alerts)
    assert "2222" not in "".join(labels)  # never leaks phone digits into labels
    assert {c["label"] for c in (await client.get("/v1/chp/cohort", headers=h)).json()} == set(
        labels
    )


async def test_supervisor_sees_labels_for_mothers_outside_their_cohort(client, make_chp):
    sup = await make_chp("sup@example.org", county="Tana River", role="supervisor")
    _, headers = await onboard(client, county="Tana River", pseudonym="Zawadi")
    await client.post(
        "/v1/checkins",
        json={"id": str(uuid.uuid4()), "symptoms": {"vaginal_bleeding": True}},
        headers=headers,
    )
    alerts = (await client.get("/v1/chp/alerts", headers=auth(sup, "supervisor"))).json()
    assert [a["label"] for a in alerts] == ["Zawadi"]
    ack = await client.post(
        f"/v1/chp/alerts/{alerts[0]['id']}/acknowledge", headers=auth(sup, "supervisor")
    )
    assert ack.json()["label"] == "Zawadi" and ack.json()["status"] == "acknowledged"
