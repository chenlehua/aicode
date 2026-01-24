"""FastMCP server for pg-mcp."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any

from mcp.server.fastmcp import FastMCP

from pg_mcp.config import ConfigLoader, DatabaseConfig, Settings
from pg_mcp.database import DatabaseService
from pg_mcp.llm import LLMService
from pg_mcp.models import QueryRequest
from pg_mcp.query import QueryService
from pg_mcp.validator import SQLValidator

logger = logging.getLogger(__name__)

# Global service instances (set during lifespan)
_query_service: QueryService | None = None
_database_service: DatabaseService | None = None


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Server lifecycle management.

    Initializes and cleans up services.

    Yields:
        Empty context dict.
    """
    global _query_service, _database_service

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

    # Use the first database (v1 limitation)
    db_config: DatabaseConfig = databases[0]
    logger.info(f"Using database: {db_config.name}")

    # Initialize services
    _database_service = DatabaseService(db_config, settings.query)
    await _database_service.initialize()

    llm_service = LLMService(settings.llm)

    # Create validator with known tables
    table_names = _database_service.get_table_names()
    validator = SQLValidator(known_tables=table_names)

    # Create query service
    _query_service = QueryService(
        llm_service=llm_service,
        database_service=_database_service,
        validator=validator,
        query_settings=settings.query,
    )

    logger.info("pg-mcp server initialized successfully")

    try:
        yield {}
    finally:
        # Cleanup
        logger.info("Shutting down pg-mcp server...")
        if _database_service:
            await _database_service.close()
        logger.info("pg-mcp server shutdown complete")


def create_server() -> FastMCP:
    """Create and configure the FastMCP server.

    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP(
        "PostgreSQL MCP Server",
        instructions="Natural language database queries for PostgreSQL",
        lifespan=lifespan,
    )

    @mcp.tool()
    async def query(query: str) -> str:
        """根据自然语言描述查询数据库。

        将自然语言查询转换为 SQL，执行查询并返回结果。
        只支持 SELECT 查询，不允许修改数据。

        Args:
            query: 自然语言查询描述，例如 "查询最近一个月注册的用户数量"

        Returns:
            JSON 格式的查询结果，包含:
            - success: 是否成功
            - sql: 生成的 SQL 语句
            - result: 查询结果数据
            - validation: LLM 对结果的验证
            - error: 错误信息（如果失败）
        """
        if _query_service is None:
            return '{"success": false, "error": "服务未初始化"}'

        request = QueryRequest(query=query)
        response = await _query_service.execute(request)

        return response.model_dump_json(indent=2)

    @mcp.tool()
    async def refresh_schema() -> str:
        """刷新数据库 Schema 缓存。

        重新从数据库获取表结构信息，更新缓存。
        当数据库结构发生变化时使用此工具。

        Returns:
            刷新结果信息。
        """
        if _database_service is None:
            return '{"success": false, "error": "服务未初始化"}'

        try:
            schema = await _database_service.refresh_schema()
            return (
                f'{{"success": true, "message": "Schema 缓存已刷新", '
                f'"tables": {len(schema.tables)}, "views": {len(schema.views)}}}'
            )
        except Exception as e:
            logger.exception("Failed to refresh schema")
            return f'{{"success": false, "error": "刷新失败: {e}"}}'

    @mcp.tool()
    async def get_schema() -> str:
        """获取当前数据库的 Schema 信息。

        返回数据库的表、视图、列等结构信息。

        Returns:
            Schema 信息的文本描述。
        """
        if _database_service is None:
            return "服务未初始化"

        try:
            schema = _database_service.schema
            return schema.to_llm_context()
        except Exception as e:
            logger.exception("Failed to get schema")
            return f"获取 Schema 失败: {e}"

    return mcp


def main() -> None:
    """Main entry point for the server."""
    mcp = create_server()
    mcp.run()


if __name__ == "__main__":
    main()
