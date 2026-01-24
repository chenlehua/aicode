"""Shared test fixtures for pg-mcp tests."""

import os
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


# ============ Pytest Hooks ============


def pytest_collection_modifyitems(config, items):
    """Automatically add markers based on test path."""
    for item in items:
        # Add markers based on directory
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


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


@pytest.fixture
def sample_empty_result() -> QueryResultData:
    """Sample empty query result for testing."""
    return QueryResultData(
        columns=[],
        rows=[],
        row_count=0,
        execution_time_ms=5.0,
    )


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Mock OpenAI client for LLM testing."""
    client = MagicMock()

    # Mock successful SQL generation response
    sql_response = MagicMock()
    sql_response.choices = [MagicMock()]
    sql_response.choices[0].message.content = "SELECT * FROM users"

    # Mock successful validation response
    validation_response = MagicMock()
    validation_response.choices = [MagicMock()]
    validation_response.choices[0].message.content = '{"passed": true, "message": "验证通过"}'

    client.chat.completions.create = AsyncMock(return_value=sql_response)

    return client


# ============ Database Integration Test Fixtures ============


@pytest.fixture
def test_db_config() -> DatabaseConfig:
    """Database config for integration tests.

    Uses environment variables or defaults for test database connection.
    """
    return DatabaseConfig(
        name="test_integration",
        host=os.environ.get("TEST_DB_HOST", "localhost"),
        port=int(os.environ.get("TEST_DB_PORT", "5433")),
        database=os.environ.get("TEST_DB_NAME", "testdb"),
        user=os.environ.get("TEST_DB_USER", "testuser"),
        password=os.environ.get("TEST_DB_PASSWORD", "testpass"),
    )


@pytest.fixture
def sample_column_info() -> ColumnInfo:
    """Sample column info for testing."""
    return ColumnInfo(
        name="id",
        data_type="integer",
        is_nullable=False,
        is_primary_key=True,
    )


@pytest.fixture
def sample_table_info() -> TableInfo:
    """Sample table info for testing."""
    return TableInfo(
        schema_name="public",
        name="users",
        columns=[
            ColumnInfo(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
            ColumnInfo(name="name", data_type="varchar", is_nullable=False),
            ColumnInfo(name="email", data_type="varchar", is_nullable=False),
            ColumnInfo(name="created_at", data_type="timestamp", is_nullable=False),
        ],
        comment="User accounts table",
    )
