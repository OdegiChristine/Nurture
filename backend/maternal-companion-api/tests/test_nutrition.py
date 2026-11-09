import pytest

from app.modules.ai.guardrails import check_output
from app.modules.nutrition.service import nutrition_tip, trimester
from tests.conftest import onboard


@pytest.mark.parametrize("weeks", [1, 13, 14, 27, 28, 42])
@pytest.mark.parametrize("county", ["Siaya", "Garissa", "Tana River", "Kisumu", "  garissa "])
@pytest.mark.parametrize("lang", ["en", "sw", "fr"])
def test_every_tip_is_safe_and_fits_a_ussd_screen(weeks, county, lang):
    tip = nutrition_tip(weeks, county, lang)
    assert tip and len(tip) <= 150 and check_output(tip).allowed


def test_trimester_boundaries():
    assert [trimester(w) for w in (1, 13, 14, 27, 28, 42)] == [1, 1, 2, 2, 3, 3]


def test_tip_varies_by_trimester_and_county():
    assert nutrition_tip(10, "Siaya") != nutrition_tip(30, "Siaya")
    assert "omena" in nutrition_tip(20, "Siaya") and "omena" not in nutrition_tip(20, "Garissa")
    assert "camel" in nutrition_tip(20, "garissa")
    assert nutrition_tip(20, "Nowhere")  # unknown county falls back to a generic list


async def test_nutrition_endpoint_and_ussd_use_the_same_logic(client):
    _, headers = await onboard(client, phone="0722000009", weeks=10, county="Garissa")
    resp = await client.get("/v1/mothers/me/nutrition", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"trimester": 1, "tip": nutrition_tip(10, "Garissa")}
    ussd = await client.post(
        "/ussd/callback", data={"sessionId": "n1", "phoneNumber": "0722000009", "text": "2"}
    )
    assert ussd.text == "END " + nutrition_tip(10, "Garissa")


async def test_simulator_page_is_served(client):
    resp = await client.get("/simulator")
    assert resp.status_code == 200 and "USSD phone simulator" in resp.text
