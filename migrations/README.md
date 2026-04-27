# Alembic migrations

- **Apply:** `poetry run alembic upgrade head` (from project root, `PYTHONPATH=src` or use `make migrate`).
- **Create:** `poetry run alembic revision --autogenerate -m "description"` after changing SQLAlchemy models.
- Async engine is configured in [`env.py`](env.py); models must be imported so `Base.metadata` is complete.
