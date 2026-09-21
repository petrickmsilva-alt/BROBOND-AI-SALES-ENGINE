"""Health-check schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

ComponentStatus = Literal["up", "down"]


class HealthResponse(BaseModel):
    """Aggregated service health."""

    status: Literal["healthy", "degraded"]
    service: str
    version: str
    environment: str
    dependencies: dict[str, ComponentStatus]
