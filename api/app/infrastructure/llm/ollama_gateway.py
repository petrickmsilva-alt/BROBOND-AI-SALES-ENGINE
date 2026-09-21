"""Ollama adapter implementing the AI gateway port."""

from __future__ import annotations

import json
import logging
import re

import httpx

from app.core.config import Settings, get_settings
from app.domain.repositories.ai_gateway import AIGateway, LeadScoreResult

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a B2B sales qualification assistant. "
    'Reply strictly with JSON: {"score": <0-100 integer>, "rationale": "<one sentence>"}.'
)


class OllamaGateway(AIGateway):
    """Talks to a local Ollama server."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def health(self) -> bool:
        """Return True when Ollama answers its tags endpoint."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self._settings.ollama_base_url}/api/tags")
            return response.status_code == httpx.codes.OK
        except httpx.HTTPError as exc:
            logger.warning("Ollama health check failed: %s", exc)
            return False

    async def score_lead(self, prompt: str) -> LeadScoreResult:
        """Score a lead using the configured model."""
        payload = {
            "model": self._settings.ollama_model,
            "prompt": f"{_SYSTEM_PROMPT}\n\nLead:\n{prompt}",
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=self._settings.ollama_timeout_seconds) as client:
            response = await client.post(
                f"{self._settings.ollama_base_url}/api/generate", json=payload
            )
            response.raise_for_status()
        raw = str(response.json().get("response", ""))
        return _parse_score(raw)


def _parse_score(raw: str) -> LeadScoreResult:
    """Extract a score payload from a model completion."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            score = int(data.get("score", 0))
            rationale = str(data.get("rationale", "")).strip()
            return LeadScoreResult(score=max(0, min(100, score)), rationale=rationale or raw[:280])
        except (ValueError, TypeError):
            logger.warning("Could not parse Ollama JSON payload")
    return LeadScoreResult(score=0, rationale=raw[:280] or "No response from model")
