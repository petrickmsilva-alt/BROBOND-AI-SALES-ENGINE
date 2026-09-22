"""Tests for the leads API, including pipeline status transitions."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_cliente(client: TestClient) -> str:
    response = client.post("/api/v1/clientes", json={"nome": "Lead Owner"})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_lead(client: TestClient, cliente_id: str | None = None) -> dict:
    cliente_id = cliente_id or _create_cliente(client)
    response = client.post(
        "/api/v1/leads",
        json={
            "cliente_id": cliente_id,
            "origem": "instagram",
            "interesse": "Oversized",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_lead(client: TestClient) -> None:
    body = _create_lead(client)
    assert body["origem"] == "instagram"
    assert body["status"] == "novo"


def test_create_lead_unknown_cliente(client: TestClient) -> None:
    response = client.post(
        "/api/v1/leads",
        json={"cliente_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404


def test_create_lead_invalid_cliente_id(client: TestClient) -> None:
    response = client.post("/api/v1/leads", json={"cliente_id": "not-a-uuid"})
    assert response.status_code == 422


def test_list_leads(client: TestClient) -> None:
    _create_lead(client)
    response = client.get("/api/v1/leads")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert isinstance(body["items"], list)


def test_get_lead(client: TestClient) -> None:
    created = _create_lead(client)
    response = client.get(f"/api/v1/leads/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_lead_status(client: TestClient) -> None:
    created = _create_lead(client)
    response = client.patch(
        f"/api/v1/leads/{created['id']}/status",
        json={"status": "negociacao"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "negociacao"


def test_update_lead_status_invalid(client: TestClient) -> None:
    created = _create_lead(client)
    response = client.patch(
        f"/api/v1/leads/{created['id']}/status",
        json={"status": "invalido"},
    )
    assert response.status_code == 422


def test_update_lead_status_not_found(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/leads/00000000-0000-0000-0000-000000000000/status",
        json={"status": "fechado"},
    )
    assert response.status_code == 404


def test_full_pipeline_transition(client: TestClient) -> None:
    created = _create_lead(client)
    for stage in ["contato", "negociacao", "proposta", "fechado"]:
        response = client.patch(
            f"/api/v1/leads/{created['id']}/status",
            json={"status": stage},
        )
        assert response.status_code == 200
        assert response.json()["status"] == stage
