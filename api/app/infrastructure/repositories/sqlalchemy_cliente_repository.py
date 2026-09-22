"""SQLAlchemy adapter for the cliente repository port."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.cliente import Cliente
from app.domain.repositories.cliente_repository import ClienteRepository
from app.infrastructure.models.cliente_model import ClienteModel


def _to_entity(model: ClienteModel) -> Cliente:
    return Cliente(
        id=model.id,
        nome=model.nome,
        telefone=model.telefone,
        email=model.email,
        instagram=model.instagram,
        cidade=model.cidade,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyClienteRepository(ClienteRepository):
    """Persists clientes in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, cliente: Cliente) -> Cliente:
        """Persist a new cliente."""
        model = ClienteModel(
            id=cliente.id,
            nome=cliente.nome,
            telefone=cliente.telefone,
            email=cliente.email,
            instagram=cliente.instagram,
            cidade=cliente.cidade,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, cliente: Cliente) -> Cliente:
        """Persist changes to an existing cliente."""
        model = await self._session.get(ClienteModel, cliente.id)
        if model is None:
            raise LookupError(f"Cliente {cliente.id} not found")
        model.nome = cliente.nome
        model.telefone = cliente.telefone
        model.email = cliente.email
        model.instagram = cliente.instagram
        model.cidade = cliente.cidade
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, cliente_id: UUID) -> Cliente | None:
        """Return a cliente by identifier, if present."""
        model = await self._session.get(ClienteModel, cliente_id)
        return _to_entity(model) if model else None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Cliente]:
        """Return a page of clientes."""
        result = await self._session.execute(
            select(ClienteModel)
            .order_by(ClienteModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(model) for model in result.scalars().all()]

    async def count(self) -> int:
        """Return the total number of clientes."""
        result = await self._session.execute(select(func.count()).select_from(ClienteModel))
        return int(result.scalar_one())

    async def delete(self, cliente_id: UUID) -> bool:
        """Delete a cliente, returning True when a row was removed."""
        result = await self._session.execute(
            delete(ClienteModel).where(ClienteModel.id == cliente_id)
        )
        await self._session.commit()
        return bool(result.rowcount)
