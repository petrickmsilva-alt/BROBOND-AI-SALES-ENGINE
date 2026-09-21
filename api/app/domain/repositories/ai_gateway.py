"""Port describing the AI provider used for lead qualification."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LeadScoreResult:
    """Outcome of an AI qualification run."""

    score: int
    rationale: str


class AIGateway(ABC):
    """Contract for the large-language-model provider."""

    @abstractmethod
    async def health(self) -> bool:
        """Return True when the provider is reachable."""

    @abstractmethod
    async def score_lead(self, prompt: str) -> LeadScoreResult:
        """Score a lead from a natural-language description."""
