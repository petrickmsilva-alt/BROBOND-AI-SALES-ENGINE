"""Lead aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class LeadStatus(StrEnum):
    """Lifecycle stages of a sales lead."""

    NEW = "new"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    WON = "won"
    LOST = "lost"


@dataclass(slots=True)
class Lead:
    """A prospective customer tracked by the sales engine."""

    name: str
    email: str
    company: str | None = None
    phone: str | None = None
    source: str | None = None
    status: LeadStatus = LeadStatus.NEW
    score: int = 0
    notes: str | None = None
    owner_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def apply_score(self, score: int, notes: str | None = None) -> None:
        """Apply an AI-generated qualification score to the lead."""
        if not 0 <= score <= 100:
            raise ValueError("Lead score must be between 0 and 100")
        self.score = score
        self.notes = notes or self.notes
        self.status = LeadStatus.QUALIFIED if score >= 50 else self.status
        self.updated_at = datetime.now(UTC)
