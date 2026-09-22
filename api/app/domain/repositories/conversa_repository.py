"""Port describing conversa persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.conversa import Conversa


class ConversaRepository(ABC):
    """Persistence contract for the Conversa aggregate."""

    @abstractmethod
    async def add(self, conversa: Conversa) -> Conversa:
        """Persist a new conversa message."""

    @abstractmethod
    async def list_by_cliente(self, cliente_id: UUID, limit: int = 100) -> list[Conversa]:
        """Return the message history for a cliente."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of conversa messages."""
