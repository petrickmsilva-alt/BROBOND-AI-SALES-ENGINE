"""Shared test fixtures.

Tests run against a real SQLite database provisioned through the project's
Alembic migrations (never ``create_all``), exercising the same schema that
PostgreSQL receives in production. The process-wide async engine and session
factory are swapped for a SQLite-backed pair, and foreign-key enforcement is
switched on so cascade behaviour matches PostgreSQL.
"""

from __future__ import annotations

import tempfile
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from alembic.config import Config
from app.api.dependencies import get_health_service
from app.application.dto.health_dto import HealthResponse
from app.core.config import get_settings
from app.infrastructure.db import session as db_session
from app.main import create_app

_API_ROOT = Path(__file__).resolve().parent.parent
_TMP_DIR = tempfile.mkdtemp(prefix="brobond-test-")
_DB_PATH = Path(_TMP_DIR) / "test.db"
_TEST_DB_URL = f"sqlite+aiosqlite:///{_DB_PATH}"


def _run_migrations() -> None:
    """Apply Alembic migrations to the test database."""
    config = Config(str(_API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(_API_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", _TEST_DB_URL)
    command.upgrade(config, "head")


@pytest.fixture(scope="session", autouse=True)
def _database() -> Iterator[None]:
    """Provision a migrated SQLite database and bind the app engine to it."""
    engine = create_async_engine(_TEST_DB_URL, echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def _set_pragma(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    factory = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

    def _bind() -> None:
        db_session._engine = engine
        db_session._session_factory = factory

    _bind()
    _run_migrations()
    get_settings.cache_clear()

    # The application lifespan disposes the engine on shutdown; keep the shared
    # test engine alive across the whole session instead.
    original_dispose = db_session.dispose_engine

    async def _noop_dispose() -> None:
        return None

    db_session.dispose_engine = _noop_dispose  # type: ignore[assignment]

    # Re-bind before every test in case a previous lifespan cleared the globals.
    global _rebind
    _rebind = _bind

    yield

    db_session.dispose_engine = original_dispose  # type: ignore[assignment]
    db_session._engine = None
    db_session._session_factory = None


_rebind: callable[[], None] | None = None


@pytest.fixture(autouse=True)
def _ensure_engine_bound() -> None:
    """Re-assert the SQLite engine binding before each test."""
    if _rebind is not None:
        _rebind()


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Yield a database session bound to the test database."""
    factory = db_session.get_session_factory()
    async with factory() as db:
        yield db


class StubHealthService:
    """Health service returning a deterministic healthy report."""

    async def check(self) -> HealthResponse:
        settings = get_settings()
        return HealthResponse(
            status="healthy",
            service=settings.app_name,
            version=settings.app_version,
            environment=settings.app_env,
            dependencies={"database": "up", "redis": "up", "ollama": "up"},
        )


@pytest.fixture
def isolated_db(_ensure_engine_bound: None) -> Iterator[None]:
    """Bind the app to a fresh, migrated database for a single test.

    Used by tests that assert on absolute row counts (e.g. the seed command)
    and therefore need an empty starting point. Depends on the autouse rebind
    fixture so it takes effect *after* the default engine has been restored.
    """
    tmp_dir = tempfile.mkdtemp(prefix="brobond-iso-")
    db_path = Path(tmp_dir) / "iso.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    engine = create_async_engine(url, echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def _set_pragma(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    config = Config(str(_API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(_API_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")

    saved_engine = db_session._engine
    saved_factory = db_session._session_factory
    db_session._engine = engine
    db_session._session_factory = async_sessionmaker(
        bind=engine, expire_on_commit=False, autoflush=False
    )
    try:
        yield
    finally:
        db_session._engine = saved_engine
        db_session._session_factory = saved_factory


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Return a TestClient wired to the migrated test database."""
    app = create_app()
    app.dependency_overrides[get_health_service] = StubHealthService
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
