"""Tests for the AI qualify endpoint's success and failure contracts."""

from __future__ import annotations

from collections.abc import Iterator

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_ai_gateway, get_health_service
from app.domain.repositories.ai_gateway import AIGateway, LeadScoreResult
from app.main import create_app
from tests.conftest import StubHealthService


class _ScoringGateway(AIGateway):
    async def health(self) -> bool:
        return True

    async def score_lead(self, prompt: str) -> LeadScoreResult:
        return LeadScoreResult(score=88, rationale="Excellent fit")


class _FailingGateway(AIGateway):
    async def health(self) -> bool:
        return False

    async def score_lead(self, prompt: str) -> LeadScoreResult:
        raise httpx.ConnectError("ollama down")


@pytest.fixture
def app_client() -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_health_service] = StubHealthService
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _make_lead(client: TestClient) -> str:
    cliente = client.post("/api/v1/clientes", json={"nome": "Qualify Cliente"}).json()
    return client.post("/api/v1/leads", json={"cliente_id": cliente["id"]}).json()["id"]


def test_qualify_success(app_client: TestClient) -> None:
    app_client.app.dependency_overrides[get_ai_gateway] = lambda: _ScoringGateway()
    lead_id = _make_lead(app_client)
    response = app_client.post(f"/api/v1/leads/{lead_id}/qualify")
    assert response.status_code == 200
    body = response.json()
    assert body["score"] == 88
    assert body["rationale"] == "Excellent fit"


def test_qualify_ai_unavailable_returns_503(app_client: TestClient) -> None:
    app_client.app.dependency_overrides[get_ai_gateway] = lambda: _FailingGateway()
    lead_id = _make_lead(app_client)
    response = app_client.post(f"/api/v1/leads/{lead_id}/qualify")
    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/json")


def test_qualify_unknown_lead_returns_404(app_client: TestClient) -> None:
    app_client.app.dependency_overrides[get_ai_gateway] = lambda: _ScoringGateway()
    response = app_client.post("/api/v1/leads/00000000-0000-0000-0000-000000000000/qualify")
    assert response.status_code == 404
