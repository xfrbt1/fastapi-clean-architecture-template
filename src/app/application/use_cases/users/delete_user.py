from uuid import UUID

from app.application.interfaces.cache import CachePort
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import UserNotFoundError

_CACHE_PREFIX = "user:"


def _cache_key(user_id: UUID) -> str:
    return f"{_CACHE_PREFIX}{user_id}"


async def delete_user(uow: UnitOfWork, cache: CachePort, user_id: UUID) -> None:
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id=str(user_id))
        await uow.users.delete(user_id)
        await uow.commit()
    await cache.delete(_cache_key(user_id))
