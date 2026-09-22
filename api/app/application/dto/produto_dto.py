"""Produto request/response schemas."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoCreateRequest(BaseModel):
    """Payload used to register a produto."""

    sku: str = Field(min_length=1, max_length=64)
    nome: str = Field(min_length=1, max_length=255)
    descricao: str | None = None
    categoria: str | None = Field(default=None, max_length=128)
    cor: str | None = Field(default=None, max_length=64)
    tamanho: str | None = Field(default=None, max_length=32)
    preco: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    estoque: int = Field(default=0, ge=0)
    ativo: bool = True


class ProdutoUpdateRequest(BaseModel):
    """Payload used to patch a produto. All fields optional."""

    sku: str | None = Field(default=None, min_length=1, max_length=64)
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    descricao: str | None = None
    categoria: str | None = Field(default=None, max_length=128)
    cor: str | None = Field(default=None, max_length=64)
    tamanho: str | None = Field(default=None, max_length=32)
    preco: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    estoque: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class ProdutoResponse(BaseModel):
    """Public representation of a produto."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    sku: str
    nome: str
    descricao: str | None
    categoria: str | None
    cor: str | None
    tamanho: str | None
    preco: Decimal
    estoque: int
    ativo: bool


class ProdutoListResponse(BaseModel):
    """Paginated collection of produtos."""

    total: int
    items: list[ProdutoResponse]
