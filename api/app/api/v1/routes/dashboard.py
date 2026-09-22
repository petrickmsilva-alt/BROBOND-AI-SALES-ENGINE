"""Dashboard endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import DashboardServiceDep
from app.application.dto.dashboard_dto import DashboardSummaryResponse, PipelineResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/pipeline", response_model=PipelineResponse, summary="Lead pipeline counts")
async def pipeline(service: DashboardServiceDep) -> PipelineResponse:
    """Return the number of leads per pipeline stage."""
    return await service.pipeline()


@router.get("/summary", response_model=DashboardSummaryResponse, summary="CRM metrics summary")
async def summary(service: DashboardServiceDep) -> DashboardSummaryResponse:
    """Return an aggregate overview of the CRM."""
    return await service.summary()
