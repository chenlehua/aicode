"""Tests for LLM service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pg_mcp.config import LLMSettings
from pg_mcp.llm import LLMService
from pg_mcp.models import (
    DatabaseSchema,
    LLMError,
    QueryResultData,
    SQLGenerationError,
    TableInfo,
    ColumnInfo,
    ValidationResult,
)


class TestLLMService:
    """Tests for LLMService."""

    @pytest.fixture
    def llm_settings(self) -> LLMSettings:
        """Create LLM settings for testing."""
        return LLMSettings(
            api_key="test-api-key",
            base_url="https://api.example.com/v1",
            model="test-model",
            temperature=0.1,
            timeout=30.0,
            max_tokens=2048,
        )

    @pytest.fixture
    def sample_schema(self) -> DatabaseSchema:
        """Create sample database schema."""
        return DatabaseSchema(
            database_name="testdb",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="users",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(name="name", data_type="varchar"),
                    ],
                )
            ],
        )

    @pytest.fixture
    def sample_result(self) -> QueryResultData:
        """Create sample query result."""
        return QueryResultData(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            row_count=2,
            execution_time_ms=10.0,
        )

    # ============ SQL Generation Tests ============

    @pytest.mark.asyncio
    async def test_generate_sql_success(
        self, llm_settings: LLMSettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test successful SQL generation."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "SELECT * FROM users"

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.generate_sql("查询所有用户", sample_schema)

            assert result == "SELECT * FROM users"

    @pytest.mark.asyncio
    async def test_generate_sql_with_markdown(
        self, llm_settings: LLMSettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test SQL generation with markdown code block."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "```sql\nSELECT * FROM users\n```"

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.generate_sql("查询所有用户", sample_schema)

            assert "```" not in result
            assert "SELECT" in result

    @pytest.mark.asyncio
    async def test_generate_sql_with_explanation(
        self, llm_settings: LLMSettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test SQL extraction when LLM includes explanation."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "这是一个查询用户的 SQL:\nSELECT id, name FROM users"

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.generate_sql("查询所有用户", sample_schema)

            assert "SELECT" in result
            assert "FROM users" in result

    @pytest.mark.asyncio
    async def test_generate_sql_empty_response(
        self, llm_settings: LLMSettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test SQL generation with empty response."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = ""

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            with pytest.raises(SQLGenerationError) as exc:
                await service.generate_sql("查询用户", sample_schema)
            assert "空响应" in str(exc.value)

    @pytest.mark.asyncio
    async def test_generate_sql_none_content(
        self, llm_settings: LLMSettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test SQL generation with None content."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = None

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            with pytest.raises(SQLGenerationError) as exc:
                await service.generate_sql("查询用户", sample_schema)
            assert "空响应" in str(exc.value)

    @pytest.mark.asyncio
    async def test_generate_sql_api_error(
        self, llm_settings: LLMSettings, sample_schema: DatabaseSchema
    ) -> None:
        """Test SQL generation with API error."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            with pytest.raises(LLMError) as exc:
                await service.generate_sql("查询用户", sample_schema)
            assert "API" in str(exc.value)

    # ============ Result Validation Tests ============

    @pytest.mark.asyncio
    async def test_validate_result_passed(
        self,
        llm_settings: LLMSettings,
        sample_result: QueryResultData,
    ) -> None:
        """Test result validation passes."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '{"passed": true, "message": "验证通过"}'

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.validate_result(
                "查询用户",
                "SELECT * FROM users",
                sample_result,
            )

            assert result.passed is True
            assert "验证通过" in result.message

    @pytest.mark.asyncio
    async def test_validate_result_failed(
        self,
        llm_settings: LLMSettings,
        sample_result: QueryResultData,
    ) -> None:
        """Test result validation fails."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = '{"passed": false, "message": "结果不符合预期"}'

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.validate_result(
                "查询管理员",
                "SELECT * FROM users",
                sample_result,
            )

            assert result.passed is False

    @pytest.mark.asyncio
    async def test_validate_result_invalid_json(
        self,
        llm_settings: LLMSettings,
        sample_result: QueryResultData,
    ) -> None:
        """Test result validation with invalid JSON response."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "结果看起来是正确的"

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.validate_result(
                "查询用户",
                "SELECT * FROM users",
                sample_result,
            )

            # Should default to passed if can't parse JSON
            assert result.passed is True

    @pytest.mark.asyncio
    async def test_validate_result_api_error_defaults_pass(
        self,
        llm_settings: LLMSettings,
        sample_result: QueryResultData,
    ) -> None:
        """Test result validation defaults to pass on API error."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.validate_result(
                "查询用户",
                "SELECT * FROM users",
                sample_result,
            )

            # Should default to pass on error to not block query
            assert result.passed is True

    @pytest.mark.asyncio
    async def test_validate_result_empty_response(
        self,
        llm_settings: LLMSettings,
        sample_result: QueryResultData,
    ) -> None:
        """Test result validation with empty response."""
        with patch("pg_mcp.llm.service.AsyncOpenAI") as mock_openai:
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = ""

            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            mock_openai.return_value = mock_client

            service = LLMService(llm_settings)
            service._client = mock_client

            result = await service.validate_result(
                "查询用户",
                "SELECT * FROM users",
                sample_result,
            )

            # Should default to pass on empty
            assert result.passed is True


