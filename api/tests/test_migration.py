"""Verify the Alembic migrations produce the expected CRM schema."""

from __future__ import annotations

import pytest
from sqlalchemy import inspect

from app.infrastructure.db import session as db_session

_EXPECTED_TABLES = {
    "alembic_version",
    "users",
    "clientes",
    "produtos",
    "leads",
    "conversas",
    "vendas",
}


@pytest.mark.asyncio
async def test_migrations_create_all_tables() -> None:
    engine = db_session.get_engine()
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync: set(inspect(sync).get_table_names()))
    assert _EXPECTED_TABLES.issubset(tables)


@pytest.mark.asyncio
async def test_leads_reference_clientes() -> None:
    engine = db_session.get_engine()

    def _fk_targets(sync: object) -> set[str]:
        inspector = inspect(sync)
        return {fk["referred_table"] for fk in inspector.get_foreign_keys("leads")}

    async with engine.connect() as conn:
        targets = await conn.run_sync(_fk_targets)
    assert "clientes" in targets


@pytest.mark.asyncio
async def test_migration_is_at_head() -> None:
    engine = db_session.get_engine()

    def _version(sync: object) -> str | None:
        inspector = inspect(sync)
        if "alembic_version" not in inspector.get_table_names():
            return None
        return "present"

    async with engine.connect() as conn:
        marker = await conn.run_sync(_version)
    assert marker == "present"
