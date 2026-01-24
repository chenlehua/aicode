"""Database service for pg-mcp."""

import logging
import time

import asyncpg

from pg_mcp.config import DatabaseConfig, QuerySettings
from pg_mcp.database.connection import ConnectionPool
from pg_mcp.database.schema_cache import SchemaCache
from pg_mcp.models import (
    DatabaseSchema,
    QueryResultData,
    SQLExecutionError,
    SQLTimeoutError,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Unified database service for schema caching and query execution.

    Args:
        config: Database connection configuration.
        query_settings: Query execution settings.
    """

    def __init__(
        self,
        config: DatabaseConfig,
        query_settings: QuerySettings,
    ) -> None:
        self.config = config
        self.query_settings = query_settings
        self._pool = ConnectionPool(config)
        self._schema_cache = SchemaCache(config.database)

    @property
    def schema(self) -> DatabaseSchema:
        """Get the cached database schema.

        Raises:
            RuntimeError: If schema has not been loaded yet.
        """
        if self._schema_cache.schema is None:
            raise RuntimeError("Schema not loaded. Call initialize() first.")
        return self._schema_cache.schema

    def get_table_names(self) -> set[str]:
        """Get all table names from the cached schema."""
        return self._schema_cache.get_table_names()

    async def initialize(self) -> None:
        """Initialize the database service.

        Creates the connection pool and loads the schema cache.
        """
        await self._pool.initialize()
        await self.refresh_schema()

    async def close(self) -> None:
        """Close the database service and release resources."""
        await self._pool.close()

    async def refresh_schema(self) -> DatabaseSchema:
        """Refresh the schema cache from the database.

        Returns:
            The updated DatabaseSchema.
        """
        async with self._pool.acquire() as conn:
            return await self._schema_cache.refresh(conn)

    async def execute_query(
        self,
        sql: str,
        limit: int | None = None,
    ) -> QueryResultData:
        """Execute a read-only SQL query.

        Args:
            sql: The SQL SELECT statement to execute.
            limit: Maximum number of rows to return. If not specified,
                   uses the default_limit from query settings.

        Returns:
            Query result containing columns, rows, and metadata.

        Raises:
            SQLExecutionError: If the query fails.
            SQLTimeoutError: If the query times out.
        """
        effective_limit = limit or self.query_settings.default_limit

        # Add LIMIT if not present in the query
        exec_sql = sql.rstrip(";")
        if "LIMIT" not in sql.upper():
            exec_sql = f"{exec_sql} LIMIT {effective_limit}"

        logger.debug(f"Executing query: {exec_sql[:200]}...")

        async with self._pool.acquire() as conn:
            try:
                # Set statement timeout
                await conn.execute(
                    f"SET statement_timeout = {self.query_settings.statement_timeout}"
                )

                start_time = time.perf_counter()
                rows = await conn.fetch(exec_sql)
                end_time = time.perf_counter()

                execution_time_ms = (end_time - start_time) * 1000

                if not rows:
                    return QueryResultData(
                        columns=[],
                        rows=[],
                        row_count=0,
                        execution_time_ms=execution_time_ms,
                    )

                # Extract column names from the first row
                columns = list(rows[0].keys())

                # Convert rows to list of lists
                result_rows = [list(row.values()) for row in rows]

                logger.info(
                    f"Query returned {len(result_rows)} rows in {execution_time_ms:.2f}ms"
                )

                return QueryResultData(
                    columns=columns,
                    rows=result_rows,
                    row_count=len(result_rows),
                    execution_time_ms=execution_time_ms,
                )

            except asyncpg.QueryCanceledError:
                raise SQLTimeoutError(
                    timeout_ms=self.query_settings.statement_timeout,
                    sql=sql,
                )
            except asyncpg.PostgresError as e:
                logger.error(f"SQL execution failed: {e}")
                raise SQLExecutionError(
                    message=str(e),
                    sql=sql,
                )
            except Exception as e:
                logger.exception("Unexpected error during query execution")
                raise SQLExecutionError(
                    message=f"Unexpected error: {e}",
                    sql=sql,
                )
