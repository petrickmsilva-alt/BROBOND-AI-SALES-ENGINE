"""Fixtures shared by the contract test-suite."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

_SNAPSHOT_PATH = Path(__file__).resolve().parent / "openapi_snapshot.json"


@pytest.fixture(scope="session")
def openapi_snapshot() -> dict[str, Any]:
    """Return the committed OpenAPI snapshot."""
    with _SNAPSHOT_PATH.open() as handle:
        return json.load(handle)


def current_spec(client: Any) -> dict[str, Any]:
    """Return the live paths->methods map exposed by the running app."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    return {
        "openapi": spec.get("openapi"),
        "paths": {
            path: sorted(m.upper() for m in methods)
            for path, methods in sorted(spec["paths"].items())
        },
    }
