"""FastMCP server for pg-mcp."""

import json
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any

from mcp.server.fastmcp import FastMCP

from pg_mcp.config import ConfigLoader, Settings
from pg_mcp.database import DatabaseService
from pg_mcp.llm import LLMService
from pg_mcp.models import QueryRequest
from pg_mcp.query import QueryService
from pg_mcp.validator import SQLValidator

logger = logging.getLogger(__name__)

# Global service instances (set during lifespan)
# Support multiple databases: {db_name: QueryService}
_query_services: dict[str, QueryService] = {}
_database_services: dict[str, DatabaseService] = {}
_database_names: list[str] = []


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Server lifecycle management.

    Initializes and cleans up services for all configured databases.

    Yields:
        Empty context dict.
    """
    global _query_services, _database_services, _database_names

    logger.info("Starting pg-mcp server...")

    # Load settings
    settings = Settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load database configuration
    if not settings.config_path:
        logger.error("PG_MCP_CONFIG_PATH environment variable not set")
        raise RuntimeError("PG_MCP_CONFIG_PATH environment variable is required")

    databases = ConfigLoader.load_databases(settings.config_path)
    if not databases:
        raise RuntimeError("No database configurations found")

    # Shared LLM service for all databases
    llm_service = LLMService(settings.llm)

    # Initialize all databases
    for db_config in databases:
        logger.info(f"Initializing database: {db_config.name}")

        try:
            # Initialize database service
            db_service = DatabaseService(db_config, settings.query)
            await db_service.initialize()
            _database_services[db_config.name] = db_service

            # Create validator with known tables
            table_names = db_service.get_table_names()
            validator = SQLValidator(known_tables=table_names)

            # Create query service
            query_service = QueryService(
                llm_service=llm_service,
                database_service=db_service,
                validator=validator,
                query_settings=settings.query,
            )
            _query_services[db_config.name] = query_service
            _database_names.append(db_config.name)
            logger.info(f"Database {db_config.name} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database {db_config.name}: {e}")
            # Continue with other databases

    if not _database_names:
        raise RuntimeError("No databases could be initialized")

    logger.info(f"pg-mcp server initialized with {len(_database_names)} database(s): {_database_names}")

    try:
        yield {}
    finally:
        # Cleanup all databases
        logger.info("Shutting down pg-mcp server...")
        for name, db_service in _database_services.items():
            logger.info(f"Closing database: {name}")
            await db_service.close()
        _query_services.clear()
        _database_services.clear()
        _database_names.clear()
        logger.info("pg-mcp server shutdown complete")


def _get_database_name(database: str | None) -> str | None:
    """Get valid database name or return None if invalid.

    Args:
        database: Database name or None for default.

    Returns:
        Valid database name or None if error.
    """
    if not _database_names:
        return None

    if database is None or database == "":
        return _database_names[0]

    if database in _query_services:
        return database

    return None


def create_server() -> FastMCP:
    """Create and configure the FastMCP server.

    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP(
        "PostgreSQL MCP Server",
        instructions="Natural language database queries for PostgreSQL. 支持的数据库: blog_db (博客系统), ecommerce_db (电商平台), erp_db (企业ERP)",
        lifespan=lifespan,
    )

    @mcp.tool()
    async def query(question: str, database: str = "") -> str:
        """根据自然语言描述查询数据库。

        将自然语言查询转换为 SQL，执行查询并返回结果。
        只支持 SELECT 查询，不允许修改数据。

        Args:
            question: 自然语言查询描述，例如 "查询最近一个月注册的用户数量"
            database: 目标数据库名称。可选值:
                - blog_db: 博客系统数据库
                - ecommerce_db: 电商平台数据库
                - erp_db: 企业ERP系统数据库
                不指定则使用 blog_db。

        Returns:
            JSON 格式的查询结果，包含:
            - success: 是否成功
            - database: 查询的数据库
            - sql: 生成的 SQL 语句
            - result: 查询结果数据
            - error: 错误信息（如果失败）
        """
        if not _query_services:
            return json.dumps({
                "success": False,
                "error": "服务未初始化，请检查数据库连接"
            }, ensure_ascii=False)

        db_name = _get_database_name(database if database else None)
        if db_name is None:
            available = ", ".join(_database_names)
            return json.dumps({
                "success": False,
                "error": f"数据库 '{database}' 不存在。可用数据库: {available}"
            }, ensure_ascii=False)

        try:
            query_service = _query_services[db_name]
            request = QueryRequest(query=question)
            response = await query_service.execute(request)

            # Add database name to response
            result = response.model_dump()
            result["database"] = db_name
            return json.dumps(result, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.exception("Query execution failed")
            return json.dumps({
                "success": False,
                "database": db_name,
                "error": f"查询失败: {e}"
            }, ensure_ascii=False)

    return mcp


def create_http_app():
    """Create HTTP ASGI application for uvicorn deployment.

    Returns:
        ASGI application that can be run with uvicorn.
    """
    mcp = create_server()
    return mcp.streamable_http_app()


def main() -> None:
    """Main entry point for the server."""
    import sys
    import os

    # Configure logging early
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    mcp = create_server()

    # Check if HTTP mode is requested via command line or environment variable
    use_http = "--http" in sys.argv or os.environ.get("PG_MCP_HTTP", "").lower() == "true"

    if use_http:
        # HTTP mode using uvicorn
        import uvicorn
        host = os.environ.get("PG_MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("PG_MCP_PORT", "8000"))
        logger.info(f"Starting pg-mcp HTTP server on {host}:{port}")

        # Create and run the HTTP app
        app = mcp.streamable_http_app()
        uvicorn.run(app, host=host, port=port, log_level="info")
    else:
        # Default STDIO mode for local MCP clients
        mcp.run()


if __name__ == "__main__":
    main()
