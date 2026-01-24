"""SQL safety validation using SQLGlot."""

import logging

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from pg_mcp.models import SQLUnsafeError

logger = logging.getLogger(__name__)


class SQLValidator:
    """Validates SQL statements for safety.

    Uses SQLGlot to parse SQL and check for dangerous operations.
    Only SELECT statements are allowed.

    Args:
        known_tables: Optional set of known table names for validation.
    """

    # Only SELECT statements are allowed
    ALLOWED_STATEMENT_TYPES: tuple[type, ...] = (exp.Select,)

    # Dangerous statement types that must be blocked
    DANGEROUS_EXPRESSION_TYPES: tuple[type, ...] = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Merge,
        exp.Create,
        exp.Alter,
        exp.Drop,
        exp.TruncateTable,
        exp.Grant,
        exp.Revoke,
        exp.Command,
    )

    # Dangerous PostgreSQL functions that could access filesystem or external resources
    DANGEROUS_FUNCTIONS: set[str] = {
        # File system access
        "pg_read_file",
        "pg_read_binary_file",
        "pg_ls_dir",
        "pg_stat_file",
        # Large object operations
        "lo_import",
        "lo_export",
        "lo_create",
        "lo_open",
        "lo_write",
        "lo_put",
        "lo_get",
        # External connections
        "dblink",
        "dblink_exec",
        "dblink_connect",
        "dblink_send_query",
        # Copy operations
        "copy",
        # System commands
        "pg_execute_server_program",
    }

    def __init__(self, known_tables: set[str] | None = None) -> None:
        self.known_tables = known_tables or set()

    def validate(self, sql: str) -> str:
        """Validate a SQL statement for safety.

        Args:
            sql: The SQL statement to validate.

        Returns:
            The validated SQL statement (unchanged if valid).

        Raises:
            SQLUnsafeError: If the SQL is unsafe or invalid.
        """
        if not sql or not sql.strip():
            raise SQLUnsafeError("空 SQL 语句", sql)

        try:
            statements = sqlglot.parse(sql, dialect="postgres")
        except ParseError as e:
            logger.warning(f"SQL parse error: {e}")
            raise SQLUnsafeError(f"SQL 语法错误: {e}", sql)

        if not statements:
            raise SQLUnsafeError("无法解析 SQL 语句", sql)

        if len(statements) > 1:
            raise SQLUnsafeError("不允许多条 SQL 语句", sql)

        statement = statements[0]

        if statement is None:
            raise SQLUnsafeError("无法解析 SQL 语句", sql)

        # Check statement type
        if not isinstance(statement, self.ALLOWED_STATEMENT_TYPES):
            stmt_type = type(statement).__name__
            raise SQLUnsafeError(f"只允许 SELECT 查询语句，收到: {stmt_type}", sql)

        # Check for dangerous expressions in the AST
        self._check_dangerous_expressions(statement, sql)

        # Check for dangerous function calls
        self._check_dangerous_functions(statement, sql)

        # Optionally check table references
        if self.known_tables:
            self._check_table_references(statement, sql)

        logger.debug(f"SQL validation passed: {sql[:100]}...")
        return sql

    def is_select_only(self, sql: str) -> bool:
        """Check if SQL is a single SELECT statement.

        Args:
            sql: The SQL statement to check.

        Returns:
            True if the SQL is a valid single SELECT statement.
        """
        try:
            self.validate(sql)
            return True
        except SQLUnsafeError:
            return False

    def _check_dangerous_expressions(self, statement: exp.Expression, sql: str) -> None:
        """Check for dangerous expression types in the AST.

        Args:
            statement: The parsed SQL statement.
            sql: Original SQL string for error reporting.

        Raises:
            SQLUnsafeError: If dangerous expressions are found.
        """
        for node in statement.walk():
            if isinstance(node, self.DANGEROUS_EXPRESSION_TYPES):
                node_type = type(node).__name__
                raise SQLUnsafeError(
                    f"包含不允许的操作: {node_type}",
                    sql,
                )

    def _check_dangerous_functions(self, statement: exp.Expression, sql: str) -> None:
        """Check for dangerous function calls in the AST.

        Args:
            statement: The parsed SQL statement.
            sql: Original SQL string for error reporting.

        Raises:
            SQLUnsafeError: If dangerous functions are found.
        """
        for node in statement.walk():
            if isinstance(node, exp.Func):
                func_name = node.name.lower() if node.name else ""
                if func_name in self.DANGEROUS_FUNCTIONS:
                    raise SQLUnsafeError(
                        f"包含不允许的函数: {func_name}",
                        sql,
                    )

            # Also check for Anonymous functions (function calls by name)
            if isinstance(node, exp.Anonymous):
                func_name = node.this.lower() if isinstance(node.this, str) else ""
                if func_name in self.DANGEROUS_FUNCTIONS:
                    raise SQLUnsafeError(
                        f"包含不允许的函数: {func_name}",
                        sql,
                    )

    def _check_table_references(self, statement: exp.Expression, sql: str) -> None:
        """Check that all table references exist in known tables.

        Args:
            statement: The parsed SQL statement.
            sql: Original SQL string for error reporting.

        Raises:
            SQLUnsafeError: If unknown tables are referenced.
        """
        for node in statement.walk():
            if isinstance(node, exp.Table):
                table_name = node.name
                schema_name = node.db

                # Check both with and without schema prefix
                full_name = f"{schema_name}.{table_name}" if schema_name else table_name

                if table_name not in self.known_tables and full_name not in self.known_tables:
                    raise SQLUnsafeError(
                        f"引用未知的表: {full_name or table_name}",
                        sql,
                    )
