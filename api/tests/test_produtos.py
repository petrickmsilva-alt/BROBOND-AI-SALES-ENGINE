"""CRUD tests for the produtos API."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient


def _create_produto(client: TestClient, sku: str | None = None) -> dict:
    sku = sku or f"BB-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/v1/produtos",
        json={
            "sku": sku,
            "nome": "Camiseta Essential Preto",
            "descricao": "Camiseta BroBond na cor Preto.",
            "categoria": "Camisetas",
            "cor": "Preto",
            "tamanho": "M",
            "preco": "89.90",
            "estoque": 50,
            "ativo": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_produto(client: TestClient) -> None:
    body = _create_produto(client)
    assert body["nome"] == "Camiseta Essential Preto"
    assert body["preco"] == "89.90"
    assert body["estoque"] == 50


def test_create_produto_duplicate_sku(client: TestClient) -> None:
    created = _create_produto(client)
    response = client.post(
        "/api/v1/produtos",
        json={"sku": created["sku"], "nome": "Outro", "preco": "10.00"},
    )
    assert response.status_code == 409


def test_list_produtos(client: TestClient) -> None:
    _create_produto(client)
    response = client.get("/api/v1/produtos")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert isinstance(body["items"], list)


def test_get_produto(client: TestClient) -> None:
    created = _create_produto(client)
    response = client.get(f"/api/v1/produtos/{created['id']}")
    assert response.status_code == 200
    assert response.json()["sku"] == created["sku"]


def test_get_produto_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/produtos/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_produto(client: TestClient) -> None:
    created = _create_produto(client)
    response = client.put(
        f"/api/v1/produtos/{created['id']}",
        json={"preco": "119.90", "estoque": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["preco"] == "119.90"
    assert body["estoque"] == 10


def test_update_produto_not_found(client: TestClient) -> None:
    response = client.put(
        "/api/v1/produtos/00000000-0000-0000-0000-000000000000",
        json={"preco": "1.00"},
    )
    assert response.status_code == 404


def test_update_produto_duplicate_sku(client: TestClient) -> None:
    first = _create_produto(client)
    second = _create_produto(client)
    response = client.put(
        f"/api/v1/produtos/{second['id']}",
        json={"sku": first["sku"]},
    )
    assert response.status_code == 409


def test_create_produto_negative_price_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/produtos",
        json={"sku": "NEG-1", "nome": "Bad", "preco": "-1.00"},
    )
    assert response.status_code == 422
