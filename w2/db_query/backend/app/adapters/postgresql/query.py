"""PostgreSQL query execution."""

import time
from datetime import datetime
from typing import Any

from app.adapters.shared.query_base import BaseQueryExecutor
from app.core.types import SQLDialect
from app.models.query import ColumnInfo, QueryResult


def _infer_pg_type(value: Any) -> str:
    """Infer PostgreSQL type name from Python value."""
    if value is None:
        return "unknown"
    pg_type_map = {
        int: "integer",
        float: "numeric",
        bool: "boolean",
        str: "text",
        bytes: "bytea",
        dict: "jsonb",
        list: "array",
    }
    return pg_type_map.get(type(value), "unknown")


class PostgreSQLQueryExecutor(BaseQueryExecutor):
    """PostgreSQL query executor."""

    def __init__(self, connection_provider: Any) -> None:
        self._connection_provider = connection_provider

    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.POSTGRES

    async def execute(self, url: str, sql: str) -> QueryResult:
        """Execute a SQL query against PostgreSQL."""
        start_time = time.time()

        # Validate SQL
        is_valid, error_msg = self.validate_sql(sql)
        if not is_valid:
            raise ValueError(error_msg or "Invalid SQL")

        # Inject LIMIT if needed
        sql_with_limit = self.inject_limit(sql)
        truncated = sql != sql_with_limit

        # Get connection pool
        pool = await self._connection_provider.get_pool(url)

        try:
            async with pool.acquire() as conn:
                # Execute query
                rows = await conn.fetch(sql_with_limit)

                # Get column information from first row or empty result handling
                if rows:
                    # Get column names from record keys
                    column_names = list(rows[0].keys())
                    # Infer types from first row values
                    columns = [
                        ColumnInfo(name=name, data_type=_infer_pg_type(rows[0][name]))
                        for name in column_names
                    ]
                else:
                    # Empty result set - need column info
                    # Try to get it by executing with LIMIT 0
                    try:
                        # Modify query to get column info without data
                        test_sql = (
                            sql_with_limit.replace("LIMIT", "LIMIT 0")
                            if "LIMIT" in sql_with_limit.upper()
                            else f"{sql_with_limit} LIMIT 0"
                        )
                        test_rows = await conn.fetch(test_sql)
                        if test_rows:
                            column_names = list(test_rows[0].keys())
                            columns = [
                                ColumnInfo(name=name, data_type="unknown")
                                for name in column_names
                            ]
                        else:
                            columns = []
                    except Exception:
                        columns = []

                # Convert rows to lists, handling datetime serialization
                def serialize_value(value: Any) -> Any:
                    """Convert non-serializable values to strings."""
                    if isinstance(value, datetime):
                        return value.isoformat()
                    return value

                row_data = [
                    [serialize_value(val) for val in row.values()] for row in rows
                ]

                execution_time_ms = int((time.time() - start_time) * 1000)

                return QueryResult(
                    columns=columns,
                    rows=row_data,
                    row_count=len(row_data),
                    truncated=truncated,
                    execution_time_ms=execution_time_ms,
                )
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {str(e)}") from e
