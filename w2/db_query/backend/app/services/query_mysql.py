"""SQL query execution and validation for MySQL."""

import re
import time
from datetime import datetime
from decimal import Decimal
from typing import Any

import sqlglot
from sqlglot import exp

from app.models.query import ColumnInfo, QueryResult
from app.services.connection_mysql import MySQLConnectionService


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


class MySQLQueryService:
    """Service for executing and validating SQL queries against MySQL."""

    MAX_ROWS = 1000

    @staticmethod
    def validate_sql(sql: str) -> tuple[bool, str | None]:
        """Validate SQL syntax and ensure it's a SELECT query."""
        try:
            # Parse all statements to detect multiple statements
            parsed_statements = sqlglot.parse(sql, dialect="mysql")

            # Check if there are multiple statements
            if len(parsed_statements) > 1:
                return False, "Multiple statements are not allowed. Please execute one SELECT query at a time."

            # Get the single statement
            if not parsed_statements:
                return False, "Invalid SQL syntax: No valid statement found"

            parsed = parsed_statements[0]

            # Check if it's a SELECT query
            if not isinstance(parsed, exp.Select):
                return False, "Only SELECT queries are allowed"

            return True, None
        except Exception as e:
            # Clean ANSI escape codes from error messages
            error_msg = str(e)
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_msg = ansi_escape.sub('', error_msg)
            return False, f"SQL syntax error: {error_msg}"

    @staticmethod
    def inject_limit(sql: str) -> str:
        """Inject LIMIT clause if not present."""
        try:
            parsed = sqlglot.parse_one(sql, dialect="mysql")
            if not isinstance(parsed, exp.Select):
                return sql

            # Check if LIMIT already exists
            if parsed.args.get("limit"):
                return sql

            # Add LIMIT using Limit expression
            limit_expr = exp.Limit(expression=exp.Literal(this=str(MySQLQueryService.MAX_ROWS), is_string=False))
            parsed.set("limit", limit_expr)
            return parsed.sql(dialect="mysql")
        except Exception:
            # If parsing fails, try simple string manipulation as fallback
            sql_upper = sql.upper().strip()
            if "LIMIT" not in sql_upper:
                # Simple fallback: append LIMIT at the end
                return f"{sql.rstrip(';')} LIMIT {MySQLQueryService.MAX_ROWS}"
            return sql

    @staticmethod
    async def execute_query(database_name: str, url: str, sql: str) -> QueryResult:
        """Execute a SQL query against MySQL."""
        start_time = time.time()

        # Validate SQL
        is_valid, error_msg = MySQLQueryService.validate_sql(sql)
        if not is_valid:
            raise ValueError(error_msg or "Invalid SQL")

        # Inject LIMIT if needed
        sql_with_limit = MySQLQueryService.inject_limit(sql)
        truncated = sql != sql_with_limit

        # Get connection pool
        pool = await MySQLConnectionService.get_pool(url)

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
                                ColumnInfo(name=name, data_type=_infer_mysql_type(rows[0][i]))
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
