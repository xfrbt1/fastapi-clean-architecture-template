from datetime import UTC, datetime
from uuid import UUID

from app.application.dto.user import UpdateUserDTO, UserDTO
from app.application.interfaces.cache import CachePort
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.mappers.user import user_to_dto
from app.domain.exceptions import UserNotFoundError


def _cache_key(user_id: UUID) -> str:
    return f"user:{user_id}"


async def update_user(
    uow: UnitOfWork,
    cache: CachePort,
    user_id: UUID,
    dto: UpdateUserDTO,
) -> UserDTO:
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id=str(user_id))
        if dto.full_name is not None:
            user.rename(dto.full_name)
        if dto.is_active is not None:
            user.is_active = dto.is_active
        user.updated_at = datetime.now(UTC)
        await uow.users.update(user)
        await uow.commit()
        dto_out = user_to_dto(user)
    await cache.delete(_cache_key(user_id))
    return dto_out
