"""SQL query execution and validation."""

import time
from datetime import datetime
from typing import Any

import sqlglot
from sqlglot import exp

from app.models.query import ColumnInfo, QueryResult
from app.services.connection import ConnectionService


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


class QueryService:
    """Service for executing and validating SQL queries."""

    MAX_ROWS = 1000

    @staticmethod
    def validate_sql(sql: str) -> tuple[bool, str | None]:
        """Validate SQL syntax and ensure it's a SELECT query."""
        try:
            # Parse all statements to detect multiple statements
            parsed_statements = sqlglot.parse(sql, dialect="postgres")
            
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
            import re
            # Remove ANSI escape sequences
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_msg = ansi_escape.sub('', error_msg)
            return False, f"SQL syntax error: {error_msg}"

    @staticmethod
    def inject_limit(sql: str) -> str:
        """Inject LIMIT clause if not present."""
        try:
            parsed = sqlglot.parse_one(sql, dialect="postgres")
            if not isinstance(parsed, exp.Select):
                return sql

            # Check if LIMIT already exists
            if parsed.args.get("limit"):
                return sql

            # Add LIMIT using Limit expression
            limit_expr = exp.Limit(expression=exp.Literal(this=str(QueryService.MAX_ROWS), is_string=False))
            parsed.set("limit", limit_expr)
            return parsed.sql(dialect="postgres")
        except Exception:
            # If parsing fails, try simple string manipulation as fallback
            sql_upper = sql.upper().strip()
            if "LIMIT" not in sql_upper:
                # Simple fallback: append LIMIT at the end
                return f"{sql.rstrip(';')} LIMIT {QueryService.MAX_ROWS}"
            return sql

    @staticmethod
    async def execute_query(database_name: str, url: str, sql: str) -> QueryResult:
        """Execute a SQL query against PostgreSQL."""
        start_time = time.time()

        # Validate SQL
        is_valid, error_msg = QueryService.validate_sql(sql)
        if not is_valid:
            raise ValueError(error_msg or "Invalid SQL")

        # Inject LIMIT if needed
        sql_with_limit = QueryService.inject_limit(sql)
        truncated = sql != sql_with_limit

        # Get connection pool
        pool = await ConnectionService.get_pool(url)

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
                                ColumnInfo(name=name, data_type="unknown") for name in column_names
                            ]
                        else:
                            columns = []
                    except Exception:
                        # If that fails, try to parse column names from SQL
                        # This is a fallback - not perfect but better than nothing
                        columns = []

                # Convert rows to lists, handling datetime serialization
                def serialize_value(value: Any) -> Any:
                    """Convert non-serializable values to strings."""
                    if isinstance(value, datetime):
                        return value.isoformat()
                    return value

                row_data = [[serialize_value(val) for val in row.values()] for row in rows]

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
