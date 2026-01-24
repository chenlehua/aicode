"""Tests for query service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from pg_mcp.config import QuerySettings
from pg_mcp.models import (
    ErrorCode,
    QueryRequest,
    QueryResultData,
    SQLGenerationError,
    SQLUnsafeError,
    ValidationResult,
)
from pg_mcp.query import QueryService
from pg_mcp.validator import SQLValidator


class TestQueryService:
    """Tests for QueryService."""

    @pytest.fixture
    def query_settings(self) -> QuerySettings:
        """Create query settings for testing."""
        return QuerySettings(
            default_limit=100,
            statement_timeout=30000,
            enable_validation=True,
        )

    @pytest.fixture
    def mock_llm(self) -> MagicMock:
        """Create a mock LLM service."""
        llm = MagicMock()
        llm.generate_sql = AsyncMock(return_value="SELECT * FROM users")
        llm.validate_result = AsyncMock(
            return_value=ValidationResult(passed=True, message="OK")
        )
        return llm

    @pytest.fixture
    def mock_db(self, sample_schema, sample_query_result) -> MagicMock:
        """Create a mock database service."""
        db = MagicMock()
        db.schema = sample_schema
        db.execute_query = AsyncMock(return_value=sample_query_result)
        return db

    @pytest.fixture
    def validator(self) -> SQLValidator:
        """Create a SQL validator."""
        return SQLValidator()

    @pytest.fixture
    def service(
        self,
        mock_llm: MagicMock,
        mock_db: MagicMock,
        validator: SQLValidator,
        query_settings: QuerySettings,
    ) -> QueryService:
        """Create a QueryService instance."""
        return QueryService(
            llm_service=mock_llm,
            database_service=mock_db,
            validator=validator,
            query_settings=query_settings,
        )

    @pytest.mark.asyncio
    async def test_execute_success(self, service: QueryService) -> None:
        """Test successful query execution."""
        request = QueryRequest(query="Find all users")

        response = await service.execute(request)

        assert response.success is True
        assert response.sql == "SELECT * FROM users"
        assert response.result is not None
        assert response.result.row_count == 2
        assert response.validation is not None
        assert response.validation.passed is True
        assert response.error is None

    @pytest.mark.asyncio
    async def test_execute_without_validation(
        self,
        mock_llm: MagicMock,
        mock_db: MagicMock,
        validator: SQLValidator,
    ) -> None:
        """Test query execution without LLM validation."""
        settings = QuerySettings(enable_validation=False)
        service = QueryService(
            llm_service=mock_llm,
            database_service=mock_db,
            validator=validator,
            query_settings=settings,
        )

        request = QueryRequest(query="Find all users")
        response = await service.execute(request)

        assert response.success is True
        assert response.validation is None
        mock_llm.validate_result.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_sql_generation_error(
        self,
        mock_llm: MagicMock,
        mock_db: MagicMock,
        validator: SQLValidator,
        query_settings: QuerySettings,
    ) -> None:
        """Test handling of SQL generation errors."""
        mock_llm.generate_sql = AsyncMock(
            side_effect=SQLGenerationError("Failed to generate SQL")
        )
        service = QueryService(
            llm_service=mock_llm,
            database_service=mock_db,
            validator=validator,
            query_settings=query_settings,
        )

        request = QueryRequest(query="Invalid query")
        response = await service.execute(request)

        assert response.success is False
        assert response.error_code == ErrorCode.SQL_GENERATION_FAILED.value
        assert "Failed to generate SQL" in response.error

    @pytest.mark.asyncio
    async def test_execute_unsafe_sql(
        self,
        mock_llm: MagicMock,
        mock_db: MagicMock,
        query_settings: QuerySettings,
    ) -> None:
        """Test handling of unsafe SQL."""
        mock_llm.generate_sql = AsyncMock(
            return_value="DROP TABLE users"
        )
        validator = SQLValidator()
        service = QueryService(
            llm_service=mock_llm,
            database_service=mock_db,
            validator=validator,
            query_settings=query_settings,
        )

        request = QueryRequest(query="Delete everything")
        response = await service.execute(request)

        assert response.success is False
        assert response.error_code == ErrorCode.SQL_UNSAFE.value

    @pytest.mark.asyncio
    async def test_execute_unexpected_error(
        self,
        mock_llm: MagicMock,
        mock_db: MagicMock,
        validator: SQLValidator,
        query_settings: QuerySettings,
    ) -> None:
        """Test handling of unexpected errors."""
        mock_llm.generate_sql = AsyncMock(
            side_effect=RuntimeError("Unexpected error")
        )
        service = QueryService(
            llm_service=mock_llm,
            database_service=mock_db,
            validator=validator,
            query_settings=query_settings,
        )

        request = QueryRequest(query="Some query")
        response = await service.execute(request)

        assert response.success is False
        assert response.error_code == ErrorCode.INTERNAL_ERROR.value
        assert "内部错误" in response.error
