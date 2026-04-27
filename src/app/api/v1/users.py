from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import CacheDep, CurrentUserId, SettingsDep, UoWDep
from app.api.schemas.common import UserResponse
from app.api.schemas.user import UserUpdateRequest
from app.application.dto.user import UpdateUserDTO
from app.application.use_cases.users.delete_user import delete_user
from app.application.use_cases.users.get_user import get_user_by_id
from app.application.use_cases.users.list_users import list_users
from app.application.use_cases.users.update_user import update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users_endpoint(
    uow: UoWDep,
    _: CurrentUserId,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UserResponse]:
    """Paginated user list (requires auth)."""
    rows = await list_users(uow, limit=limit, offset=offset)
    return [
        UserResponse(
            id=r.id,
            email=r.email,
            full_name=r.full_name,
            is_active=r.is_active,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: UUID,
    uow: UoWDep,
    cache: CacheDep,
    settings: SettingsDep,
    _: CurrentUserId,
) -> UserResponse:
    dto = await get_user_by_id(
        uow,
        cache,
        user_id=user_id,
        cache_ttl_seconds=settings.user_cache_ttl_seconds,
    )
    return UserResponse(
        id=dto.id,
        email=dto.email,
        full_name=dto.full_name,
        is_active=dto.is_active,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: UUID,
    body: UserUpdateRequest,
    uow: UoWDep,
    cache: CacheDep,
    _: CurrentUserId,
) -> UserResponse:
    dto = UpdateUserDTO(full_name=body.full_name, is_active=body.is_active)
    result = await update_user(uow, cache, user_id, dto)
    return UserResponse(
        id=result.id,
        email=result.email,
        full_name=result.full_name,
        is_active=result.is_active,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_user_endpoint(
    user_id: UUID,
    uow: UoWDep,
    cache: CacheDep,
    _: CurrentUserId,
) -> Response:
    await delete_user(uow, cache, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
