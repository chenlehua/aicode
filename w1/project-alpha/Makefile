.PHONY: help build up down restart logs ps shell-backend shell-db migrate seed rebuild dev-up dev-down check-api check-frontend check-all install-pre-commit format format-check

# Default target
help:
	@echo "Ticket Tag Management - Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help           Show this help message"
	@echo "  build          Build all Docker images"
	@echo "  up             Start all services"
	@echo "  down           Stop all services"
	@echo "  restart        Restart all services"
	@echo "  logs           Show logs from all services"
	@echo "  logs-backend   Show backend logs"
	@echo "  logs-frontend  Show frontend logs"
	@echo "  logs-db        Show database logs"
	@echo "  ps             Show running containers"
	@echo "  shell-backend  Open shell in backend container"
	@echo "  shell-db       Open PostgreSQL shell"
	@echo "  migrate        Run database migrations"
	@echo "  seed           Load seed data"
	@echo "  rebuild        Rebuild and restart all services"
	@echo "  install-pre-commit  Install pre-commit hooks"
	@echo "  format         Format code (black, isort, prettier)"
	@echo "  format-check   Check code formatting"

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo ""
	@echo "Services started:"
	@echo "  - Frontend: http://localhost"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - API Docs: http://localhost:8000/docs"
	@echo "  - Database: localhost:5432"

# Stop all services
down:
	docker-compose down

# Restart all services
restart: down up

# Show logs
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f db

# Show running containers
ps:
	docker-compose ps

# Open shell in backend container
shell-backend:
	docker-compose exec backend /bin/bash

# Open PostgreSQL shell
shell-db:
	docker-compose exec db psql -U ticketapp -d ticketapp

# Run database migrations
migrate:
	docker-compose exec backend uv run alembic upgrade head

# Load seed data
seed:
	docker-compose exec -T db psql -U ticketapp -d ticketapp < backend/docs/seed.sql
	@echo "Seed data loaded successfully!"

# Rebuild and restart
rebuild: build up

# Development commands
dev-up:
	docker-compose up -d db
	@echo "Database started. Use './start-backend.sh' and 'npm run dev' for local development"

dev-down:
	docker-compose stop db

# Debug commands
check-api:
	@echo "Checking backend API..."
	@curl -s http://localhost:8000/health | jq . || echo "Backend not responding"
	@echo ""
	@echo "Checking tickets API..."
	@curl -s http://localhost:8000/api/v1/tickets | jq '.total' || echo "Tickets API not responding"
	@echo ""
	@echo "Checking tags API..."
	@curl -s http://localhost:8000/api/v1/tags | jq 'length' || echo "Tags API not responding"

check-frontend:
	@echo "Checking frontend..."
	@curl -s http://localhost | grep -q "Ticket Tag Management" && echo "Frontend is accessible" || echo "Frontend not accessible"

check-all: check-api check-frontend
	@echo ""
	@echo "All checks completed!"

# Pre-commit commands
install-pre-commit:
	@echo "Installing pre-commit..."
	pip install pre-commit || uv pip install pre-commit
	pre-commit install
	@echo "Pre-commit installed successfully!"

format:
	@echo "Formatting Python code..."
	@cd backend && UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --extra dev > /dev/null 2>&1 || true
	cd backend && uv run black . && uv run isort .
	@echo "Formatting TypeScript/JavaScript code..."
	cd frontend && npm run format
	@echo "Code formatted!"

format-check:
	@echo "Checking Python code formatting..."
	@cd backend && UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --extra dev > /dev/null 2>&1 || true
	cd backend && uv run black --check . && uv run isort --check-only .
	@echo "Checking TypeScript/JavaScript code formatting..."
	cd frontend && npm run format:check
	@echo "Format check passed!"
