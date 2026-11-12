from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401  (register tables)
from app.core.config import get_settings
from app.core.db import get_session
from app.core.errors import register_error_handlers
from app.core.logging import add_request_id_middleware, configure_logging
from app.modules.alerts.router import router as alerts_router
from app.modules.channels.ussd import router as ussd_router
from app.modules.channels.whatsapp import router as whatsapp_router
from app.modules.chat.router import router as chat_router
from app.modules.checkins.router import router as checkins_router
from app.modules.chp.router import router as chp_router
from app.modules.mothers.router import router as mothers_router
from app.modules.nutrition.router import router as nutrition_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        # Don't expose interactive docs outside local development.
        docs_url="/docs" if settings.environment == "local" else None,
        redoc_url=None,
    )
    add_request_id_middleware(app)
    register_error_handlers(app)

    for router in (
        mothers_router,
        nutrition_router,
        checkins_router,
        chp_router,
        alerts_router,
        ussd_router,
        whatsapp_router,
    ):
        app.include_router(router)

    if settings.environment == "local":  # demo-only: speaks as any phone number
        app.include_router(chat_router)

        @app.get("/chat", include_in_schema=False)
        async def chat_page() -> FileResponse:
            return FileResponse(Path(__file__).parent / "static" / "chat.html")

    @app.get("/dashboard", include_in_schema=False)
    async def dashboard() -> FileResponse:
        return FileResponse(Path(__file__).parent / "static" / "dashboard.html")

    @app.get("/simulator", include_in_schema=False)
    async def simulator() -> FileResponse:
        return FileResponse(Path(__file__).parent / "static" / "simulator.html")

    @app.get("/health", tags=["ops"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", tags=["ops"])
    async def ready(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
        await session.execute(text("SELECT 1"))
        return {"status": "ready"}

    return app


app = create_app()
