"""CRUD tests for the clientes API."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_cliente(client: TestClient, nome: str = "Cliente Teste") -> dict:
    response = client.post(
        "/api/v1/clientes",
        json={
            "nome": nome,
            "telefone": "+55 62 99999-0000",
            "email": "cliente@example.com",
            "instagram": "@cliente",
            "cidade": "Goiânia",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_cliente(client: TestClient) -> None:
    body = _create_cliente(client, "Ana Souza")
    assert body["nome"] == "Ana Souza"
    assert body["cidade"] == "Goiânia"
    assert body["id"]


def test_get_cliente(client: TestClient) -> None:
    created = _create_cliente(client, "Bruno Lima")
    response = client.get(f"/api/v1/clientes/{created['id']}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Bruno Lima"


def test_get_cliente_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/clientes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_clientes(client: TestClient) -> None:
    _create_cliente(client, "Carla Dias")
    response = client.get("/api/v1/clientes")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert isinstance(body["items"], list)


def test_update_cliente(client: TestClient) -> None:
    created = _create_cliente(client, "Diego Nunes")
    response = client.put(
        f"/api/v1/clientes/{created['id']}",
        json={"cidade": "São Paulo"},
    )
    assert response.status_code == 200
    assert response.json()["cidade"] == "São Paulo"


def test_update_cliente_not_found(client: TestClient) -> None:
    response = client.put(
        "/api/v1/clientes/00000000-0000-0000-0000-000000000000",
        json={"nome": "Ghost"},
    )
    assert response.status_code == 404


def test_delete_cliente(client: TestClient) -> None:
    created = _create_cliente(client, "Eduarda Reis")
    response = client.delete(f"/api/v1/clientes/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/v1/clientes/{created['id']}").status_code == 404


def test_delete_cliente_not_found(client: TestClient) -> None:
    response = client.delete("/api/v1/clientes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_cliente_validation_error(client: TestClient) -> None:
    response = client.post("/api/v1/clientes", json={"nome": "A"})
    assert response.status_code == 422
