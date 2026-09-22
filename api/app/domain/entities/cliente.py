"""Cliente aggregate.

A ``Cliente`` is the central entity of the CRM: every lead, conversation and
sale hangs off a customer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class Cliente:
    """A customer tracked by the sales engine."""

    nome: str
    telefone: str | None = None
    email: str | None = None
    instagram: str | None = None
    cidade: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        """Mark the aggregate as modified."""
        self.updated_at = datetime.now(UTC)
