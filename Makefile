.PHONY: help dev down logs test lint format clean

# Default target
help:
	@echo "AI PR Reviewer — Available Commands"
	@echo "──────────────────────────────────────"
	@echo "  make dev       Start all services (docker-compose)"
	@echo "  make down      Stop all services"
	@echo "  make logs      Tail backend logs"
	@echo "  make shell     Open shell in backend container"
	@echo "  make migrate   Run Alembic migrations"
	@echo "  make test      Run all tests"
	@echo "  make lint      Run linters (ruff + mypy)"
	@echo "  make format    Auto-format code (ruff format)"
	@echo "  make clean     Remove containers and volumes"
	@echo "  make seed-vdb  Seed vector DB with guidelines"

# ── Docker ─────────────────────────────────────────────────────────────────────
dev:
	docker compose -f infra/docker/docker-compose.yml up --build -d
	@echo "✅ Services started. API docs: http://localhost:8000/docs"

down:
	docker compose -f infra/docker/docker-compose.yml down

logs:
	docker compose -f infra/docker/docker-compose.yml logs -f backend worker

shell:
	docker compose -f infra/docker/docker-compose.yml exec backend bash

# ── Database ────────────────────────────────────────────────────────────────────
migrate:
	docker compose -f infra/docker/docker-compose.yml exec backend \
		alembic upgrade head

migrate-create:
	docker compose -f infra/docker/docker-compose.yml exec backend \
		alembic revision --autogenerate -m "$(msg)"

# ── Testing ─────────────────────────────────────────────────────────────────────
test:
	cd backend && python -m pytest tests/ -v --tb=short

test-cov:
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

# ── Code Quality ────────────────────────────────────────────────────────────────
lint:
	cd backend && ruff check app/ && mypy app/

format:
	cd backend && ruff format app/

# ── Vector DB ───────────────────────────────────────────────────────────────────
seed-vdb:
	docker compose -f infra/docker/docker-compose.yml exec backend \
		python /app/../vector-db/ingest.py

# ── Cleanup ─────────────────────────────────────────────────────────────────────
clean:
	docker compose -f infra/docker/docker-compose.yml down -v --remove-orphans
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
