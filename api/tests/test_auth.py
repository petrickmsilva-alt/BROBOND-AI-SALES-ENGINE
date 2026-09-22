"""End-to-end tests for the authentication flow."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _register(client: TestClient, email: str) -> dict:
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Sales Person",
            "password": "supersecret",
        },
    ).json()


def test_register_login_and_me(client: TestClient) -> None:
    email = "rep1@example.com"
    registered = _register(client, email)
    assert registered["email"] == email

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "supersecret"},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["token_type"] == "bearer"

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_register_duplicate_email(client: TestClient) -> None:
    _register(client, "dup@example.com")
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "full_name": "Other",
            "password": "supersecret",
        },
    )
    assert response.status_code == 409


def test_login_bad_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpass1"},
    )
    assert response.status_code == 401


def test_me_requires_token(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_rejects_garbage_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401
