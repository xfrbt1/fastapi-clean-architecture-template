#!/usr/bin/env bash
# Optional shell helpers (Makefile is preferred).
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-src}"

case "${1:-}" in
  install) poetry install --with dev ;;
  run) poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 ;;
  test) poetry run pytest ;;
  lint) poetry run flake8 src tests ;;
  format) poetry run black src tests ;;
  typecheck) poetry run mypy src ;;
  migrate) poetry run alembic upgrade head ;;
  docker-build) docker build -t fastapi-clean-architecture:latest . ;;
  up) docker compose up -d --build ;;
  down) docker compose down ;;
  *) echo "Usage: $0 {install|run|test|lint|format|typecheck|migrate|docker-build|up|down}"; exit 1 ;;
esac
