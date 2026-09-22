"""Port describing produto persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.produto import Produto


class ProdutoRepository(ABC):
    """Persistence contract for the Produto aggregate."""

    @abstractmethod
    async def add(self, produto: Produto) -> Produto:
        """Persist a new produto."""

    @abstractmethod
    async def update(self, produto: Produto) -> Produto:
        """Persist changes to an existing produto."""

    @abstractmethod
    async def get_by_id(self, produto_id: UUID) -> Produto | None:
        """Return a produto by identifier, if present."""

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Produto | None:
        """Return a produto by its SKU, if present."""

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Produto]:
        """Return a page of produtos."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of produtos."""

    @abstractmethod
    async def delete(self, produto_id: UUID) -> bool:
        """Delete a produto, returning True when a row was removed."""
