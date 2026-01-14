.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend build build-backend build-frontend test test-backend test-frontend clean clean-backend clean-frontend lint lint-backend lint-frontend format format-backend format-frontend typecheck typecheck-backend typecheck-frontend docker-up docker-down docker-logs docker-build docker-up-postgres docker-up-backend docker-up-frontend docker-down-postgres docker-down-backend docker-down-frontend docker-logs-postgres docker-logs-backend docker-logs-frontend docker-dev-up docker-dev-down docker-dev-logs docker-dev-up-postgres docker-dev-up-backend docker-dev-up-frontend docker-dev-down-postgres docker-dev-down-backend docker-dev-down-frontend docker-dev-logs-postgres docker-dev-logs-backend docker-dev-logs-frontend docker-clean

# Variables
BACKEND_DIR = backend
FRONTEND_DIR = frontend
BACKEND_PORT = 8000
FRONTEND_PORT = 5173

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	cd $(BACKEND_DIR) && uv sync --extra dev

install-frontend: ## Install frontend dependencies
	cd $(FRONTEND_DIR) && npm install

# Development
dev: dev-backend dev-frontend ## Run both backend and frontend in development mode

dev-backend: ## Run backend development server
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)

dev-frontend: ## Run frontend development server
	cd $(FRONTEND_DIR) && npm run dev

# Build
build: build-backend build-frontend ## Build both backend and frontend

build-backend: ## Build backend (no-op for Python, but useful for consistency)
	@echo "Backend is ready to run (no build step needed)"

build-frontend: ## Build frontend for production
	cd $(FRONTEND_DIR) && npm run build

# Testing
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd $(BACKEND_DIR) && uv run pytest tests/ -v; \
	exit_code=$$?; \
	if [ $$exit_code -eq 5 ]; then \
		echo "No tests found (this is normal if tests haven't been written yet)"; \
		exit 0; \
	elif [ $$exit_code -ne 0 ]; then \
		echo "Tests failed or pytest not installed. Run 'make install-backend' first."; \
		exit $$exit_code; \
	fi

test-frontend: ## Run frontend tests
	@if grep -q '"test"' $(FRONTEND_DIR)/package.json; then \
		cd $(FRONTEND_DIR) && npm test; \
	else \
		echo "No test script configured in package.json"; \
	fi

# Linting
lint: lint-backend lint-frontend ## Lint all code

lint-backend: ## Lint backend code
	cd $(BACKEND_DIR) && uv run ruff check .

lint-frontend: ## Lint frontend code
	cd $(FRONTEND_DIR) && npm run lint

# Formatting
format: format-backend format-frontend ## Format all code

format-backend: ## Format backend code
	cd $(BACKEND_DIR) && uv run ruff format .

format-frontend: ## Format frontend code
	cd $(FRONTEND_DIR) && npm run format

# Type checking
typecheck: typecheck-backend typecheck-frontend ## Type check all code

typecheck-backend: ## Type check backend code
	cd $(BACKEND_DIR) && uv run mypy app/

typecheck-frontend: ## Type check frontend code
	cd $(FRONTEND_DIR) && npm run typecheck

# Cleaning
clean: clean-backend clean-frontend ## Clean all build artifacts

clean-backend: ## Clean backend artifacts
	cd $(BACKEND_DIR) && rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find $(BACKEND_DIR) -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find $(BACKEND_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true

clean-frontend: ## Clean frontend artifacts
	cd $(FRONTEND_DIR) && rm -rf node_modules dist build .vite

# Database
db-init: ## Initialize database schema
	cd $(BACKEND_DIR) && uv run python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

db-reset: ## Reset database (WARNING: deletes all data)
	rm -f ~/.db_query/db_query.db
	$(MAKE) db-init

# Quick start
start: install ## Install dependencies and start development servers
	@echo "Starting development servers..."
	@echo "Backend will be available at http://localhost:$(BACKEND_PORT)"
	@echo "Frontend will be available at http://localhost:$(FRONTEND_PORT)"
	@echo "Run 'make dev-backend' in one terminal and 'make dev-frontend' in another"

# Health check
health: ## Check if backend is running
	@curl -s http://localhost:$(BACKEND_PORT)/health || echo "Backend is not running"

# Docker Compose
docker-up: ## Start all services with docker-compose
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View logs from all services
	docker-compose logs -f

docker-build: ## Build all Docker images
	docker-compose build

# Docker Compose - Individual Services (Production)
docker-up-postgres: ## Start only PostgreSQL service
	docker-compose up -d postgres

docker-up-backend: ## Start backend service (requires postgres)
	docker-compose up -d backend

docker-up-frontend: ## Start frontend service (requires backend)
	docker-compose up -d frontend

docker-down-postgres: ## Stop PostgreSQL service
	docker-compose stop postgres

docker-down-backend: ## Stop backend service
	docker-compose stop backend

docker-down-frontend: ## Stop frontend service
	docker-compose stop frontend

docker-logs-postgres: ## View PostgreSQL logs
	docker-compose logs -f postgres

docker-logs-backend: ## View backend logs
	docker-compose logs -f backend

docker-logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

# Docker Compose - Development
docker-dev-up: ## Start development services with docker-compose
	docker-compose -f docker-compose.dev.yml up -d

docker-dev-down: ## Stop development services
	docker-compose -f docker-compose.dev.yml down

docker-dev-logs: ## View logs from development services
	docker-compose -f docker-compose.dev.yml logs -f

# Docker Compose - Individual Services (Development)
docker-dev-up-postgres: ## Start only PostgreSQL service (dev)
	docker-compose -f docker-compose.dev.yml up -d postgres

docker-dev-up-backend: ## Start backend service (dev, requires postgres)
	docker-compose -f docker-compose.dev.yml up -d backend

docker-dev-up-frontend: ## Start frontend service (dev, requires backend)
	docker-compose -f docker-compose.dev.yml up -d frontend

docker-dev-down-postgres: ## Stop PostgreSQL service (dev)
	docker-compose -f docker-compose.dev.yml stop postgres

docker-dev-down-backend: ## Stop backend service (dev)
	docker-compose -f docker-compose.dev.yml stop backend

docker-dev-down-frontend: ## Stop frontend service (dev)
	docker-compose -f docker-compose.dev.yml stop frontend

docker-dev-logs-postgres: ## View PostgreSQL logs (dev)
	docker-compose -f docker-compose.dev.yml logs -f postgres

docker-dev-logs-backend: ## View backend logs (dev)
	docker-compose -f docker-compose.dev.yml logs -f backend

docker-dev-logs-frontend: ## View frontend logs (dev)
	docker-compose -f docker-compose.dev.yml logs -f frontend

docker-clean: ## Remove all containers, volumes, and images
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
