.PHONY: help setup dev test lint format typecheck build clean docker-up docker-down docker-logs migrate

help:
	@echo "=================================================================="
	@echo "CORTEXA — Production Engineering Foundation Commands"
	@echo "=================================================================="
	@echo "  make setup        - Install backend & frontend dependencies"
	@echo "  make dev          - Start all services with Docker Compose"
	@echo "  make test         - Run backend and frontend test suites"
	@echo "  make lint         - Run linters (Ruff, ESLint)"
	@echo "  make format       - Run code formatters (Ruff format, Prettier)"
	@echo "  make typecheck    - Run type checkers (MyPy, tsc)"
	@echo "  make build        - Build backend and frontend artifacts/images"
	@echo "  make clean        - Remove caches, builds, and temporary files"
	@echo "  make docker-up    - Build and start containers in background"
	@echo "  make docker-down  - Stop and remove running containers"
	@echo "  make docker-logs  - View live logs from all Docker containers"
	@echo "  make migrate      - Run database migrations with Alembic"
	@echo "=================================================================="

setup:
	@echo "==> Setting up Python virtual environment..."
	python -m pip install --upgrade pip
	pip install -r apps/api/requirements.txt
	@echo "==> Setting up Frontend dependencies..."
	cd apps/web && npm install

dev: docker-up

test:
	@echo "==> Running backend test suite..."
	pytest
	@echo "==> Running frontend checks..."
	cd apps/web && npm run type-check

lint:
	@echo "==> Running backend linting..."
	ruff check .
	@echo "==> Running frontend linting..."
	cd apps/web && npm run lint

format:
	@echo "==> Formatting backend code..."
	ruff format .
	@echo "==> Formatting frontend code..."
	cd apps/web && npm run format

typecheck:
	@echo "==> Running MyPy on backend..."
	mypy apps/api/app
	@echo "==> Running TypeScript compiler on frontend..."
	cd apps/web && npm run type-check

build:
	@echo "==> Building Docker images..."
	docker compose build

clean:
	@echo "==> Cleaning caches and artifacts..."
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf apps/web/.next apps/web/out

docker-up:
	@echo "==> Starting Cortexa stack with Docker Compose..."
	docker compose up --build -d

docker-down:
	@echo "==> Stopping Cortexa stack..."
	docker compose down

docker-logs:
	@echo "==> Streaming logs..."
	docker compose logs -f

migrate:
	@echo "==> Applying database migrations..."
	cd apps/api && alembic upgrade head
