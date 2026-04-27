from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.infrastructure.db.models.user import UserModel


def _to_domain(row: UserModel) -> User:
    return User(
        id=row.id,
        email=Email(row.email),
        hashed_password=row.hashed_password,
        full_name=row.full_name,
        created_at=row.created_at,
        updated_at=row.updated_at,
        is_active=row.is_active,
    )


def _to_model(entity: User) -> UserModel:
    return UserModel(
        id=entity.id,
        email=entity.email.value,
        hashed_password=entity.hashed_password,
        full_name=entity.full_name,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        is_active=entity.is_active,
    )


class SqlAlchemyUserRepository(UserRepository):
    """User persistence using async SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.get(UserModel, user_id)
        return _to_domain(result) if result is not None else None

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value).limit(1)
        res = await self._session.execute(stmt)
        row = res.scalar_one_or_none()
        return _to_domain(row) if row is not None else None

    async def list_users(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = select(UserModel).order_by(UserModel.created_at.desc()).offset(offset).limit(limit)
        res = await self._session.execute(stmt)
        rows = res.scalars().all()
        return [_to_domain(r) for r in rows]

    async def add(self, user: User) -> None:
        self._session.add(_to_model(user))

    async def update(self, user: User) -> None:
        existing = await self._session.get(UserModel, user.id)
        if existing is None:
            return
        existing.email = user.email.value
        existing.hashed_password = user.hashed_password
        existing.full_name = user.full_name
        existing.is_active = user.is_active
        existing.updated_at = user.updated_at

    async def delete(self, user_id: UUID) -> None:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await self._session.execute(stmt)
