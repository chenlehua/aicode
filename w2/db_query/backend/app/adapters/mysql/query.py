"""MySQL query execution."""

import time
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.adapters.shared.query_base import BaseQueryExecutor
from app.core.types import SQLDialect
from app.models.query import ColumnInfo, QueryResult


def _infer_mysql_type(value: Any) -> str:
    """Infer MySQL type name from Python value."""
    if value is None:
        return "unknown"
    type_map = {
        int: "int",
        float: "double",
        bool: "tinyint",
        str: "varchar",
        bytes: "blob",
        dict: "json",
        list: "json",
        Decimal: "decimal",
    }
    return type_map.get(type(value), "unknown")


class MySQLQueryExecutor(BaseQueryExecutor):
    """MySQL query executor."""

    def __init__(self, connection_provider: Any) -> None:
        self._connection_provider = connection_provider

    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.MYSQL

    async def execute(self, url: str, sql: str) -> QueryResult:
        """Execute a SQL query against MySQL."""
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
                async with conn.cursor() as cursor:
                    # Execute query
                    await cursor.execute(sql_with_limit)
                    rows = await cursor.fetchall()

                    # Get column descriptions
                    if cursor.description:
                        column_names = [desc[0] for desc in cursor.description]
                        # Infer types from first row if available
                        if rows:
                            columns = [
                                ColumnInfo(
                                    name=name, data_type=_infer_mysql_type(rows[0][i])
                                )
                                for i, name in enumerate(column_names)
                            ]
                        else:
                            columns = [
                                ColumnInfo(name=name, data_type="unknown")
                                for name in column_names
                            ]
                    else:
                        columns = []

                    # Convert rows to lists, handling special types
                    def serialize_value(value: Any) -> Any:
                        """Convert non-serializable values to strings."""
                        if isinstance(value, datetime):
                            return value.isoformat()
                        if isinstance(value, Decimal):
                            return float(value)
                        if isinstance(value, bytes):
                            return value.decode("utf-8", errors="replace")
                        return value

                    row_data = [[serialize_value(val) for val in row] for row in rows]

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
