"""Dashboard request/response schemas."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class PipelineResponse(BaseModel):
    """Lead counts per pipeline stage."""

    novo: int
    contato: int
    negociacao: int
    proposta: int
    fechado: int
    perdido: int


class DashboardSummaryResponse(BaseModel):
    """High-level CRM metrics for the dashboard."""

    clientes: int
    produtos: int
    leads: int
    vendas: int
    receita: Decimal
    pipeline: PipelineResponse
