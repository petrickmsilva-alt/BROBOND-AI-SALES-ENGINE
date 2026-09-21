"""SQLAlchemy adapter for the lead repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.lead import Lead, LeadStatus
from app.domain.repositories.lead_repository import LeadRepository
from app.infrastructure.models.lead_model import LeadModel


def _to_entity(model: LeadModel) -> Lead:
    return Lead(
        id=model.id,
        name=model.name,
        email=model.email,
        company=model.company,
        phone=model.phone,
        source=model.source,
        status=LeadStatus(model.status),
        score=model.score,
        notes=model.notes,
        owner_id=model.owner_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyLeadRepository(LeadRepository):
    """Persists leads in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, lead: Lead) -> Lead:
        """Persist a new lead."""
        model = LeadModel(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            company=lead.company,
            phone=lead.phone,
            source=lead.source,
            status=lead.status.value,
            score=lead.score,
            notes=lead.notes,
            owner_id=lead.owner_id,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, lead: Lead) -> Lead:
        """Persist changes to an existing lead."""
        model = await self._session.get(LeadModel, lead.id)
        if model is None:
            raise LookupError(f"Lead {lead.id} not found")
        model.name = lead.name
        model.email = lead.email
        model.company = lead.company
        model.phone = lead.phone
        model.source = lead.source
        model.status = lead.status.value
        model.score = lead.score
        model.notes = lead.notes
        model.owner_id = lead.owner_id
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, lead_id: UUID) -> Lead | None:
        """Return a lead by identifier, if present."""
        model = await self._session.get(LeadModel, lead_id)
        return _to_entity(model) if model else None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Lead]:
        """Return a page of leads."""
        result = await self._session.execute(
            select(LeadModel).order_by(LeadModel.created_at.desc()).limit(limit).offset(offset)
        )
        return [_to_entity(model) for model in result.scalars().all()]
