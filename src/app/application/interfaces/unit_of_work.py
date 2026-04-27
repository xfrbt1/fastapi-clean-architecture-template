from types import TracebackType
from typing import Protocol

from app.domain.repositories.user_repository import UserRepository


class UnitOfWork(Protocol):
    """Coordinates repositories and a single database transaction."""

    @property
    def users(self) -> UserRepository:
        """User aggregate repository."""

    async def __aenter__(self) -> "UnitOfWork":
        """Begin transaction context."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Commit or rollback."""

    async def commit(self) -> None:
        """Commit pending work."""

    async def rollback(self) -> None:
        """Rollback pending work."""
