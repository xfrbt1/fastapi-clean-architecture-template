"""Integration tests: HTTP client + PostgreSQL + Redis (see README)."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings
from app.infrastructure.db.base import Base


def _ensure_test_env() -> None:
    """Align env with docker-compose defaults for local integration runs."""
    os.environ.setdefault("DB_HOST", "127.0.0.1")
    os.environ.setdefault("DB_PORT", "5432")
    os.environ.setdefault("DB_USER", "app")
    os.environ.setdefault("DB_PASSWORD", "app")
    os.environ.setdefault("DB_NAME", "app")
    os.environ.setdefault("REDIS_HOST", "127.0.0.1")
    os.environ.setdefault("REDIS_PORT", "6379")


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    """Create tables for the session; skip if PostgreSQL is unavailable."""
    _ensure_test_env()
    get_settings.cache_clear()
    settings = get_settings()
    engine = create_async_engine(settings.db.dsn, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 — surface connection errors
        await engine.dispose()
        pytest.skip(f"PostgreSQL not reachable for integration tests: {exc}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
        get_settings.cache_clear()


@pytest_asyncio.fixture
async def http_client(engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    """ASGI app with lifespan (DB pool + Redis client)."""
    _ = engine
    get_settings.cache_clear()
    from app.main import app

    async with (
        LifespanManager(app),
        AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client,
    ):
        yield client


@pytest_asyncio.fixture(autouse=True)
async def truncate_users(engine: AsyncEngine) -> AsyncIterator[None]:
    """Truncate users between tests."""
    yield
    async with engine.begin() as conn:
        await conn.execute(text('TRUNCATE TABLE "users" CASCADE'))
