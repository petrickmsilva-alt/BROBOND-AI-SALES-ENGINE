"""Use cases powering the CRM dashboard."""

from __future__ import annotations

from app.application.dto.dashboard_dto import DashboardSummaryResponse, PipelineResponse
from app.domain.entities.lead import LeadStatus
from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.repositories.lead_repository import LeadRepository
from app.domain.repositories.produto_repository import ProdutoRepository
from app.domain.repositories.venda_repository import VendaRepository


class DashboardService:
    """Aggregates CRM metrics for reporting."""

    def __init__(
        self,
        clientes: ClienteRepository,
        produtos: ProdutoRepository,
        leads: LeadRepository,
        vendas: VendaRepository,
    ) -> None:
        self._clientes = clientes
        self._produtos = produtos
        self._leads = leads
        self._vendas = vendas

    async def pipeline(self) -> PipelineResponse:
        """Return the number of leads per pipeline stage."""
        counts = await self._leads.count_by_status()
        return PipelineResponse(
            novo=counts.get(LeadStatus.NOVO, 0),
            contato=counts.get(LeadStatus.CONTATO, 0),
            negociacao=counts.get(LeadStatus.NEGOCIACAO, 0),
            proposta=counts.get(LeadStatus.PROPOSTA, 0),
            fechado=counts.get(LeadStatus.FECHADO, 0),
            perdido=counts.get(LeadStatus.PERDIDO, 0),
        )

    async def summary(self) -> DashboardSummaryResponse:
        """Return an aggregate overview of the CRM."""
        return DashboardSummaryResponse(
            clientes=await self._clientes.count(),
            produtos=await self._produtos.count(),
            leads=await self._leads.count(),
            vendas=await self._vendas.count(),
            receita=await self._vendas.total_revenue(),
            pipeline=await self.pipeline(),
        )
