.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend build build-backend build-frontend test test-backend test-frontend clean clean-backend clean-frontend lint lint-backend lint-frontend format format-backend format-frontend typecheck typecheck-backend typecheck-frontend

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
