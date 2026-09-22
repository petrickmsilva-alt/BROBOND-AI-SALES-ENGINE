"""Port describing cliente persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.cliente import Cliente


class ClienteRepository(ABC):
    """Persistence contract for the Cliente aggregate."""

    @abstractmethod
    async def add(self, cliente: Cliente) -> Cliente:
        """Persist a new cliente."""

    @abstractmethod
    async def update(self, cliente: Cliente) -> Cliente:
        """Persist changes to an existing cliente."""

    @abstractmethod
    async def get_by_id(self, cliente_id: UUID) -> Cliente | None:
        """Return a cliente by identifier, if present."""

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Cliente]:
        """Return a page of clientes."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of clientes."""

    @abstractmethod
    async def delete(self, cliente_id: UUID) -> bool:
        """Delete a cliente, returning True when a row was removed."""
