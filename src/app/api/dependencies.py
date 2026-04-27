from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.application.interfaces.cache import CachePort
from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork

security = HTTPBearer(auto_error=False)


def get_app_settings() -> Settings:
    return get_settings()


def get_uow(request: Request) -> SqlAlchemyUnitOfWork:
    session_factory = request.app.state.session_factory
    return SqlAlchemyUnitOfWork(session_factory)


def get_cache_port(request: Request) -> CachePort:
    cache: RedisCache = request.app.state.cache
    return cache


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> UUID:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials, settings)
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return UUID(str(sub))
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc


UoWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
CacheDep = Annotated[CachePort, Depends(get_cache_port)]
SettingsDep = Annotated[Settings, Depends(get_app_settings)]
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
