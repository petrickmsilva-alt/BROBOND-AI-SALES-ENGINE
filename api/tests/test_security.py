"""Security helper tests."""

import pytest

from app.core.security import (
    TokenError,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_round_trip() -> None:
    hashed = hash_password("supersecret123")
    assert verify_password("supersecret123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_token_round_trip() -> None:
    token = create_token("user-1", "access")
    claims = decode_token(token, "access")
    assert claims["sub"] == "user-1"


def test_token_type_mismatch() -> None:
    token = create_token("user-1", "refresh")
    with pytest.raises(TokenError):
        decode_token(token, "access")
