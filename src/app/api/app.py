from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.api.errors import domain_error_handler
from app.api.middlewares import CorrelationIdMiddleware
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.domain.exceptions import DomainError
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.db.engine import create_engine_and_session_factory

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup: engines, Redis; shutdown: dispose."""
    settings = get_settings()
    configure_logging(debug=settings.app.debug)
    engine, session_factory = create_engine_and_session_factory(settings)
    redis_client = Redis.from_url(settings.redis.url, decode_responses=False)
    cache = RedisCache(redis_client)

    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.redis = redis_client
    app.state.cache = cache

    logger.info("application_startup", env=settings.app.env)
    yield
    await redis_client.aclose()
    await engine.dispose()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Configure FastAPI with routes, middleware, and exception handlers."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app.name,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(CorrelationIdMiddleware)

    @app.exception_handler(DomainError)
    async def _domain_handler(request: Request, exc: DomainError) -> JSONResponse:
        http_exc = domain_error_handler(exc)
        return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(ValueError)
    async def _value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    app.include_router(api_router)
    return app
