from tests.conftest import PASSWORD  # noqa: F401


async def dial(client, text, phone="0712345678", session_id="s1"):
    resp = await client.post(
        "/ussd/callback", data={"sessionId": session_id, "phoneNumber": phone, "text": text}
    )
    assert resp.status_code == 200
    return resp.text


async def test_registration_flow_then_menu(client, make_chp):
    await make_chp("chp1@example.org", county="Siaya")
    assert (await dial(client, "")).startswith("CON Welcome / Karibu")
    assert "weeks pregnant" in await dial(client, "1")
    assert (await dial(client, "1*20")).startswith("CON Your age")
    assert (await dial(client, "1*20*17")).startswith("CON County")
    assert (await dial(client, "1*20*17*3")).startswith("CON May your health worker")
    assert (await dial(client, "1*20*17*3*1")).startswith("END You are registered")
    assert (await dial(client, "")).startswith("CON Welcome back")


async def test_registration_rejects_bad_input(client):
    assert (await dial(client, "1*99")).startswith("END Invalid")
    assert (await dial(client, "9")).startswith("END Invalid")


async def _register(client, lang="1"):
    await dial(client, f"{lang}*28*17*3*1")


async def test_full_symptom_check_emergency(client, make_chp):
    chp_id = await make_chp("chp1@example.org", county="Siaya")
    await _register(client)
    # headache=yes, vision=yes, others no  -> emergency (28 weeks)
    path = "1*1*1*2*2*2*2"
    out = await dial(client, path, session_id="sess-emergency")
    assert out.startswith("END This is an emergency")
    # retry of the same USSD session must not duplicate the check-in/alert
    await dial(client, path, session_id="sess-emergency")

    from tests.conftest import auth

    alerts = (await client.get("/v1/chp/alerts", headers=auth(chp_id, "chp"))).json()
    assert len(alerts) == 1 and alerts[0]["tier"] == "emergency"


async def test_symptom_check_low_and_questions_progress(client):
    await _register(client)
    assert (await dial(client, "1")).startswith("CON Do you have a severe headache")
    assert (await dial(client, "1*2")).startswith("CON Blurred vision")
    out = await dial(client, "1*2*2*2*2*2*2", session_id="sess-low")
    assert out.startswith("END Keep attending clinic visits")


async def test_swahili_flow(client):
    await _register(client, lang="2")
    assert (await dial(client, "")).startswith("CON Karibu tena")
    assert (await dial(client, "1")).startswith("CON Una maumivu makali ya kichwa")


async def test_invalid_input_ends_session_and_tip(client):
    await _register(client)
    assert (await dial(client, "1*3")).startswith("END Invalid")
    assert (await dial(client, "7")).startswith("END Invalid")
    assert "omena" in await dial(client, "2")


async def test_every_ussd_screen_fits_the_limit():
    from app.modules.channels.ussd import STRINGS

    for lang, table in STRINGS.items():
        for key, text in table.items():
            assert len(text) + 4 <= 160, f"{lang}.{key} is {len(text)} chars"
