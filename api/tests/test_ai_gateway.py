"""Tests for the Ollama gateway and its response parsing."""

from __future__ import annotations

import httpx
import pytest

from app.core.config import get_settings
from app.infrastructure.llm.ollama_gateway import OllamaGateway, _parse_score


def test_parse_score_extracts_json() -> None:
    result = _parse_score('Here you go {"score": 73, "rationale": "Good fit"} end')
    assert result.score == 73
    assert result.rationale == "Good fit"


def test_parse_score_clamps_range() -> None:
    result = _parse_score('{"score": 250, "rationale": "x"}')
    assert result.score == 100


def test_parse_score_handles_garbage() -> None:
    result = _parse_score("no json here")
    assert result.score == 0
    assert result.rationale


def test_parse_score_handles_invalid_json() -> None:
    result = _parse_score('{"score": "abc"')
    assert result.score == 0


@pytest.mark.asyncio
async def test_health_returns_false_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    gateway = OllamaGateway(get_settings())

    class _Client:
        async def __aenter__(self) -> _Client:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def get(self, url: str) -> httpx.Response:
            raise httpx.ConnectError("down")

    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: _Client())
    assert await gateway.health() is False


@pytest.mark.asyncio
async def test_score_lead_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    gateway = OllamaGateway(get_settings())

    class _Response:
        status_code = 200

        def json(self) -> dict[str, str]:
            return {"response": '{"score": 60, "rationale": "ok"}'}

        def raise_for_status(self) -> None:
            return None

    class _Client:
        async def __aenter__(self) -> _Client:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, url: str, json: dict) -> _Response:
            return _Response()

    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: _Client())
    result = await gateway.score_lead("prompt")
    assert result.score == 60
