"""JWT creation/validation and password hashing helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import bcrypt
import jwt
from jwt import PyJWTError

from app.core.config import Settings, get_settings

TokenType = Literal["access", "refresh"]

_MAX_PASSWORD_BYTES = 72


class TokenError(Exception):
    """Raised when a JWT cannot be decoded or is of an unexpected type."""


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    digest = bcrypt.hashpw(_encode(plain_password), bcrypt.gensalt())
    return digest.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(_encode(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_token(
    subject: str,
    token_type: TokenType = "access",
    settings: Settings | None = None,
) -> str:
    """Create a signed JWT for the given subject."""
    config = settings or get_settings()
    lifetime = (
        config.jwt_access_token_expire_minutes
        if token_type == "access"
        else config.jwt_refresh_token_expire_minutes
    )
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=lifetime)).timestamp()),
    }
    return jwt.encode(payload, config.jwt_secret_key, algorithm=config.jwt_algorithm)


def decode_token(
    token: str,
    expected_type: TokenType = "access",
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Decode and validate a JWT, returning its claims."""
    config = settings or get_settings()
    try:
        claims: dict[str, Any] = jwt.decode(
            token, config.jwt_secret_key, algorithms=[config.jwt_algorithm]
        )
    except PyJWTError as exc:
        raise TokenError("Invalid or expired token") from exc

    if claims.get("type") != expected_type:
        raise TokenError(f"Expected a {expected_type} token")
    return claims


def _encode(password: str) -> bytes:
    """Encode a password to bcrypt's 72-byte input limit."""
    return password.encode("utf-8")[:_MAX_PASSWORD_BYTES]
