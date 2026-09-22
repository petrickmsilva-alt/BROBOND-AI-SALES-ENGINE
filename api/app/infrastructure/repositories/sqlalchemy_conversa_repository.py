"""SQLAlchemy adapter for the conversa repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.conversa import Conversa, ConversaRole
from app.domain.repositories.conversa_repository import ConversaRepository
from app.infrastructure.models.conversa_model import ConversaModel


def _to_entity(model: ConversaModel) -> Conversa:
    return Conversa(
        id=model.id,
        cliente_id=model.cliente_id,
        role=ConversaRole(model.role),
        mensagem=model.mensagem,
        created_at=model.created_at,
    )


class SQLAlchemyConversaRepository(ConversaRepository):
    """Persists conversas in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, conversa: Conversa) -> Conversa:
        """Persist a new conversa message."""
        model = ConversaModel(
            id=conversa.id,
            cliente_id=conversa.cliente_id,
            role=conversa.role.value,
            mensagem=conversa.mensagem,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_by_cliente(self, cliente_id: UUID, limit: int = 100) -> list[Conversa]:
        """Return the message history for a cliente."""
        result = await self._session.execute(
            select(ConversaModel)
            .where(ConversaModel.cliente_id == cliente_id)
            .order_by(ConversaModel.created_at)
            .limit(limit)
        )
        return [_to_entity(model) for model in result.scalars().all()]

    async def count(self) -> int:
        """Return the total number of conversa messages."""
        result = await self._session.execute(select(func.count()).select_from(ConversaModel))
        return int(result.scalar_one())
