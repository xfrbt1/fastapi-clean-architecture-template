import json
from datetime import datetime
from uuid import UUID

from app.application.dto.user import UserDTO
from app.application.interfaces.cache import CachePort
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.mappers.user import user_to_dto
from app.domain.exceptions import UserNotFoundError

_CACHE_PREFIX = "user:"


def _cache_key(user_id: UUID) -> str:
    return f"{_CACHE_PREFIX}{user_id}"


def _dto_to_json_bytes(dto: UserDTO) -> bytes:
    payload = {
        "id": str(dto.id),
        "email": dto.email,
        "full_name": dto.full_name,
        "is_active": dto.is_active,
        "created_at": dto.created_at.isoformat(),
        "updated_at": dto.updated_at.isoformat(),
    }
    return json.dumps(payload).encode("utf-8")


def _dto_from_json(raw: bytes) -> UserDTO:
    data = json.loads(raw.decode("utf-8"))
    return UserDTO(
        id=UUID(data["id"]),
        email=data["email"],
        full_name=data["full_name"],
        is_active=data["is_active"],
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )


async def get_user_by_id(
    uow: UnitOfWork,
    cache: CachePort,
    *,
    user_id: UUID,
    cache_ttl_seconds: int,
) -> UserDTO:
    """Load user; try cache first, then database, then populate cache."""
    cached = await cache.get(_cache_key(user_id))
    if cached is not None:
        return _dto_from_json(cached)

    async with uow:
        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id=str(user_id))
        dto = user_to_dto(user)

    await cache.set(_cache_key(user_id), _dto_to_json_bytes(dto), ttl_seconds=cache_ttl_seconds)
    return dto
