"""Port describing lead persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.lead import Lead


class LeadRepository(ABC):
    """Persistence contract for the Lead aggregate."""

    @abstractmethod
    async def add(self, lead: Lead) -> Lead:
        """Persist a new lead."""

    @abstractmethod
    async def update(self, lead: Lead) -> Lead:
        """Persist changes to an existing lead."""

    @abstractmethod
    async def get_by_id(self, lead_id: UUID) -> Lead | None:
        """Return a lead by identifier, if present."""

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Lead]:
        """Return a page of leads."""
