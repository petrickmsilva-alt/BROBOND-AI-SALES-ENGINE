"""Regenerate the committed OpenAPI snapshot.

Run with ``python -m scripts.update_openapi_snapshot`` from the ``api``
directory. Only run this when an API change to the public surface is
intentional; the contract test-suite compares against the committed file.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.main import create_app

_SNAPSHOT_PATH = (
    Path(__file__).resolve().parent.parent / "tests" / "contracts" / ("openapi_snapshot.json")
)


def build_paths() -> dict[str, list[str]]:
    """Return the stable path -> sorted-methods map exposed by the API."""
    app = create_app()
    spec = app.openapi()
    return {
        path: sorted(method.upper() for method in methods)
        for path, methods in sorted(spec["paths"].items())
    }


def build_snapshot() -> dict[str, object]:
    """Return the stable OpenAPI snapshot representation."""
    app = create_app()
    return {"openapi": app.openapi().get("openapi"), "paths": build_paths()}


def main() -> None:
    paths = build_paths()
    snapshot: dict[str, object] = {"openapi": create_app().openapi().get("openapi"), "paths": paths}
    with _SNAPSHOT_PATH.open("w") as handle:
        json.dump(snapshot, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"Wrote {_SNAPSHOT_PATH} with {len(paths)} paths")


if __name__ == "__main__":
    main()
