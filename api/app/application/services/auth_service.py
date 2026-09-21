"""Use cases for authentication and account creation."""

from __future__ import annotations

from app.core.exceptions import AuthenticationError, EntityAlreadyExistsError
from app.core.security import create_token, hash_password, verify_password
from app.domain.entities.user import User, UserRole
from app.domain.repositories.user_repository import UserRepository


class AuthService:
    """Coordinates registration and login."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def register(
        self, email: str, full_name: str, password: str, role: UserRole = UserRole.SALES_REP
    ) -> User:
        """Create a new account, rejecting duplicate emails."""
        if await self._users.get_by_email(email) is not None:
            raise EntityAlreadyExistsError(f"User {email} already exists")
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=role,
        )
        return await self._users.add(user)

    async def authenticate(self, email: str, password: str) -> tuple[str, str]:
        """Validate credentials and return an (access, refresh) token pair."""
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("User is inactive")
        return create_token(str(user.id), "access"), create_token(str(user.id), "refresh")
