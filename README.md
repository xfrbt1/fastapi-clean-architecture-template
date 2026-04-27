# FastAPI Clean Architecture Template

Production-ready backend template built with **Python 3.12+**, **FastAPI**, **Clean Architecture**, **PostgreSQL**, **Redis**, **JWT**, **Alembic**, and **Docker**.

## Requirements

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker & Docker Compose (optional)

## Quick Start (Local)

```bash
cp .env.example .env
# Set JWT_SECRET_KEY (a long random string)
poetry install --with dev
# Start PostgreSQL and Redis (for example, only DB and cache)
docker compose up -d postgres redis
export PYTHONPATH=src
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- OpenAPI: <http://localhost:8000/docs>
- Health: `GET /api/v1/health` (PostgreSQL + Redis)

## Docker Compose (API + PostgreSQL + Redis)

```bash
cp .env.example .env
make up
# Run migrations from the API container (image includes alembic.ini and migrations/)
docker compose exec api /app/.venv/bin/alembic -c /app/alembic.ini upgrade head
```

API: <http://localhost:8000/docs>

## Commands (Makefile)

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies with Poetry |
| `make run` | Run uvicorn with hot-reload |
| `make test` | Pytest (unit + integration) |
| `make lint` | Flake8 |
| `make format` | Black |
| `make typecheck` | Mypy |
| `make migrate` | Apply Alembic migrations |
| `make migration name=add_table` | Create a new revision |
| `make docker-build` | Build API image |
| `make up` | Start docker compose |
| `make down` | Stop compose |

## Alembic Migrations

```bash
export PYTHONPATH=src
# Apply
poetry run alembic upgrade head

# Create a new migration (after model changes)
poetry run alembic revision --autogenerate -m "description"
```

See details in [migrations/README.md](migrations/README.md).

## Tests

```bash
export PYTHONPATH=src
export JWT_SECRET_KEY="your-test-secret-at-least-32-chars-long!!"
poetry run pytest tests/unit -v                    # unit (without DB)
poetry run pytest tests/integration -v             # requires PostgreSQL and Redis (docker compose up -d)
```

Integration tests are skipped (`skipped`) if the database is unavailable.

## Architecture

- **domain** - entities, value objects, repository interfaces, domain exceptions (no framework imports).
- **application** - use cases, DTOs, abstractions (Unit of Work, Cache).
- **infrastructure** - SQLAlchemy, Redis, repository implementations.
- **api** - FastAPI routes, Pydantic schemas, DI, error handling.

### Redis

- **Cache:** `GET /api/v1/users/{id}` caches responses in Redis (TTL from `USER_CACHE_TTL_SECONDS`); when a user is updated/deleted, the key is invalidated (`app/application/use_cases/users/`).
- **Pub/Sub:** for pub/sub use the `redis.asyncio` client (e.g., `client.publish` / `PubSub`); this template demonstrates the common **cache** use case to avoid duplicating abstraction layers.

### Main HTTP Routes

| Method | Path | Description |
|-------|------|-------------|
| GET | `/api/v1/health` | PostgreSQL and Redis status |
| POST | `/api/v1/auth/register` | Registration |
| POST | `/api/v1/auth/login` | JWT access token |
| GET | `/api/v1/auth/me` | Current user (Bearer) |
| GET | `/api/v1/users` | User list (Bearer) |
| GET | `/api/v1/users/{id}` | User by id, with cache (Bearer) |
| PATCH | `/api/v1/users/{id}` | Update (Bearer) |
| DELETE | `/api/v1/users/{id}` | Delete (Bearer) |

## Environment Variables

See [.env.example](.env.example). For production, use a strong `JWT_SECRET_KEY` and disable `APP_DEBUG`.

## Dev Container

Open the folder in VS Code and choose "Reopen in Container" - it uses `docker-compose.yml` (the `api` service).

---

## Adding a New Entity

Follow this checklist when introducing a new domain entity (e.g. `Product`). Keep the same layer order to respect dependency direction (`domain → application → infrastructure → api`).

### 1. Domain layer

| File | What to do |
|------|-----------|
| `src/app/domain/entities/<entity>.py` | Define a `@dataclass(slots=True)` with business methods |
| `src/app/domain/value_objects/<vo>.py` | Add value objects if needed (e.g. `Price`, `SKU`) |
| `src/app/domain/repositories/<entity>_repository.py` | Define a `Protocol` with async CRUD methods |
| `src/app/domain/exceptions.py` | Add `<Entity>NotFoundError`, `<Entity>AlreadyExistsError`, etc. |

### 2. Application layer

| File | What to do |
|------|-----------|
| `src/app/application/dto/<entity>.py` | Add `<Entity>DTO`, `Create<Entity>DTO`, `Update<Entity>DTO` |
| `src/app/application/mappers/<entity>.py` | Add `<entity>_to_dto()` mapper function |
| `src/app/application/use_cases/<entity>/create_<entity>.py` | One file per use case |
| `src/app/application/use_cases/<entity>/get_<entity>.py` | ... |
| `src/app/application/use_cases/<entity>/list_<entity>s.py` | ... |
| `src/app/application/use_cases/<entity>/update_<entity>.py` | ... |
| `src/app/application/use_cases/<entity>/delete_<entity>.py` | ... |
| `src/app/application/interfaces/unit_of_work.py` | Add `<entity>s: <Entity>Repository` property to `UnitOfWork` |

### 3. Infrastructure layer

| File | What to do |
|------|-----------|
| `src/app/infrastructure/db/models/<entity>.py` | Define `<Entity>Model(Base)` with SQLAlchemy `mapped_column` |
| `src/app/infrastructure/db/unit_of_work.py` | Expose `<entity>s` property backed by `SqlAlchemy<Entity>Repository` |
| `src/app/infrastructure/repositories/<entity>_repository.py` | Implement the repository Protocol using `AsyncSession` |

### 4. API layer

| File | What to do |
|------|-----------|
| `src/app/api/schemas/<entity>.py` | Add Pydantic request/response schemas |
| `src/app/api/v1/<entity>s.py` | Create `APIRouter` with GET / POST / PATCH / DELETE routes |
| `src/app/api/v1/router.py` | Register the new router with `router.include_router(...)` |

### 5. Database migration

```bash
export PYTHONPATH=src
poetry run alembic revision --autogenerate -m "create_<entity>s_table"
poetry run alembic upgrade head
```

### 6. Tests

| File | What to add |
|------|------------|
| `tests/unit/domain/test_<entity>.py` | Unit tests for entity business rules and value objects |
| `tests/integration/api/test_<entity>s_flow.py` | Full HTTP flow: create → read → update → delete |
| `tests/integration/conftest.py` | `truncate_<entity>s` autouse fixture |

---

## License

MIT
