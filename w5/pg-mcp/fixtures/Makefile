# =====================================================
# PostgreSQL MCP Server - Test Fixtures Makefile
# 测试数据库管理
# =====================================================

.PHONY: help up down restart logs status \
        up-small up-medium up-large \
        down-small down-medium down-large \
        restart-small restart-medium restart-large \
        logs-small logs-medium logs-large \
        rebuild rebuild-small rebuild-medium rebuild-large \
        clean clean-small clean-medium clean-large \
        shell-small shell-medium shell-large \
        psql-small psql-medium psql-large \
        stats stats-small stats-medium stats-large \
        up-admin down-admin

# Default target
.DEFAULT_GOAL := help

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

# Database connection info
SMALL_PORT := 5432
MEDIUM_PORT := 5433
LARGE_PORT := 5434
DB_USER := postgres
DB_PASS := postgres

# =====================================================
# Help
# =====================================================

help: ## 显示帮助信息
	@echo ""
	@echo "$(GREEN)PostgreSQL MCP Server - Test Fixtures$(NC)"
	@echo "======================================="
	@echo ""
	@echo "$(YELLOW)数据库信息:$(NC)"
	@echo "  Small  (博客系统)   - localhost:$(SMALL_PORT)/blog_db"
	@echo "  Medium (电商平台)   - localhost:$(MEDIUM_PORT)/ecommerce_db"
	@echo "  Large  (ERP系统)    - localhost:$(LARGE_PORT)/erp_db"
	@echo ""
	@echo "$(YELLOW)可用命令:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# =====================================================
# Start/Stop All Databases
# =====================================================

up: ## 启动所有测试数据库
	@echo "$(GREEN)Starting all test databases...$(NC)"
	docker compose up -d pg-small pg-medium pg-large
	@echo ""
	@echo "$(GREEN)Databases started:$(NC)"
	@echo "  Small:  localhost:$(SMALL_PORT)/blog_db"
	@echo "  Medium: localhost:$(MEDIUM_PORT)/ecommerce_db"
	@echo "  Large:  localhost:$(LARGE_PORT)/erp_db"

down: ## 停止所有测试数据库
	@echo "$(YELLOW)Stopping all test databases...$(NC)"
	docker compose down

restart: down up ## 重启所有测试数据库

logs: ## 查看所有数据库日志
	docker compose logs -f pg-small pg-medium pg-large

status: ## 查看数据库状态
	@echo "$(GREEN)Database Status:$(NC)"
	@echo ""
	@docker compose ps

# =====================================================
# Individual Database Operations
# =====================================================

up-small: ## 启动 Small 数据库 (博客系统)
	@echo "$(GREEN)Starting Small database (Blog System)...$(NC)"
	docker compose up -d pg-small

up-medium: ## 启动 Medium 数据库 (电商平台)
	@echo "$(GREEN)Starting Medium database (E-Commerce)...$(NC)"
	docker compose up -d pg-medium

up-large: ## 启动 Large 数据库 (ERP系统)
	@echo "$(GREEN)Starting Large database (ERP System)...$(NC)"
	docker compose up -d pg-large

down-small: ## 停止 Small 数据库
	docker compose stop pg-small

down-medium: ## 停止 Medium 数据库
	docker compose stop pg-medium

down-large: ## 停止 Large 数据库
	docker compose stop pg-large

restart-small: down-small up-small ## 重启 Small 数据库

restart-medium: down-medium up-medium ## 重启 Medium 数据库

restart-large: down-large up-large ## 重启 Large 数据库

logs-small: ## 查看 Small 数据库日志
	docker compose logs -f pg-small

logs-medium: ## 查看 Medium 数据库日志
	docker compose logs -f pg-medium

logs-large: ## 查看 Large 数据库日志
	docker compose logs -f pg-large

# =====================================================
# Rebuild Databases (Clean + Reinitialize)
# =====================================================

rebuild: rebuild-small rebuild-medium rebuild-large ## 重建所有数据库

rebuild-small: ## 重建 Small 数据库 (删除数据并重新初始化)
	@echo "$(RED)Rebuilding Small database...$(NC)"
	docker compose stop pg-small
	docker compose rm -f pg-small
	docker volume rm -f pg-mcp-small-data 2>/dev/null || true
	docker compose up -d pg-small
	@echo "$(GREEN)Small database rebuilt successfully!$(NC)"

