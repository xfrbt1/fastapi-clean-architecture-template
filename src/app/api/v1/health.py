from fastapi import APIRouter, Request, status

from app.api.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health(request: Request) -> HealthResponse:
    session_factory = request.app.state.session_factory
    cache = request.app.state.cache

    db_status = "ok"
    try:
        from sqlalchemy import text

        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    redis_status = "ok" if await cache.ping() else "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return HealthResponse(status=overall, database=db_status, redis=redis_status)
