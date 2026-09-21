"""User aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class UserRole(StrEnum):
    """Roles available in the platform."""

    ADMIN = "admin"
    MANAGER = "manager"
    SALES_REP = "sales_rep"


@dataclass(slots=True)
class User:
    """A platform user able to authenticate and own leads."""

    email: str
    full_name: str
    hashed_password: str
    role: UserRole = UserRole.SALES_REP
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def deactivate(self) -> None:
        """Disable the user without deleting history."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)
