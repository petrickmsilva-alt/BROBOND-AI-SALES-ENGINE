"""Contract tests for the clientes endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

_JSON = "application/json"
_CLIENTE_KEYS = {
    "id",
    "nome",
    "telefone",
    "email",
    "instagram",
    "cidade",
    "created_at",
    "updated_at",
}


def test_list_clientes_contract(client: TestClient) -> None:
    response = client.get("/api/v1/clientes")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(_JSON)
    body = response.json()
    assert set(body.keys()) == {"total", "items"}


def test_create_cliente_contract(client: TestClient) -> None:
    response = client.post("/api/v1/clientes", json={"nome": "Contract Cliente"})
    assert response.status_code == 201
    assert response.headers["content-type"].startswith(_JSON)
    assert set(response.json().keys()) == _CLIENTE_KEYS


def test_get_cliente_contract(client: TestClient) -> None:
    created = client.post("/api/v1/clientes", json={"nome": "Get Cliente"}).json()
    response = client.get(f"/api/v1/clientes/{created['id']}")
    assert response.status_code == 200
    assert set(response.json().keys()) == _CLIENTE_KEYS


def test_update_cliente_contract(client: TestClient) -> None:
    created = client.post("/api/v1/clientes", json={"nome": "Put Cliente"}).json()
    response = client.put(f"/api/v1/clientes/{created['id']}", json={"cidade": "Goiânia"})
    assert response.status_code == 200
    assert response.json()["cidade"] == "Goiânia"


def test_delete_cliente_contract(client: TestClient) -> None:
    created = client.post("/api/v1/clientes", json={"nome": "Del Cliente"}).json()
    response = client.delete(f"/api/v1/clientes/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""


def test_clientes_methods_match_spec(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    assert set(spec["paths"]["/api/v1/clientes"].keys()) == {"get", "post"}
    assert set(spec["paths"]["/api/v1/clientes/{cliente_id}"].keys()) == {
        "get",
        "put",
        "delete",
    }


def test_not_found_returns_json(client: TestClient) -> None:
    response = client.get("/api/v1/clientes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith(_JSON)