rebuild-medium: ## 重建 Medium 数据库 (删除数据并重新初始化)
	@echo "$(RED)Rebuilding Medium database...$(NC)"
	docker compose stop pg-medium
	docker compose rm -f pg-medium
	docker volume rm -f pg-mcp-medium-data 2>/dev/null || true
	docker compose up -d pg-medium
	@echo "$(GREEN)Medium database rebuilt successfully!$(NC)"

rebuild-large: ## 重建 Large 数据库 (删除数据并重新初始化)
	@echo "$(RED)Rebuilding Large database...$(NC)"
	docker compose stop pg-large
	docker compose rm -f pg-large
	docker volume rm -f pg-mcp-large-data 2>/dev/null || true
	docker compose up -d pg-large
	@echo "$(GREEN)Large database rebuilt successfully!$(NC)"

# =====================================================
# Clean (Remove Containers and Volumes)
# =====================================================

clean: ## 清理所有容器和数据卷
	@echo "$(RED)Cleaning all containers and volumes...$(NC)"
	docker compose down -v
	docker volume rm -f pg-mcp-small-data pg-mcp-medium-data pg-mcp-large-data pg-mcp-pgadmin-data 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-small: ## 清理 Small 数据库
	docker compose stop pg-small
	docker compose rm -f pg-small
	docker volume rm -f pg-mcp-small-data 2>/dev/null || true

clean-medium: ## 清理 Medium 数据库
	docker compose stop pg-medium
	docker compose rm -f pg-medium
	docker volume rm -f pg-mcp-medium-data 2>/dev/null || true

clean-large: ## 清理 Large 数据库
	docker compose stop pg-large
	docker compose rm -f pg-large
	docker volume rm -f pg-mcp-large-data 2>/dev/null || true

# =====================================================
# Database Shell Access
# =====================================================

shell-small: ## 进入 Small 数据库容器 shell
	docker compose exec pg-small /bin/sh

shell-medium: ## 进入 Medium 数据库容器 shell
	docker compose exec pg-medium /bin/sh

shell-large: ## 进入 Large 数据库容器 shell
	docker compose exec pg-large /bin/sh

psql-small: ## 连接到 Small 数据库 psql
	docker compose exec pg-small psql -U $(DB_USER) -d blog_db

psql-medium: ## 连接到 Medium 数据库 psql
	docker compose exec pg-medium psql -U $(DB_USER) -d ecommerce_db

psql-large: ## 连接到 Large 数据库 psql
	docker compose exec pg-large psql -U $(DB_USER) -d erp_db

# =====================================================
# Database Statistics
# =====================================================

stats: stats-small stats-medium stats-large ## 显示所有数据库统计信息

stats-small: ## 显示 Small 数据库统计
	@echo ""
	@echo "$(GREEN)=== Small Database (Blog System) ===$(NC)"
	@echo "Port: $(SMALL_PORT), Database: blog_db"
	@docker compose exec -T pg-small psql -U $(DB_USER) -d blog_db -c "\
		SELECT 'Tables' AS type, COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' \
		UNION ALL \
		SELECT 'Views', COUNT(*) FROM information_schema.views WHERE table_schema = 'public' \
		UNION ALL \
		SELECT 'Indexes', COUNT(*) FROM pg_indexes WHERE schemaname = 'public' \
		UNION ALL \
		SELECT 'Functions', COUNT(*) FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public'; \
	" 2>/dev/null || echo "Database not running"
	@docker compose exec -T pg-small psql -U $(DB_USER) -d blog_db -c "\
		SELECT relname AS table_name, n_live_tup AS row_count \
		FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 5; \
	" 2>/dev/null || true

stats-medium: ## 显示 Medium 数据库统计
	@echo ""
	@echo "$(GREEN)=== Medium Database (E-Commerce) ===$(NC)"
	@echo "Port: $(MEDIUM_PORT), Database: ecommerce_db"
	@docker compose exec -T pg-medium psql -U $(DB_USER) -d ecommerce_db -c "\
		SELECT 'Tables' AS type, COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' \
		UNION ALL \
		SELECT 'Views', COUNT(*) FROM information_schema.views WHERE table_schema = 'public' \
		UNION ALL \
		SELECT 'Indexes', COUNT(*) FROM pg_indexes WHERE schemaname = 'public' \
		UNION ALL \
		SELECT 'Custom Types', COUNT(*) FROM pg_type WHERE typnamespace = 'public'::regnamespace AND typtype = 'e'; \
	" 2>/dev/null || echo "Database not running"
	@docker compose exec -T pg-medium psql -U $(DB_USER) -d ecommerce_db -c "\
		SELECT relname AS table_name, n_live_tup AS row_count \
		FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 5; \
	" 2>/dev/null || true

