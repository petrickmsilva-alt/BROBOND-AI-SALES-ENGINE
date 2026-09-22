"""Use cases for lead management and AI qualification."""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import EntityNotFoundError
from app.domain.entities.lead import Lead, LeadStatus
from app.domain.repositories.ai_gateway import AIGateway
from app.domain.repositories.cliente_repository import ClienteRepository
from app.domain.repositories.lead_repository import LeadRepository


class LeadService:
    """Coordinates lead persistence, pipeline transitions and scoring."""

    def __init__(
        self,
        leads: LeadRepository,
        clientes: ClienteRepository,
        ai_gateway: AIGateway,
    ) -> None:
        self._leads = leads
        self._clientes = clientes
        self._ai = ai_gateway

    async def create(
        self,
        cliente_id: UUID,
        origem: str | None = None,
        interesse: str | None = None,
        observacao: str | None = None,
        status: LeadStatus = LeadStatus.NOVO,
    ) -> Lead:
        """Register a new lead for an existing cliente."""
        if await self._clientes.get_by_id(cliente_id) is None:
            raise EntityNotFoundError(f"Cliente {cliente_id} not found")
        lead = Lead(
            cliente_id=cliente_id,
            origem=origem,
            interesse=interesse,
            observacao=observacao,
            status=status,
        )
        return await self._leads.add(lead)

    async def list_leads(self, limit: int = 50, offset: int = 0) -> tuple[list[Lead], int]:
        """Return a page of leads and the total count."""
        items = await self._leads.list_all(limit=limit, offset=offset)
        total = await self._leads.count()
        return items, total

    async def get(self, lead_id: UUID) -> Lead:
        """Return a lead or raise when missing."""
        lead = await self._leads.get_by_id(lead_id)
        if lead is None:
            raise EntityNotFoundError(f"Lead {lead_id} not found")
        return lead

    async def change_status(self, lead_id: UUID, status: LeadStatus) -> Lead:
        """Move a lead to a new pipeline stage."""
        lead = await self.get(lead_id)
        lead.change_status(status)
        return await self._leads.update(lead)

    async def qualify(self, lead_id: UUID) -> Lead:
        """Score a lead with the AI gateway and persist the result."""
        lead = await self.get(lead_id)
        cliente = await self._clientes.get_by_id(lead.cliente_id)
        prompt = (
            f"Cliente: {cliente.nome if cliente else 'unknown'}\n"
            f"Cidade: {cliente.cidade if cliente else 'unknown'}\n"
            f"Origem: {lead.origem or 'unknown'}\n"
            f"Interesse: {lead.interesse or 'unknown'}"
        )
        result = await self._ai.score_lead(prompt)
        lead.apply_score(result.score, result.rationale)
        return await self._leads.update(lead)
