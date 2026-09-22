"""Conversa aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class ConversaRole(StrEnum):
    """Author of a conversation message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(slots=True)
class Conversa:
    """A single message exchanged with a customer."""

    cliente_id: UUID
    role: ConversaRole
    mensagem: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
