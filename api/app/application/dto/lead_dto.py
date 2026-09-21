"""Lead request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.entities.lead import LeadStatus


class LeadCreateRequest(BaseModel):
    """Payload used to register a lead."""

    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    company: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    source: str | None = Field(default=None, max_length=64)


class LeadResponse(BaseModel):
    """Public representation of a lead."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    company: str | None
    phone: str | None
    source: str | None
    status: LeadStatus
    score: int
    notes: str | None
    created_at: datetime


class LeadScoreResponse(BaseModel):
    """Result of an AI qualification run."""

    lead_id: str
    score: int
    rationale: str
    status: LeadStatus
