"""Contract tests for the dashboard endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

_JSON = "application/json"
_PIPELINE_KEYS = {"novo", "contato", "negociacao", "proposta", "fechado", "perdido"}


def test_pipeline_contract(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard/pipeline")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(_JSON)
    body = response.json()
    assert set(body.keys()) == _PIPELINE_KEYS
    assert all(isinstance(value, int) for value in body.values())


def test_pipeline_method_is_get_only(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    methods = set(spec["paths"]["/api/v1/dashboard/pipeline"].keys())
    assert methods == {"get"}


def test_summary_contract(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(_JSON)
    body = response.json()
    assert {"clientes", "produtos", "leads", "vendas", "receita", "pipeline"} <= set(body)
    assert set(body["pipeline"].keys()) == _PIPELINE_KEYS
