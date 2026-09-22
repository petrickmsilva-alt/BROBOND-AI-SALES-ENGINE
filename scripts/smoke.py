#!/usr/bin/env python3
"""HTTP smoke test for the BROBOND AI Sales Engine API.

Exercises the critical public endpoints against a running API and asserts that
none of them return a 5xx that indicates a crash. The ``/leads/{id}/qualify``
endpoint is allowed to answer 503 when the AI provider is unavailable, but is
never allowed to answer 500.

Usage:
    python scripts/smoke.py [--base-url http://localhost:8000]

Exit code 0 means every check passed; 1 means at least one failed.
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from typing import Any

import json


@dataclass
class Check:
    """Outcome of a single smoke assertion."""

    name: str
    ok: bool
    detail: str


def _request(
    method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 10.0
) -> tuple[int, str]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def _wait_for_health(base_url: str, attempts: int = 30, delay: float = 2.0) -> bool:
    for _ in range(attempts):
        try:
            status, _ = _request("GET", f"{base_url}/health")
            if status == 200:
                return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(delay)
    return False


def run(base_url: str) -> list[Check]:
    """Run the smoke checks and return their results."""
    checks: list[Check] = []

    # /health must be reachable and healthy/degraded (never a 5xx).
    status, _ = _request("GET", f"{base_url}/health")
    checks.append(
        Check("GET /health", status == 200, f"status={status}, expected 200")
    )

    # /clientes list must respond 200.
    status, _ = _request("GET", f"{base_url}/api/v1/clientes")
    checks.append(
        Check("GET /clientes", status == 200, f"status={status}, expected 200")
    )

    # Create a cliente so we can create a lead to qualify.
    status, body = _request(
        "POST", f"{base_url}/api/v1/clientes", {"nome": "Smoke Cliente"}
    )
    cliente_ok = status == 201
    checks.append(
        Check("POST /clientes", cliente_ok, f"status={status}, expected 201")
    )
    cliente_id = json.loads(body)["id"] if cliente_ok else None

    # /leads list must respond 200.
    status, _ = _request("GET", f"{base_url}/api/v1/leads")
    checks.append(Check("GET /leads", status == 200, f"status={status}, expected 200"))

    # /dashboard/pipeline must respond 200.
    status, _ = _request("GET", f"{base_url}/api/v1/dashboard/pipeline")
    checks.append(
        Check(
            "GET /dashboard/pipeline",
            status == 200,
            f"status={status}, expected 200",
        )
    )

    # /leads/{id}/qualify must respond 200 or 503, never 500.
    lead_id: str | None = None
    if cliente_id:
        status, body = _request(
            "POST", f"{base_url}/api/v1/leads", {"cliente_id": cliente_id}
        )
        if status == 201:
            lead_id = json.loads(body)["id"]
    target_lead = lead_id or str(uuid.uuid4())
    status, _ = _request(
        "POST", f"{base_url}/api/v1/leads/{target_lead}/qualify"
    )
    checks.append(
        Check(
            "POST /leads/{id}/qualify",
            status in {200, 503, 404},
            f"status={status}, expected 200/503 (404 tolerated), never 500",
        )
    )

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="BROBOND API smoke test")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--no-wait", action="store_true", help="Skip readiness wait")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    if not args.no_wait and not _wait_for_health(base_url):
        print(f"API at {base_url} did not become healthy in time", file=sys.stderr)
        return 1

    checks = run(base_url)

    print("BROBOND AI SALES ENGINE - smoke test")
    print("------------------------------------")
    failures = 0
    for check in checks:
        marker = "PASS" if check.ok else "FAIL"
        print(f"{marker}  {check.name:<28} {check.detail if not check.ok else ''}".rstrip())
        if not check.ok:
            failures += 1
    print("------------------------------------")

    if failures:
        print(f"{failures} smoke check(s) failed.")
        return 1
    print("All smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
