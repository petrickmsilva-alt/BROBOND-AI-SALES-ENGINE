"""Contract tests for the leads endpoints.

Validates HTTP method, status code, response schema and content-type against
the documented behaviour and the OpenAPI definition.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

_JSON = "application/json"


def _cliente_id(client: TestClient) -> str:
    return client.post("/api/v1/clientes", json={"nome": "Contract Lead"}).json()["id"]


def test_list_leads_contract(client: TestClient) -> None:
    response = client.get("/api/v1/leads")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(_JSON)
    body = response.json()
    assert set(body.keys()) == {"total", "items"}
    assert isinstance(body["total"], int)
    assert isinstance(body["items"], list)


def test_create_lead_contract(client: TestClient) -> None:
    response = client.post("/api/v1/leads", json={"cliente_id": _cliente_id(client)})
    assert response.status_code == 201
    assert response.headers["content-type"].startswith(_JSON)
    body = response.json()
    expected = {
        "id",
        "cliente_id",
        "origem",
        "score",
        "status",
        "interesse",
        "observacao",
        "created_at",
    }
    assert expected == set(body.keys())
    assert body["status"] == "novo"


def test_patch_status_contract(client: TestClient) -> None:
    lead = client.post("/api/v1/leads", json={"cliente_id": _cliente_id(client)}).json()
    response = client.patch(f"/api/v1/leads/{lead['id']}/status", json={"status": "proposta"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(_JSON)
    assert response.json()["status"] == "proposta"


def test_qualify_endpoint_exists(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    assert "/api/v1/leads/{lead_id}/qualify" in spec["paths"]
    assert "post" in spec["paths"]["/api/v1/leads/{lead_id}/qualify"]


def test_qualify_never_returns_500(client: TestClient) -> None:
    """A qualify call must be 200 (scored) or 503 (AI down), never 500."""
    lead = client.post("/api/v1/leads", json={"cliente_id": _cliente_id(client)}).json()
    response = client.post(f"/api/v1/leads/{lead['id']}/qualify")
    assert response.status_code in {200, 503}
    assert response.headers["content-type"].startswith(_JSON)


def test_get_lead_contract(client: TestClient) -> None:
    lead = client.post("/api/v1/leads", json={"cliente_id": _cliente_id(client)}).json()
    response = client.get(f"/api/v1/leads/{lead['id']}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(_JSON)
    assert response.json()["id"] == lead["id"]
