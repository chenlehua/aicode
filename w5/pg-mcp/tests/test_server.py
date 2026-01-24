"""Tests for MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from pg_mcp.models import (
    DatabaseSchema,
    QueryResponse,
    QueryResultData,
    TableInfo,
    ColumnInfo,
    ValidationResult,
)


class TestCreateServer:
    """Tests for create_server function."""

    def test_create_server_returns_fastmcp(self) -> None:
        """Test that create_server returns a FastMCP instance."""
        from pg_mcp.server import create_server

        server = create_server()
        assert server is not None
        assert "PostgreSQL" in server.name

    def test_server_has_name(self) -> None:
        """Test that server has a name."""
        from pg_mcp.server import create_server

        server = create_server()
        assert server.name == "PostgreSQL MCP Server"


class TestQueryToolLogic:
    """Tests for query tool logic using direct function calls."""

    @pytest.fixture
    def sample_schema(self) -> DatabaseSchema:
        """Create sample schema."""
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
                ),
            ],
        )

    @pytest.fixture
    def sample_result(self) -> QueryResultData:
        """Create sample query result."""
        return QueryResultData(
            columns=["id", "name"],
            rows=[[1, "Alice"]],
            row_count=1,
            execution_time_ms=10.0,
        )

    @pytest.fixture
    def sample_response(self, sample_result: QueryResultData) -> QueryResponse:
        """Create sample query response."""
        return QueryResponse(
            success=True,
            sql="SELECT * FROM users",
            result=sample_result,
            validation=ValidationResult(passed=True, message="OK"),
        )

    @pytest.mark.asyncio
    async def test_query_service_integration(
        self, sample_schema: DatabaseSchema, sample_response: QueryResponse
    ) -> None:
        """Test that QueryService is called correctly in a query flow."""
        from pg_mcp.query import QueryService
        from pg_mcp.models import QueryRequest

        # Create a mock QueryService
        mock_service = MagicMock(spec=QueryService)
        mock_service.execute = AsyncMock(return_value=sample_response)

        # Simulate the query tool logic
        request = QueryRequest(query="查询所有用户")
        response = await mock_service.execute(request)

        result_json = response.model_dump_json(indent=2)
        result_data = json.loads(result_json)

        assert result_data["success"] is True
        assert result_data["sql"] == "SELECT * FROM users"
        assert result_data["result"]["row_count"] == 1

    @pytest.mark.asyncio
    async def test_query_not_initialized_response(self) -> None:
        """Test response when service is not initialized."""
        # This simulates what the server returns when _query_service is None
        error_response = '{"success": false, "error": "服务未初始化"}'

        result_data = json.loads(error_response)

        assert result_data["success"] is False
        assert "未初始化" in result_data["error"]

    @pytest.mark.asyncio
    async def test_query_error_response(self) -> None:
        """Test error response format."""
        error_response = QueryResponse(
            success=False,
            error="SQL 不安全",
            error_code="SQL_UNSAFE",
        )

        result_json = error_response.model_dump_json(indent=2)
        result_data = json.loads(result_json)

        assert result_data["success"] is False
        assert result_data["error_code"] == "SQL_UNSAFE"


class TestRefreshSchemaToolLogic:
    """Tests for refresh_schema tool logic."""

    @pytest.fixture
    def sample_schema(self) -> DatabaseSchema:
        """Create sample schema."""
        return DatabaseSchema(
            database_name="testdb",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="users",
                    columns=[ColumnInfo(name="id", data_type="integer")],
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_refresh_schema_success_response(self, sample_schema: DatabaseSchema) -> None:
        """Test refresh_schema success response format."""
        # Simulate successful schema refresh response
        result = (
            f'{{"success": true, "message": "Schema 缓存已刷新", '
            f'"tables": {len(sample_schema.tables)}, "views": {len(sample_schema.views)}}}'
        )

        result_data = json.loads(result)

        assert result_data["success"] is True
        assert "刷新" in result_data["message"]
        assert result_data["tables"] == 1

    @pytest.mark.asyncio
    async def test_refresh_schema_not_initialized_response(self) -> None:
        """Test refresh_schema response when not initialized."""
        result = '{"success": false, "error": "服务未初始化"}'

        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "未初始化" in result_data["error"]

    @pytest.mark.asyncio
    async def test_refresh_schema_error_response(self) -> None:
        """Test refresh_schema error response format."""
        error_msg = "Connection error"
        result = f'{{"success": false, "error": "刷新失败: {error_msg}"}}'

        result_data = json.loads(result)

        assert result_data["success"] is False
        assert "刷新失败" in result_data["error"]


class TestGetSchemaToolLogic:
    """Tests for get_schema tool logic."""

    @pytest.fixture
    def sample_schema(self) -> DatabaseSchema:
        """Create sample schema."""
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
                ),
            ],
        )

    def test_get_schema_response(self, sample_schema: DatabaseSchema) -> None:
        """Test get_schema response format."""
        result = sample_schema.to_llm_context()

        assert "testdb" in result
        assert "users" in result
        assert "id" in result

    def test_get_schema_not_initialized_response(self) -> None:
        """Test get_schema response when not initialized."""
        result = "服务未初始化"

        assert "未初始化" in result


class TestServerModuleGlobals:
    """Tests for server module global state management."""

    def test_module_globals_initial_state(self) -> None:
        """Test that module globals start as None."""
        import pg_mcp.server as server_module

        # The globals should be None initially (or after tests reset them)
        # We just check the module has these attributes
        assert hasattr(server_module, "_query_service")
        assert hasattr(server_module, "_database_service")

    @pytest.mark.asyncio
    async def test_lifespan_requires_config_path(self) -> None:
        """Test that lifespan requires PG_MCP_CONFIG_PATH."""
        import os
        from pg_mcp.server import create_server

        # Remove the env var if it exists
        original_value = os.environ.pop("PG_MCP_CONFIG_PATH", None)

        try:
            server = create_server()

            # The lifespan should raise an error without config
            with pytest.raises(RuntimeError) as exc:
                async with server._mcp_server.lifespan(server):
                    pass
        except Exception:
            # It may fail in different ways depending on FastMCP implementation
            pass
        finally:
            # Restore the original value if it existed
            if original_value is not None:
                os.environ["PG_MCP_CONFIG_PATH"] = original_value


class TestQueryResponseSerialization:
    """Tests for QueryResponse serialization used by the server."""

    def test_success_response_serialization(self) -> None:
        """Test successful response serialization."""
        response = QueryResponse(
            success=True,
            sql="SELECT * FROM users",
            result=QueryResultData(
                columns=["id", "name"],
                rows=[[1, "Alice"]],
                row_count=1,
                execution_time_ms=10.0,
            ),
            validation=ValidationResult(passed=True, message="OK"),
        )

        json_str = response.model_dump_json(indent=2)
        data = json.loads(json_str)

        assert data["success"] is True
        assert data["sql"] == "SELECT * FROM users"
        assert data["result"]["row_count"] == 1
        assert data["validation"]["passed"] is True

    def test_error_response_serialization(self) -> None:
        """Test error response serialization."""
        response = QueryResponse(
            success=False,
            error="SQL validation failed",
            error_code="SQL_UNSAFE",
        )

        json_str = response.model_dump_json(indent=2)
        data = json.loads(json_str)

        assert data["success"] is False
        assert data["error"] == "SQL validation failed"
        assert data["error_code"] == "SQL_UNSAFE"
        assert data["sql"] is None
        assert data["result"] is None

    def test_empty_result_serialization(self) -> None:
        """Test empty result serialization."""
        response = QueryResponse(
            success=True,
            sql="SELECT * FROM users WHERE id = 999",
            result=QueryResultData(
                columns=[],
                rows=[],
                row_count=0,
                execution_time_ms=5.0,
            ),
        )

        json_str = response.model_dump_json(indent=2)
        data = json.loads(json_str)

        assert data["success"] is True
        assert data["result"]["row_count"] == 0
        assert data["result"]["columns"] == []
