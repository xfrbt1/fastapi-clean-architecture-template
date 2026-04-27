from fastapi import APIRouter, status

from app.api.dependencies import CurrentUserId, SettingsDep, UoWDep
from app.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.api.schemas.common import UserResponse
from app.application.dto.user import CreateUserDTO, LoginDTO
from app.application.use_cases.auth.authenticate_user import login_user
from app.application.use_cases.auth.get_current_user import get_user_profile
from app.application.use_cases.auth.register_user import register_user
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, uow: UoWDep) -> UserResponse:
    """Create a new account."""
    dto = CreateUserDTO(email=body.email, password=body.password, full_name=body.full_name)
    result = await register_user(uow, dto)
    return UserResponse(
        id=result.id,
        email=result.email,
        full_name=result.full_name,
        is_active=result.is_active,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    uow: UoWDep,
    settings: SettingsDep,
) -> TokenResponse:
    """Return JWT access token."""
    dto = LoginDTO(email=body.email, password=body.password)
    user = await login_user(uow, dto)
    token = create_access_token(subject=str(user.id), settings=settings)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(
    uow: UoWDep,
    user_id: CurrentUserId,
) -> UserResponse:
    """Current user from Bearer token."""
    profile = await get_user_profile(uow, user_id)
    return UserResponse(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        is_active=profile.is_active,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
