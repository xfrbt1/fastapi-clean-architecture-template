from typing import Protocol
from uuid import UUID

from app.domain.entities.user import User
from app.domain.value_objects.email import Email


class UserRepository(Protocol):
    """Persistence abstraction for User aggregate."""

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Return user by primary key or None."""

    async def get_by_email(self, email: Email) -> User | None:
        """Return user by unique email or None."""

    async def list_users(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        """Paginated list."""

    async def add(self, user: User) -> None:
        """Insert a new user (caller commits via UoW)."""

    async def update(self, user: User) -> None:
        """Update existing user."""

    async def delete(self, user_id: UUID) -> None:
        """Delete by id."""
