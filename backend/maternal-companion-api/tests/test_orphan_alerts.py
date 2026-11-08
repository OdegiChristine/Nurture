"""A danger sign must never vanish because a mother has no CHP."""

import uuid

from tests.conftest import auth, onboard

EMERGENCY = {"vaginal_bleeding": True}


async def checkin(client, headers, symptoms=EMERGENCY):
    resp = await client.post(
        "/v1/checkins", json={"id": str(uuid.uuid4()), "symptoms": symptoms}, headers=headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["alert_created"] is True


async def test_no_chp_alert_goes_to_county_supervisor(client, make_chp):
    sup = await make_chp("sup@example.org", county="Tana River", role="supervisor")
    _, headers = await onboard(client, county="Tana River")  # no CHP in Tana River
    await checkin(client, headers)

    alerts = (await client.get("/v1/chp/alerts", headers=auth(sup, "supervisor"))).json()
    assert len(alerts) == 1 and alerts[0]["tier"] == "emergency"


async def test_supervisor_from_another_county_is_the_fallback(client, make_chp):
    sup = await make_chp("sup@example.org", county="Siaya", role="supervisor")
    _, headers = await onboard(client, county="Tana River")
    await checkin(client, headers)
    assert len((await client.get("/v1/chp/alerts", headers=auth(sup, "supervisor"))).json()) == 1


async def test_no_chp_and_no_supervisor_alert_is_unrouted_but_visible_to_admin(client, make_chp):
    admin = await make_chp("admin@example.org", role="admin")
    _, headers = await onboard(client, county="Tana River")
    await checkin(client, headers)

    unrouted = (await client.get("/v1/admin/alerts/unrouted", headers=auth(admin, "admin"))).json()
    assert len(unrouted) == 1


async def test_admin_can_assign_unrouted_alert_to_a_chp(client, make_chp):
    admin = await make_chp("admin@example.org", role="admin")
    chp = await make_chp("chp@example.org", county="Garissa")
    _, headers = await onboard(client, county="Tana River")
    await checkin(client, headers)
    alert_id = (await client.get("/v1/admin/alerts/unrouted", headers=auth(admin, "admin"))).json()[
        0
    ]["id"]

    resp = await client.post(
        f"/v1/admin/alerts/{alert_id}/assign",
        json={"chp_id": str(chp)},
        headers=auth(admin, "admin"),
    )
    assert resp.status_code == 200
    assert (
        await client.get("/v1/admin/alerts/unrouted", headers=auth(admin, "admin"))
    ).json() == []
    assert len((await client.get("/v1/chp/alerts", headers=auth(chp, "chp"))).json()) == 1


async def test_oversight_endpoints_are_not_open_to_chps_or_mothers(client, make_chp):
    chp = await make_chp("chp@example.org")
    _, mother = await onboard(client)
    for headers in (auth(chp, "chp"), mother):
        assert (await client.get("/v1/admin/alerts/unrouted", headers=headers)).status_code == 403
    assert (await client.get("/v1/admin/alerts/unrouted")).status_code == 401


async def test_new_chp_adopts_orphan_mothers_and_their_unrouted_alerts(client, make_chp):
    _, headers = await onboard(client, county="Garissa")  # no CHP yet
    await checkin(client, headers)

    chp = await make_chp("late@example.org", county="Garissa")
    assert len((await client.get("/v1/chp/cohort", headers=auth(chp, "chp"))).json()) == 1
    alerts = (await client.get("/v1/chp/alerts", headers=auth(chp, "chp"))).json()
    assert len(alerts) == 1 and alerts[0]["tier"] == "emergency"
