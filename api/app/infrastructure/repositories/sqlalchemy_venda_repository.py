"""SQLAlchemy adapter for the venda repository port."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.venda import MetodoPagamento, Venda, VendaStatus
from app.domain.repositories.venda_repository import VendaRepository
from app.infrastructure.models.venda_model import VendaModel


def _to_entity(model: VendaModel) -> Venda:
    return Venda(
        id=model.id,
        cliente_id=model.cliente_id,
        valor=model.valor,
        metodo_pagamento=MetodoPagamento(model.metodo_pagamento),
        status=VendaStatus(model.status),
        created_at=model.created_at,
    )


class SQLAlchemyVendaRepository(VendaRepository):
    """Persists vendas in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, venda: Venda) -> Venda:
        """Persist a new venda."""
        model = VendaModel(
            id=venda.id,
            cliente_id=venda.cliente_id,
            valor=venda.valor,
            metodo_pagamento=venda.metodo_pagamento.value,
            status=venda.status.value,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def get_by_id(self, venda_id: UUID) -> Venda | None:
        """Return a venda by identifier, if present."""
        model = await self._session.get(VendaModel, venda_id)
        return _to_entity(model) if model else None

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Venda]:
        """Return a page of vendas."""
        result = await self._session.execute(
            select(VendaModel).order_by(VendaModel.created_at.desc()).limit(limit).offset(offset)
        )
        return [_to_entity(model) for model in result.scalars().all()]

    async def count(self) -> int:
        """Return the total number of vendas."""
        result = await self._session.execute(select(func.count()).select_from(VendaModel))
        return int(result.scalar_one())

    async def total_revenue(self) -> Decimal:
        """Return the summed value of all paid sales."""
        result = await self._session.execute(
            select(func.coalesce(func.sum(VendaModel.valor), 0)).where(
                VendaModel.status == VendaStatus.PAGO.value
            )
        )
        return Decimal(str(result.scalar_one()))