class TestLLMServiceHelpers:
    """Tests for LLMService helper methods."""

    @pytest.fixture
    def service(self) -> LLMService:
        """Create LLM service for testing."""
        settings = LLMSettings(api_key="test-key")
        with patch("pg_mcp.llm.service.AsyncOpenAI"):
            return LLMService(settings)

    # ============ _clean_sql Tests ============

    def test_clean_sql_plain(self, service: LLMService) -> None:
        """Test cleaning plain SQL."""
        result = service._clean_sql("SELECT * FROM users")
        assert result == "SELECT * FROM users"

    def test_clean_sql_markdown_block(self, service: LLMService) -> None:
        """Test cleaning SQL with markdown code block."""
        result = service._clean_sql("```sql\nSELECT * FROM users\n```")
        assert "```" not in result
        assert "SELECT * FROM users" in result

    def test_clean_sql_whitespace(self, service: LLMService) -> None:
        """Test cleaning SQL with extra whitespace."""
        result = service._clean_sql("  SELECT * FROM users  ")
        assert result == "SELECT * FROM users"

    def test_clean_sql_with_explanation(self, service: LLMService) -> None:
        """Test cleaning SQL with preceding explanation."""
        result = service._clean_sql("这是SQL: SELECT * FROM users")
        assert "SELECT * FROM users" in result

    def test_clean_sql_empty(self, service: LLMService) -> None:
        """Test cleaning empty SQL."""
        result = service._clean_sql("")
        assert result == ""

    # ============ _parse_validation_response Tests ============

    def test_parse_validation_json_passed(self, service: LLMService) -> None:
        """Test parsing valid JSON with passed=true."""
        result = service._parse_validation_response('{"passed": true, "message": "OK"}')
        assert result.passed is True
        assert result.message == "OK"

    def test_parse_validation_json_failed(self, service: LLMService) -> None:
        """Test parsing valid JSON with passed=false."""
        result = service._parse_validation_response('{"passed": false, "message": "错误"}')
        assert result.passed is False
        assert result.message == "错误"

    def test_parse_validation_wrapped_json(self, service: LLMService) -> None:
        """Test parsing JSON wrapped in text."""
        result = service._parse_validation_response(
            '结果验证: {"passed": true, "message": "验证完成"}'
        )
        assert result.passed is True

    def test_parse_validation_text_positive(self, service: LLMService) -> None:
        """Test parsing positive text response."""
        result = service._parse_validation_response("结果正确，符合预期")
        assert result.passed is True

    def test_parse_validation_text_negative(self, service: LLMService) -> None:
        """Test parsing negative text response."""
        result = service._parse_validation_response("结果不正确")
        assert result.passed is False

    # ============ _format_sample_rows Tests ============

    def test_format_sample_rows_normal(self, service: LLMService) -> None:
        """Test formatting normal sample rows."""
        result = QueryResultData(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            row_count=2,
            execution_time_ms=10.0,
        )
        formatted = service._format_sample_rows(result)
        assert "Alice" in formatted
        assert "Bob" in formatted

    def test_format_sample_rows_empty(self, service: LLMService) -> None:
        """Test formatting empty result."""
        result = QueryResultData(
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=5.0,
        )
        formatted = service._format_sample_rows(result)
        assert "无数据" in formatted

    def test_format_sample_rows_with_null(self, service: LLMService) -> None:
        """Test formatting rows with NULL values."""
        result = QueryResultData(
            columns=["id", "name"],
            rows=[[1, None]],
            row_count=1,
            execution_time_ms=5.0,
        )
        formatted = service._format_sample_rows(result)
        assert "NULL" in formatted

    def test_format_sample_rows_truncate_long_value(self, service: LLMService) -> None:
        """Test formatting rows with long values."""
        long_value = "A" * 100
        result = QueryResultData(
            columns=["id", "content"],
            rows=[[1, long_value]],
            row_count=1,
            execution_time_ms=5.0,
        )
        formatted = service._format_sample_rows(result)
        assert "..." in formatted
        assert long_value not in formatted

    def test_format_sample_rows_more_than_max(self, service: LLMService) -> None:
        """Test formatting more rows than max_rows."""
        result = QueryResultData(
            columns=["id"],
            rows=[[i] for i in range(10)],
            row_count=10,
            execution_time_ms=5.0,
        )
        formatted = service._format_sample_rows(result, max_rows=5)
        assert "还有" in formatted
        assert "5" in formatted
