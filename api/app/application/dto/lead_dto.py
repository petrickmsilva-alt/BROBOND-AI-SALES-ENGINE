"""Lead request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.lead import LeadStatus


class LeadCreateRequest(BaseModel):
    """Payload used to register a lead."""

    cliente_id: str
    origem: str | None = Field(default=None, max_length=64)
    interesse: str | None = Field(default=None, max_length=255)
    observacao: str | None = None
    status: LeadStatus = LeadStatus.NOVO


class LeadStatusUpdateRequest(BaseModel):
    """Payload used to move a lead through the pipeline."""

    status: LeadStatus


class LeadResponse(BaseModel):
    """Public representation of a lead."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    cliente_id: str
    origem: str | None
    score: int
    status: LeadStatus
    interesse: str | None
    observacao: str | None
    created_at: datetime


class LeadListResponse(BaseModel):
    """Paginated collection of leads."""

    total: int
    items: list[LeadResponse]


class LeadScoreResponse(BaseModel):
    """Result of an AI qualification run."""

    lead_id: str
    score: int
    rationale: str
    status: LeadStatus
