"""Guard the public OpenAPI surface against silent regressions.

If any endpoint disappears, changes HTTP method, or the OpenAPI version shifts
without the snapshot being regenerated, this test fails and CI blocks the merge.
Regenerate intentionally with ``python -m scripts.update_openapi_snapshot``.
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from tests.contracts.conftest import current_spec


def test_openapi_version_matches(client: TestClient, openapi_snapshot: dict[str, Any]) -> None:
    live = current_spec(client)
    assert live["openapi"] == openapi_snapshot["openapi"]


def test_no_endpoint_disappeared(client: TestClient, openapi_snapshot: dict[str, Any]) -> None:
    live_paths = current_spec(client)["paths"]
    missing = {
        path: methods
        for path, methods in openapi_snapshot["paths"].items()
        if path not in live_paths
    }
    assert not missing, f"Endpoints removed from the API: {sorted(missing)}"


def test_no_method_removed(client: TestClient, openapi_snapshot: dict[str, Any]) -> None:
    live_paths = current_spec(client)["paths"]
    regressions: dict[str, list[str]] = {}
    for path, methods in openapi_snapshot["paths"].items():
        live_methods = set(live_paths.get(path, []))
        dropped = sorted(set(methods) - live_methods)
        if dropped:
            regressions[path] = dropped
    assert not regressions, f"HTTP methods removed: {regressions}"


def test_snapshot_is_exact(client: TestClient, openapi_snapshot: dict[str, Any]) -> None:
    """The live surface must equal the snapshot exactly.

    Additions also fail so that new endpoints are a deliberate, reviewed change
    to the committed snapshot.
    """
    live = current_spec(client)
    assert live == openapi_snapshot, (
        "OpenAPI surface drifted from the snapshot. If intended, regenerate it "
        "with `python -m scripts.update_openapi_snapshot`."
    )
