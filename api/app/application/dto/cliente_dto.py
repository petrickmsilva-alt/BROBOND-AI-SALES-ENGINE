"""Cliente request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteCreateRequest(BaseModel):
    """Payload used to register a cliente."""

    nome: str = Field(min_length=2, max_length=255)
    telefone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    instagram: str | None = Field(default=None, max_length=128)
    cidade: str | None = Field(default=None, max_length=128)


class ClienteUpdateRequest(BaseModel):
    """Payload used to patch a cliente. All fields optional."""

    nome: str | None = Field(default=None, min_length=2, max_length=255)
    telefone: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    instagram: str | None = Field(default=None, max_length=128)
    cidade: str | None = Field(default=None, max_length=128)


class ClienteResponse(BaseModel):
    """Public representation of a cliente."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    telefone: str | None
    email: str | None
    instagram: str | None
    cidade: str | None
    created_at: datetime
    updated_at: datetime


class ClienteListResponse(BaseModel):
    """Paginated collection of clientes."""

    total: int
    items: list[ClienteResponse]
