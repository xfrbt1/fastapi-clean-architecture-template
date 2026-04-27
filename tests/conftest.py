"""Pytest configuration and shared fixtures."""

import os

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio for anyio-based tests."""
    return "asyncio"


@pytest.fixture(autouse=True)
def _jwt_secret() -> None:
    """Ensure JWT secret is set before any app import in tests."""
    os.environ.setdefault(
        "JWT_SECRET_KEY",
        "test-secret-key-must-be-long-enough-for-hs256-32bytes!",
    )
