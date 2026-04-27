"""Unit tests: Email value object and User entity (no DB/framework)."""

import uuid
from datetime import UTC, datetime

import pytest

from app.domain.entities.user import User
from app.domain.value_objects.email import Email


def test_email_normalizes_and_validates() -> None:
    """Email VO strips, lowercases, and rejects invalid strings."""
    e = Email("  User@Example.COM ")
    assert e.value == "user@example.com"

    with pytest.raises(ValueError, match="Invalid email"):
        Email("not-an-email")

    with pytest.raises(ValueError, match="Invalid email"):
        Email("")


def test_user_rename_business_rule() -> None:
    """rename() rejects blank names."""
    uid = uuid.uuid4()
    now = datetime.now(UTC)
    user = User(
        id=uid,
        email=Email("u@example.com"),
        hashed_password="x",
        full_name="Alice",
        created_at=now,
        updated_at=now,
    )
    user.rename("  Bob  ")
    assert user.full_name == "Bob"

    with pytest.raises(ValueError, match="empty"):
        user.rename("   ")
