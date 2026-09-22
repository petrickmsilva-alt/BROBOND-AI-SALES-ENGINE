"""Lead endpoints."""

from __future__ import annotations

import logging
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import LeadServiceDep
from app.application.dto.lead_dto import (
    LeadCreateRequest,
    LeadListResponse,
    LeadResponse,
    LeadScoreResponse,
    LeadStatusUpdateRequest,
)
from app.core.exceptions import EntityNotFoundError
from app.domain.entities.lead import Lead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["leads"])


def _to_response(lead: Lead) -> LeadResponse:
    return LeadResponse(
        id=str(lead.id),
        cliente_id=str(lead.cliente_id),
        origem=lead.origem,
        score=lead.score,
        status=lead.status,
        interesse=lead.interesse,
        observacao=lead.observacao,
        created_at=lead.created_at,
    )


@router.get("", response_model=LeadListResponse, summary="List leads")
async def list_leads(
    service: LeadServiceDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> LeadListResponse:
    """Return a page of leads."""
    items, total = await service.list_leads(limit=limit, offset=offset)
    return LeadListResponse(total=total, items=[_to_response(lead) for lead in items])


@router.get("/{lead_id}", response_model=LeadResponse, summary="Get a lead")
async def get_lead(lead_id: UUID, service: LeadServiceDep) -> LeadResponse:
    """Return a single lead."""
    try:
        lead = await service.get(lead_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(lead)


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a lead",
)
async def create_lead(payload: LeadCreateRequest, service: LeadServiceDep) -> LeadResponse:
    """Register a new lead for an existing cliente."""
    try:
        lead = await service.create(
            cliente_id=UUID(payload.cliente_id),
            origem=payload.origem,
            interesse=payload.interesse,
            observacao=payload.observacao,
            status=payload.status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid cliente_id"
        ) from exc
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(lead)


@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse,
    summary="Move a lead through the pipeline",
)
async def update_lead_status(
    lead_id: UUID, payload: LeadStatusUpdateRequest, service: LeadServiceDep
) -> LeadResponse:
    """Update the pipeline status of a lead."""
    try:
        lead = await service.change_status(lead_id, payload.status)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(lead)


@router.post(
    "/{lead_id}/qualify",
    response_model=LeadScoreResponse,
    summary="Qualify a lead with the AI engine",
)
async def qualify_lead(lead_id: UUID, service: LeadServiceDep) -> LeadScoreResponse:
    """Score the lead using Ollama and persist the outcome.

    Returns 404 when the lead is unknown and 503 when the AI provider is
    unreachable, never a 500.
    """
    try:
        lead = await service.qualify(lead_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Lead qualification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI qualification provider is unavailable",
        ) from exc
    return LeadScoreResponse(
        lead_id=str(lead.id),
        score=lead.score,
        rationale=lead.observacao or "",
        status=lead.status,
    )
