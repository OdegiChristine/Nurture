import uuid

from tests.conftest import auth


async def say(client, phone, text, reset=False):
    resp = await client.post(
        "/chat/simulate",
        json={"phone": phone, "text": text, "reset": reset, "message_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["messages"]


async def register(client, phone, lang="1"):
    for text in ["hi", lang, "28", "17", "3", "Naomi", "1", "1"]:
        out = await say(client, phone, text)
    return out


async def test_full_registration_creates_a_mother_with_chosen_details(client, make_chp):
    chp = await make_chp("grace@example.org", county="Siaya")
    out = await register(client, "0700000005")
    assert "registered" in out[0]["text"] and out[0]["buttons"] == [
        "Symptom check",
        "Nutrition tip",
    ]
    cohort = (await client.get("/v1/chp/cohort", headers=auth(chp, "chp"))).json()
    assert [c["label"] for c in cohort] == ["Naomi"]
    assert cohort[0]["phone"] == "+254700000005"  # consented, so visible


async def test_registration_validates_input_and_can_skip_nickname(client):
    phone = "0700000006"
    await say(client, phone, "hi")
    await say(client, phone, "1")
    assert "number" in (await say(client, phone, "abc"))[0]["text"]
    assert "weeks" in (await say(client, phone, "99"))[0]["text"]
    await say(client, phone, "20")
    await say(client, phone, "17")
    assert "choose" in (await say(client, phone, "Mars"))[0]["text"]
    await say(client, phone, "Siaya")
    await say(client, phone, "skip")
    await say(client, phone, "None")
    out = await say(client, phone, "No")
    assert "registered" in out[0]["text"]


async def test_danger_signs_in_chat_alert_the_chp(client, make_chp):
    chp = await make_chp("grace@example.org", county="Siaya")
    await register(client, "0700000005")
    for text in ["hi", "1", "1", "1", "2", "2", "2", "2"]:
        out = await say(client, "0700000005", text)
    assert "emergency" in out[0]["text"].lower()
    alerts = (await client.get("/v1/chp/alerts", headers=auth(chp, "chp"))).json()
    assert len(alerts) == 1 and alerts[0]["tier"] == "emergency" and alerts[0]["label"] == "Naomi"


async def test_low_risk_check_and_nutrition_tip(client):
    await register(client, "0700000005")
    await say(client, "0700000005", "hi")
    await say(client, "0700000005", "Symptom check")
    for _ in range(5):
        await say(client, "0700000005", "No")
    out = await say(client, "0700000005", "No")
    assert "Keep attending" in out[0]["text"]
    assert "omena" in (await say(client, "0700000005", "Nutrition tip"))[0]["text"]


async def test_swahili_and_menu_escape_and_bad_answer(client):
    await register(client, "0700000007", lang="2")
    menu = await say(client, "0700000007", "hi")
    assert menu[0]["buttons"] == ["Kagua dalili", "Ushauri wa lishe"]
    await say(client, "0700000007", "1")
    assert "Tafadhali chagua" in (await say(client, "0700000007", "maybe"))[0]["text"]
    assert (await say(client, "0700000007", "menu"))[0]["buttons"]


async def test_same_mother_is_recognised_across_ussd_and_chat(client):
    await client.post(
        "/ussd/callback",
        data={"sessionId": "r", "phoneNumber": "0700000008", "text": "1*28*17*3*1"},
    )
    menu = await say(client, "0700000008", "hi")
    assert menu[0]["buttons"] == ["Symptom check", "Nutrition tip"]


async def test_bad_phone_and_page_served(client):
    resp = await client.post("/chat/simulate", json={"phone": "123", "text": "hi"})
    assert resp.status_code == 400
    assert "chat simulator" in (await client.get("/chat")).text.lower()
