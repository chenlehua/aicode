"""Shared query execution logic."""

import re
from abc import ABC, abstractmethod
from typing import Any

import sqlglot
from sqlglot import exp

from app.core.types import QueryExecutor, SQLDialect


class BaseQueryExecutor(QueryExecutor, ABC):
    """
    Base implementation of QueryExecutor with shared logic.

    Subclasses only need to implement database-specific execution.
    """

    _max_rows: int = 1000

    @property
    def max_rows(self) -> int:
        return self._max_rows

    @property
    @abstractmethod
    def dialect(self) -> SQLDialect:
        """The SQL dialect this executor uses."""
        ...

    def validate_sql(self, sql: str) -> tuple[bool, str | None]:
        """
        Validate SQL syntax and ensure it's a SELECT query.

        Uses sqlglot with the appropriate dialect.
        """
        try:
            parsed_statements = sqlglot.parse(sql, dialect=self.dialect.value)

            if len(parsed_statements) > 1:
                return (
                    False,
                    "Multiple statements are not allowed. Please execute one SELECT query at a time.",
                )

            if not parsed_statements:
                return False, "Invalid SQL syntax: No valid statement found"

            parsed = parsed_statements[0]

            if not isinstance(parsed, exp.Select):
                return False, "Only SELECT queries are allowed"

            return True, None

        except Exception as e:
            error_msg = self._clean_error_message(str(e))
            return False, f"SQL syntax error: {error_msg}"

    def inject_limit(self, sql: str) -> str:
        """Inject LIMIT clause if not present."""
        try:
            parsed = sqlglot.parse_one(sql, dialect=self.dialect.value)

            if not isinstance(parsed, exp.Select):
                return sql

            if parsed.args.get("limit"):
                return sql

            limit_expr = exp.Limit(
                expression=exp.Literal(this=str(self.max_rows), is_string=False)
            )
            parsed.set("limit", limit_expr)
            return parsed.sql(dialect=self.dialect.value)

        except Exception:
            # Fallback to string manipulation
            if "LIMIT" not in sql.upper():
                return f"{sql.rstrip(';')} LIMIT {self.max_rows}"
            return sql

    @staticmethod
    def _clean_error_message(error_msg: str) -> str:
        """Remove ANSI escape codes from error messages."""
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return ansi_escape.sub("", error_msg)

    @abstractmethod
    async def execute(self, url: str, sql: str) -> Any:
        """Execute a SQL query and return results."""
        ...
