"""Shared test fixtures."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_health_service
from app.application.dto.health_dto import HealthResponse
from app.core.config import get_settings
from app.main import create_app


class StubHealthService:
    """Health service returning a deterministic healthy report."""

    async def check(self) -> HealthResponse:
        settings = get_settings()
        return HealthResponse(
            status="healthy",
            service=settings.app_name,
            version=settings.app_version,
            environment=settings.app_env,
            dependencies={"database": "up", "redis": "up", "ollama": "up"},
        )


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_health_service] = StubHealthService
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
