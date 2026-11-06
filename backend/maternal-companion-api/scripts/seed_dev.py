"""Create tables (dev only -- use Alembic elsewhere) and a demo CHP.

python -m scripts.seed_dev
"""

import asyncio

import app.models  # noqa: F401
from app.core.db import Base, SessionLocal, engine
from app.modules.chp.service import create_chp


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as session:
        await create_chp(
            session,
            name="Demo CHP",
            email="chp@example.org",
            password="change-me-now",  # noqa: S106
            county="Siaya",
        )
    print("Seeded demo CHP: chp@example.org / change-me-now")


if __name__ == "__main__":
    asyncio.run(main())
