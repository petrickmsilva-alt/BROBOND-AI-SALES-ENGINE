"""Tests for infrastructure helpers: GUID type and user repository paths."""

from __future__ import annotations

import uuid

import pytest

from app.domain.entities.user import User, UserRole
from app.infrastructure.db.types import GUID
from app.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


class _SqliteDialect:
    name = "sqlite"

    def type_descriptor(self, value: object) -> object:
        return value


class _PgDialect:
    name = "postgresql"

    def type_descriptor(self, value: object) -> object:
        return value


def test_guid_bind_and_result_sqlite() -> None:
    guid = GUID()
    dialect = _SqliteDialect()
    value = uuid.uuid4()
    stored = guid.process_bind_param(value, dialect)
    assert stored == value.hex
    restored = guid.process_result_value(stored, dialect)
    assert restored == value
    assert guid.process_bind_param(None, dialect) is None
    assert guid.process_result_value(None, dialect) is None


def test_guid_bind_from_string_sqlite() -> None:
    guid = GUID()
    dialect = _SqliteDialect()
    value = uuid.uuid4()
    assert guid.process_bind_param(str(value), dialect) == value.hex


def test_guid_postgres_paths() -> None:
    guid = GUID()
    dialect = _PgDialect()
    value = uuid.uuid4()
    assert guid.process_bind_param(value, dialect) == value
    assert guid.process_bind_param(str(value), dialect) == value
    guid.load_dialect_impl(dialect)
    guid.load_dialect_impl(_SqliteDialect())


def test_guid_result_passthrough_uuid() -> None:
    guid = GUID()
    value = uuid.uuid4()
    assert guid.process_result_value(value, _SqliteDialect()) == value


@pytest.mark.asyncio
async def test_user_repository_lookups(session) -> None:
    repo = SQLAlchemyUserRepository(session)
    user = await repo.add(
        User(
            email="infra@example.com",
            full_name="Infra User",
            hashed_password="hashed",
            role=UserRole.ADMIN,
        )
    )
    assert await repo.get_by_id(user.id) is not None
    assert await repo.get_by_email("infra@example.com") is not None
    assert await repo.get_by_email("missing@example.com") is None
    users = await repo.list_all()
    assert any(u.id == user.id for u in users)
    assert await repo.get_by_id(uuid.uuid4()) is None
