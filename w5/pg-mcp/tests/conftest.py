"""Shared test fixtures for pg-mcp tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from pg_mcp.config import DatabaseConfig, LLMSettings, QuerySettings
from pg_mcp.models import (
    ColumnInfo,
    DatabaseSchema,
    QueryResultData,
    TableInfo,
    ValidationResult,
)


@pytest.fixture
def sample_llm_settings() -> LLMSettings:
    """Create sample LLM settings for testing."""
    return LLMSettings(
        api_key="test-api-key",
        base_url="https://api.example.com/v1",
        model="test-model",
        temperature=0.1,
        timeout=30.0,
        max_tokens=2048,
    )


@pytest.fixture
def sample_query_settings() -> QuerySettings:
    """Create sample query settings for testing."""
    return QuerySettings(
        default_limit=100,
        statement_timeout=30000,
        enable_validation=True,
    )


@pytest.fixture
def sample_database_config() -> DatabaseConfig:
    """Create sample database configuration for testing."""
    return DatabaseConfig(
        name="test_db",
        host="localhost",
        port=5432,
        database="testdb",
        user="testuser",
        password="testpass",
        min_pool_size=2,
        max_pool_size=5,
        ssl=False,
    )


@pytest.fixture
def sample_schema() -> DatabaseSchema:
    """Create a sample database schema for testing."""
    return DatabaseSchema(
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
                        is_nullable=False,
                    ),
                    ColumnInfo(
                        name="email",
                        data_type="varchar",
                        is_nullable=False,
                    ),
                    ColumnInfo(
                        name="created_at",
                        data_type="timestamp",
                        is_nullable=False,
                    ),
                ],
                comment="User accounts table",
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
                        is_nullable=False,
                        is_foreign_key=True,
                        foreign_table="public.users",
                        foreign_column="id",
                    ),
                    ColumnInfo(
                        name="total",
                        data_type="numeric",
                        is_nullable=False,
                    ),
                ],
                comment="Customer orders",
            ),
        ],
    )


@pytest.fixture
def sample_query_result() -> QueryResultData:
    """Create a sample query result for testing."""
    return QueryResultData(
        columns=["id", "name", "email"],
        rows=[
            [1, "Alice", "alice@example.com"],
            [2, "Bob", "bob@example.com"],
        ],
        row_count=2,
        execution_time_ms=15.5,
    )


@pytest.fixture
def mock_llm_service(sample_query_result: QueryResultData) -> MagicMock:
    """Create a mock LLM service."""
    service = MagicMock()
    service.generate_sql = AsyncMock(return_value="SELECT * FROM users")
    service.validate_result = AsyncMock(
        return_value=ValidationResult(
            passed=True,
            message="查询结果符合预期",
        )
    )
    return service


@pytest.fixture
def mock_database_service(
    sample_schema: DatabaseSchema,
    sample_query_result: QueryResultData,
) -> MagicMock:
    """Create a mock database service."""
    service = MagicMock()
    service.schema = sample_schema
    service.get_table_names = MagicMock(return_value={"users", "orders", "public.users", "public.orders"})
    service.execute_query = AsyncMock(return_value=sample_query_result)
    return service
