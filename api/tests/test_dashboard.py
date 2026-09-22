"""Tests for the dashboard API."""

from __future__ import annotations

from fastapi.testclient import TestClient

_PIPELINE_KEYS = {"novo", "contato", "negociacao", "proposta", "fechado", "perdido"}


def _create_lead_in_stage(client: TestClient, stage: str) -> None:
    cliente = client.post("/api/v1/clientes", json={"nome": "Dash Cliente"}).json()
    lead = client.post("/api/v1/leads", json={"cliente_id": cliente["id"]}).json()
    if stage != "novo":
        client.patch(f"/api/v1/leads/{lead['id']}/status", json={"status": stage})


def test_pipeline_shape(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard/pipeline")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == _PIPELINE_KEYS
    assert all(isinstance(v, int) for v in body.values())


def test_pipeline_counts_reflect_leads(client: TestClient) -> None:
    before = client.get("/api/v1/dashboard/pipeline").json()
    _create_lead_in_stage(client, "negociacao")
    after = client.get("/api/v1/dashboard/pipeline").json()
    assert after["negociacao"] == before["negociacao"] + 1


def test_summary(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    for key in ("clientes", "produtos", "leads", "vendas", "receita", "pipeline"):
        assert key in body
    assert set(body["pipeline"].keys()) == _PIPELINE_KEYS
