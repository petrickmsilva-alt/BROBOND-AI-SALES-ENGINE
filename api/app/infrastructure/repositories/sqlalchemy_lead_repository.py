"""SQLAlchemy adapter for the lead repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.lead import Lead, LeadStatus
from app.domain.repositories.lead_repository import LeadRepository
from app.infrastructure.models.lead_model import LeadModel


def _to_entity(model: LeadModel) -> Lead:
    return Lead(
        id=model.id,
        cliente_id=model.cliente_id,
        origem=model.origem,
        score=model.score,
        status=LeadStatus(model.status),
        interesse=model.interesse,
        observacao=model.observacao,
        created_at=model.created_at,
    )


class SQLAlchemyLeadRepository(LeadRepository):
    """Persists leads in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, lead: Lead) -> Lead:
        """Persist a new lead."""
        model = LeadModel(
            id=lead.id,
            cliente_id=lead.cliente_id,
            origem=lead.origem,
            score=lead.score,
            status=lead.status.value,
            interesse=lead.interesse,
            observacao=lead.observacao,
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
        model.cliente_id = lead.cliente_id
        model.origem = lead.origem
        model.score = lead.score
        model.status = lead.status.value
        model.interesse = lead.interesse
        model.observacao = lead.observacao
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

    async def count(self) -> int:
        """Return the total number of leads."""
        result = await self._session.execute(select(func.count()).select_from(LeadModel))
        return int(result.scalar_one())

    async def count_by_status(self) -> dict[LeadStatus, int]:
        """Return the number of leads grouped by pipeline status."""
        result = await self._session.execute(
            select(LeadModel.status, func.count()).group_by(LeadModel.status)
        )
        counts = {status: 0 for status in LeadStatus}
        for raw_status, total in result.all():
            counts[LeadStatus(raw_status)] = int(total)
        return counts

    async def delete(self, lead_id: UUID) -> bool:
        """Delete a lead, returning True when a row was removed."""
        result = await self._session.execute(delete(LeadModel).where(LeadModel.id == lead_id))
        await self._session.commit()
        return bool(result.rowcount)
