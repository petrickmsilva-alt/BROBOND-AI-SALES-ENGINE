"""Lead aggregate.

A lead represents an opportunity attached to a :class:`Cliente`. Leads move
through the sales pipeline and can be scored by the AI qualification engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class LeadStatus(StrEnum):
    """Pipeline stages of a sales lead."""

    NOVO = "novo"
    CONTATO = "contato"
    NEGOCIACAO = "negociacao"
    PROPOSTA = "proposta"
    FECHADO = "fechado"
    PERDIDO = "perdido"


@dataclass(slots=True)
class Lead:
    """A sales opportunity tied to a customer."""

    cliente_id: UUID
    origem: str | None = None
    score: int = 0
    status: LeadStatus = LeadStatus.NOVO
    interesse: str | None = None
    observacao: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def change_status(self, status: LeadStatus) -> None:
        """Move the lead to a new pipeline stage."""
        self.status = status

    def apply_score(self, score: int, observacao: str | None = None) -> None:
        """Apply an AI-generated qualification score to the lead."""
        if not 0 <= score <= 100:
            raise ValueError("Lead score must be between 0 and 100")
        self.score = score
        self.observacao = observacao or self.observacao
        if self.status is LeadStatus.NOVO and score >= 50:
            self.status = LeadStatus.CONTATO
