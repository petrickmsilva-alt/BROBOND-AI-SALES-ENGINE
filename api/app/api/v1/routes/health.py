"""Health endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import HealthServiceDep
from app.application.dto.health_dto import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Service and dependency health")
async def health(service: HealthServiceDep) -> HealthResponse:
    """Return the health of the API and its downstream dependencies."""
    return await service.check()
