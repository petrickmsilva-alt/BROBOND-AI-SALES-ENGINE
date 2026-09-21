"""Port describing user persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import User


class UserRepository(ABC):
    """Persistence contract for the User aggregate."""

    @abstractmethod
    async def add(self, user: User) -> User:
        """Persist a new user."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return a user by identifier, if present."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Return a user by email, if present."""

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[User]:
        """Return a page of users."""
