from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._users: SqlAlchemyUserRepository | None = None

    @property
    def users(self) -> SqlAlchemyUserRepository:
        if self._session is None:
            msg = "UnitOfWork is not active"
            raise RuntimeError(msg)
        if self._users is None:
            self._users = SqlAlchemyUserRepository(self._session)
        return self._users

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self._users = SqlAlchemyUserRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
            self._users = None

    async def commit(self) -> None:
        if self._session is None:
            msg = "UnitOfWork is not active"
            raise RuntimeError(msg)
        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            msg = "UnitOfWork is not active"
            raise RuntimeError(msg)
        await self._session.rollback()
