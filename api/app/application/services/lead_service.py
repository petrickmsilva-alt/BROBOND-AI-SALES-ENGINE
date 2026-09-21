"""Use cases for lead management and AI qualification."""

from __future__ import annotations

from uuid import UUID

from app.core.exceptions import EntityNotFoundError
from app.domain.entities.lead import Lead
from app.domain.repositories.ai_gateway import AIGateway
from app.domain.repositories.lead_repository import LeadRepository


class LeadService:
    """Coordinates lead persistence and scoring."""

    def __init__(self, leads: LeadRepository, ai_gateway: AIGateway) -> None:
        self._leads = leads
        self._ai = ai_gateway

    async def create(
        self,
        name: str,
        email: str,
        company: str | None = None,
        phone: str | None = None,
        source: str | None = None,
        owner_id: UUID | None = None,
    ) -> Lead:
        """Register a new lead."""
        lead = Lead(
            name=name, email=email, company=company, phone=phone, source=source, owner_id=owner_id
        )
        return await self._leads.add(lead)

    async def list_leads(self, limit: int = 50, offset: int = 0) -> list[Lead]:
        """Return a page of leads."""
        return await self._leads.list_all(limit=limit, offset=offset)

    async def get(self, lead_id: UUID) -> Lead:
        """Return a lead or raise when missing."""
        lead = await self._leads.get_by_id(lead_id)
        if lead is None:
            raise EntityNotFoundError(f"Lead {lead_id} not found")
        return lead

    async def qualify(self, lead_id: UUID) -> Lead:
        """Score a lead with the AI gateway and persist the result."""
        lead = await self.get(lead_id)
        prompt = (
            f"Name: {lead.name}\n"
            f"Email: {lead.email}\n"
            f"Company: {lead.company or 'unknown'}\n"
            f"Source: {lead.source or 'unknown'}"
        )
        result = await self._ai.score_lead(prompt)
        lead.apply_score(result.score, result.rationale)
        return await self._leads.update(lead)
