"""FastAPI application factory and ASGI entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.routes import health
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.infrastructure.cache.redis_client import close_redis
from app.infrastructure.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown of shared resources."""
    yield
    await close_redis()
    await dispose_engine()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application."""
    config = settings or get_settings()
    configure_logging(config.debug)

    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        description="Enterprise AI sales engine API.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(api_router, prefix=config.api_v1_prefix)

    @app.get("/", tags=["meta"], summary="Service metadata")
    async def root() -> dict[str, str]:
        """Return basic service metadata."""
        return {
            "service": config.app_name,
            "version": config.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
