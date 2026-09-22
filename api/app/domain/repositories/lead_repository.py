"""Port describing lead persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.lead import Lead, LeadStatus


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

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of leads."""

    @abstractmethod
    async def count_by_status(self) -> dict[LeadStatus, int]:
        """Return the number of leads grouped by pipeline status."""

    @abstractmethod
    async def delete(self, lead_id: UUID) -> bool:
        """Delete a lead, returning True when a row was removed."""
