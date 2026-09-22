"""Port describing venda persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.domain.entities.venda import Venda


class VendaRepository(ABC):
    """Persistence contract for the Venda aggregate."""

    @abstractmethod
    async def add(self, venda: Venda) -> Venda:
        """Persist a new venda."""

    @abstractmethod
    async def get_by_id(self, venda_id: UUID) -> Venda | None:
        """Return a venda by identifier, if present."""

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Venda]:
        """Return a page of vendas."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of vendas."""

    @abstractmethod
    async def total_revenue(self) -> Decimal:
        """Return the summed value of all paid sales."""
