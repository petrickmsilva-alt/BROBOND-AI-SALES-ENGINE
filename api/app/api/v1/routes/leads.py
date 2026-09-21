"""Lead endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUserDep, LeadServiceDep
from app.application.dto.lead_dto import LeadCreateRequest, LeadResponse, LeadScoreResponse
from app.core.exceptions import EntityNotFoundError
from app.domain.entities.lead import Lead

router = APIRouter(prefix="/leads", tags=["leads"])


def _to_response(lead: Lead) -> LeadResponse:
    return LeadResponse(
        id=str(lead.id),
        name=lead.name,
        email=lead.email,
        company=lead.company,
        phone=lead.phone,
        source=lead.source,
        status=lead.status,
        score=lead.score,
        notes=lead.notes,
        created_at=lead.created_at,
    )


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a lead",
)
async def create_lead(
    payload: LeadCreateRequest, service: LeadServiceDep, current_user: CurrentUserDep
) -> LeadResponse:
    """Register a new lead owned by the current user."""
    lead = await service.create(
        name=payload.name,
        email=str(payload.email),
        company=payload.company,
        phone=payload.phone,
        source=payload.source,
        owner_id=current_user.id,
    )
    return _to_response(lead)


@router.get("", response_model=list[LeadResponse], summary="List leads")
async def list_leads(
    service: LeadServiceDep,
    current_user: CurrentUserDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[LeadResponse]:
    """Return a page of leads."""
    leads = await service.list_leads(limit=limit, offset=offset)
    return [_to_response(lead) for lead in leads]


@router.post(
    "/{lead_id}/qualify",
    response_model=LeadScoreResponse,
    summary="Qualify a lead with the AI engine",
)
async def qualify_lead(
    lead_id: UUID, service: LeadServiceDep, current_user: CurrentUserDep
) -> LeadScoreResponse:
    """Score the lead using Ollama and persist the outcome."""
    try:
        lead = await service.qualify(lead_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return LeadScoreResponse(
        lead_id=str(lead.id),
        score=lead.score,
        rationale=lead.notes or "",
        status=lead.status,
    )
