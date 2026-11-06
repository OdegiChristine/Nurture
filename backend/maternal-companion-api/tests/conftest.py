import os

# Must be set before the app (and its cached settings) are imported. Real environment variables
# take priority over any local .env file, so the tests behave the same on every machine.
os.environ.update(
    {
        "ENVIRONMENT": "local",
        "DATABASE_URL": "sqlite+aiosqlite://",
        "JWT_SECRET": "test-jwt-secret-test-jwt-secret-1234",
        "PHONE_HASH_PEPPER": "test-pepper-test-pepper-test-pepper-1",
        "FIELD_ENCRYPTION_KEY": "DRP9v8RoAwRKgkggsRa0pBKI9S6ppNpr1AjyIQhn5Xo=",
        "WHATSAPP_APP_SECRET": "test-app-secret",
        "WHATSAPP_VERIFY_TOKEN": "test-verify-token",
    }
)

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401
from app.core.db import Base, get_session  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.main import create_app  # noqa: E402
from app.modules.chp.service import create_chp  # noqa: E402

PASSWORD = "correct-horse-battery"


@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session_factory):
    app = create_app()

    async def _session():
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_session] = _session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def make_chp(session_factory):
    async def _make(email: str, county: str = "Siaya"):
        async with session_factory() as s:
            chp = await create_chp(s, name=email, email=email, password=PASSWORD, county=county)
            return chp.id

    return _make


def auth(sub, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(sub), role)}"}


async def onboard(client, phone="0712345678", weeks=28, county="Siaya", consent=False, **extra):
    body = {
        "phone": phone,
        "age": 16,
        "gestation_weeks": weeks,
        "county": county,
        "consent_chp_contact": consent,
        **extra,
    }
    resp = await client.post("/v1/mothers", json=body)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return data["mother"]["id"], {"Authorization": f"Bearer {data['access_token']}"}
