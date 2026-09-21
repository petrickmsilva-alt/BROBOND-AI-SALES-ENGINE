"""Use case aggregating dependency health."""

from __future__ import annotations

import logging

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.health_dto import ComponentStatus, HealthResponse
from app.core.config import Settings
from app.domain.repositories.ai_gateway import AIGateway

logger = logging.getLogger(__name__)


class HealthService:
    """Checks every downstream dependency."""

    def __init__(
        self,
        settings: Settings,
        session: AsyncSession | None = None,
        redis: Redis | None = None,
        ai_gateway: AIGateway | None = None,
    ) -> None:
        self._settings = settings
        self._session = session
        self._redis = redis
        self._ai = ai_gateway

    async def check(self) -> HealthResponse:
        """Return the aggregated health report."""
        dependencies: dict[str, ComponentStatus] = {
            "database": await self._check_database(),
            "redis": await self._check_redis(),
            "ollama": await self._check_ollama(),
        }
        critical_down = any(
            dependencies[name] == "down" for name in ("database", "redis") if name in dependencies
        )
        return HealthResponse(
            status="degraded" if critical_down else "healthy",
            service=self._settings.app_name,
            version=self._settings.app_version,
            environment=self._settings.app_env,
            dependencies=dependencies,
        )

    async def _check_database(self) -> ComponentStatus:
        if self._session is None:
            return "down"
        try:
            await self._session.execute(text("SELECT 1"))
        except Exception as exc:
            logger.warning("Database health check failed: %s", exc)
            return "down"
        return "up"

    async def _check_redis(self) -> ComponentStatus:
        if self._redis is None:
            return "down"
        try:
            await self._redis.ping()
        except Exception as exc:
            logger.warning("Redis health check failed: %s", exc)
            return "down"
        return "up"

    async def _check_ollama(self) -> ComponentStatus:
        if self._ai is None:
            return "down"
        return "up" if await self._ai.health() else "down"