stats-large: ## 显示 Large 数据库统计
	@echo ""
	@echo "$(GREEN)=== Large Database (ERP System) ===$(NC)"
	@echo "Port: $(LARGE_PORT), Database: erp_db"
	@docker compose exec -T pg-large psql -U $(DB_USER) -d erp_db -c "\
		SELECT table_schema, COUNT(*) AS table_count \
		FROM information_schema.tables \
		WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema') \
		GROUP BY table_schema ORDER BY table_schema; \
	" 2>/dev/null || echo "Database not running"
	@docker compose exec -T pg-large psql -U $(DB_USER) -d erp_db -c "\
		SELECT schemaname || '.' || relname AS table_name, n_live_tup AS row_count \
		FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 10; \
	" 2>/dev/null || true

# =====================================================
# pgAdmin (Database Management UI)
# =====================================================

up-admin: ## 启动 pgAdmin 管理界面
	@echo "$(GREEN)Starting pgAdmin...$(NC)"
	docker compose --profile admin up -d pgadmin
	@echo ""
	@echo "$(GREEN)pgAdmin is available at: http://localhost:5050$(NC)"
	@echo "  Email:    admin@example.com"
	@echo "  Password: admin"

down-admin: ## 停止 pgAdmin
	docker compose stop pgadmin
	docker compose rm -f pgadmin

# =====================================================
# Wait for Database
# =====================================================

wait-small: ## 等待 Small 数据库就绪
	@echo "Waiting for Small database to be ready..."
	@until docker compose exec -T pg-small pg_isready -U $(DB_USER) -d blog_db > /dev/null 2>&1; do \
		sleep 1; \
	done
	@echo "$(GREEN)Small database is ready!$(NC)"

wait-medium: ## 等待 Medium 数据库就绪
	@echo "Waiting for Medium database to be ready..."
	@until docker compose exec -T pg-medium pg_isready -U $(DB_USER) -d ecommerce_db > /dev/null 2>&1; do \
		sleep 1; \
	done
	@echo "$(GREEN)Medium database is ready!$(NC)"

wait-large: ## 等待 Large 数据库就绪
	@echo "Waiting for Large database to be ready..."
	@until docker compose exec -T pg-large pg_isready -U $(DB_USER) -d erp_db > /dev/null 2>&1; do \
		sleep 1; \
	done
	@echo "$(GREEN)Large database is ready!$(NC)"

wait: wait-small wait-medium wait-large ## 等待所有数据库就绪

# =====================================================
# Connection Strings (for reference)
# =====================================================

connection-info: ## 显示数据库连接信息
	@echo ""
	@echo "$(GREEN)Database Connection Strings:$(NC)"
	@echo ""
	@echo "$(YELLOW)Small (Blog System):$(NC)"
	@echo "  URL:  postgresql://$(DB_USER):$(DB_PASS)@localhost:$(SMALL_PORT)/blog_db"
	@echo "  psql: psql -h localhost -p $(SMALL_PORT) -U $(DB_USER) -d blog_db"
	@echo ""
	@echo "$(YELLOW)Medium (E-Commerce):$(NC)"
	@echo "  URL:  postgresql://$(DB_USER):$(DB_PASS)@localhost:$(MEDIUM_PORT)/ecommerce_db"
	@echo "  psql: psql -h localhost -p $(MEDIUM_PORT) -U $(DB_USER) -d ecommerce_db"
	@echo ""
	@echo "$(YELLOW)Large (ERP System):$(NC)"
	@echo "  URL:  postgresql://$(DB_USER):$(DB_PASS)@localhost:$(LARGE_PORT)/erp_db"
	@echo "  psql: psql -h localhost -p $(LARGE_PORT) -U $(DB_USER) -d erp_db"
	@echo ""
