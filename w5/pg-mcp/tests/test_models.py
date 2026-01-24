"""Tests for pg-mcp models."""

import pytest
from datetime import datetime

from pg_mcp.models import (
    ColumnInfo,
    DatabaseSchema,
    ErrorCode,
    QueryError,
    QueryRequest,
    QueryResponse,
    QueryResultData,
    SQLGenerationError,
    SQLUnsafeError,
    TableInfo,
    ValidationResult,
)


class TestErrorModels:
    """Tests for error models."""

    def test_error_code_values(self) -> None:
        """Test that all error codes have expected values."""
        assert ErrorCode.SQL_GENERATION_FAILED.value == "SQL_GENERATION_FAILED"
        assert ErrorCode.SQL_UNSAFE.value == "SQL_UNSAFE"
        assert ErrorCode.SQL_EXECUTION_FAILED.value == "SQL_EXECUTION_FAILED"
        assert ErrorCode.SQL_TIMEOUT.value == "SQL_TIMEOUT"

    def test_query_error_str(self) -> None:
        """Test QueryError string representation."""
        error = QueryError(ErrorCode.INTERNAL_ERROR, "Something went wrong", "details")
        assert "[INTERNAL_ERROR]" in str(error)
        assert "Something went wrong" in str(error)
        assert "details" in str(error)

    def test_query_error_str_no_details(self) -> None:
        """Test QueryError string representation without details."""
        error = QueryError(ErrorCode.INTERNAL_ERROR, "Something went wrong")
        assert "[INTERNAL_ERROR]" in str(error)
        assert "Something went wrong" in str(error)

    def test_sql_generation_error(self) -> None:
        """Test SQLGenerationError creation."""
        error = SQLGenerationError("Failed to generate SQL")
        assert error.code == ErrorCode.SQL_GENERATION_FAILED
        assert error.message == "Failed to generate SQL"

    def test_sql_unsafe_error(self) -> None:
        """Test SQLUnsafeError creation."""
        error = SQLUnsafeError("Contains INSERT", "INSERT INTO users VALUES (1)")
        assert error.code == ErrorCode.SQL_UNSAFE
        assert error.sql == "INSERT INTO users VALUES (1)"


class TestQueryModels:
    """Tests for query request/response models."""

    def test_query_request_valid(self) -> None:
        """Test valid query request creation."""
        request = QueryRequest(query="Find all users")
        assert request.query == "Find all users"

    def test_query_request_empty_fails(self) -> None:
        """Test that empty query fails validation."""
        with pytest.raises(ValueError):
            QueryRequest(query="")

    def test_query_request_too_long_fails(self) -> None:
        """Test that too long query fails validation."""
        with pytest.raises(ValueError):
            QueryRequest(query="a" * 5000)

    def test_query_result_data(self) -> None:
        """Test QueryResultData creation."""
        result = QueryResultData(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            row_count=2,
            execution_time_ms=10.5,
        )
        assert result.columns == ["id", "name"]
        assert result.row_count == 2
        assert result.execution_time_ms == 10.5

    def test_validation_result(self) -> None:
        """Test ValidationResult creation."""
        result = ValidationResult(passed=True, message="OK")
        assert result.passed is True
        assert result.message == "OK"

    def test_query_response_success(self) -> None:
        """Test successful QueryResponse creation."""
        response = QueryResponse(
            success=True,
            sql="SELECT * FROM users",
            result=QueryResultData(
                columns=["id"],
                rows=[[1]],
                row_count=1,
                execution_time_ms=5.0,
            ),
        )
        assert response.success is True
        assert response.sql == "SELECT * FROM users"
        assert response.result is not None
        assert response.error is None

    def test_query_response_error(self) -> None:
        """Test error QueryResponse creation."""
        response = QueryResponse(
            success=False,
            error="Query failed",
            error_code=ErrorCode.SQL_EXECUTION_FAILED.value,
        )
        assert response.success is False
        assert response.error == "Query failed"
        assert response.sql is None


class TestSchemaModels:
    """Tests for schema models."""

    def test_column_info_defaults(self) -> None:
        """Test ColumnInfo default values."""
        col = ColumnInfo(name="id", data_type="integer")
        assert col.is_nullable is True
        assert col.is_primary_key is False
        assert col.is_foreign_key is False
        assert col.default_value is None

    def test_table_info_full_name(self) -> None:
        """Test TableInfo full_name property."""
        table = TableInfo(schema_name="public", name="users", columns=[])
        assert table.full_name == "public.users"

    def test_database_schema_to_llm_context(self) -> None:
        """Test DatabaseSchema.to_llm_context() method."""
        schema = DatabaseSchema(
            database_name="testdb",
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
                        ColumnInfo(
                            name="name",
                            data_type="varchar",
                            is_nullable=True,
                        ),
                    ],
                ),
            ],
        )

        context = schema.to_llm_context()

        assert "testdb" in context
        assert "users" in context
        assert "id" in context
        assert "integer" in context
        assert "PK" in context

    def test_database_schema_get_table_names(self) -> None:
        """Test DatabaseSchema.get_table_names() method."""
        schema = DatabaseSchema(
            database_name="testdb",
            tables=[
                TableInfo(schema_name="public", name="users", columns=[]),
                TableInfo(schema_name="public", name="orders", columns=[]),
            ],
        )

        names = schema.get_table_names()

        assert "users" in names
        assert "orders" in names
        assert "public.users" in names
        assert "public.orders" in names
