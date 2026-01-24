"""Query orchestration service for pg-mcp."""

import logging
from datetime import datetime, timezone

from pg_mcp.config import QuerySettings
from pg_mcp.database import DatabaseService
from pg_mcp.llm import LLMService
from pg_mcp.models import (
    ErrorCode,
    QueryError,
    QueryRequest,
    QueryResponse,
    SQLUnsafeError,
)
from pg_mcp.validator import SQLValidator

logger = logging.getLogger(__name__)


class QueryService:
    """Orchestrates the natural language to SQL query workflow.

    This service coordinates:
    1. Fetching database schema
    2. Generating SQL from natural language
    3. Validating SQL safety
    4. Executing the query
    5. Optionally validating results with LLM

    Args:
        llm_service: LLM service for SQL generation and validation.
        database_service: Database service for schema and query execution.
        validator: SQL safety validator.
        query_settings: Query execution settings.
    """

    def __init__(
        self,
        llm_service: LLMService,
        database_service: DatabaseService,
        validator: SQLValidator,
        query_settings: QuerySettings,
    ) -> None:
        self.llm_service = llm_service
        self.database_service = database_service
        self.validator = validator
        self.query_settings = query_settings

    async def execute(self, request: QueryRequest) -> QueryResponse:
        """Execute a natural language query.

        Args:
            request: The query request containing the natural language query.

        Returns:
            QueryResponse containing the results or error information.
        """
        logger.info(f"Processing query: {request.query[:100]}...")

        try:
            # 1. Get Schema
            schema = self.database_service.schema

            # 2. Generate SQL using LLM
            sql = await self.llm_service.generate_sql(request.query, schema)

            # 3. Validate SQL safety
            self.validator.validate(sql)

            # 4. Execute SQL
            result = await self.database_service.execute_query(
                sql,
                limit=self.query_settings.default_limit,
            )

            # 5. Optionally validate results with LLM
            validation = None
            if self.query_settings.enable_validation:
                validation = await self.llm_service.validate_result(
                    request.query,
                    sql,
                    result,
                )

            # 6. Build success response
            logger.info(f"Query completed successfully: {result.row_count} rows")
            return QueryResponse(
                success=True,
                sql=sql,
                result=result,
                validation=validation,
                generated_at=datetime.now(timezone.utc),
            )

        except SQLUnsafeError as e:
            logger.warning(f"SQL validation failed: {e.message}")
            return self._build_error_response(e)

        except QueryError as e:
            logger.error(f"Query error: {e}")
            return self._build_error_response(e)

        except Exception as e:
            logger.exception("Unexpected error during query execution")
            return QueryResponse(
                success=False,
                error=f"内部错误: {e}",
                error_code=ErrorCode.INTERNAL_ERROR.value,
                generated_at=datetime.now(timezone.utc),
            )

    def _build_error_response(self, error: QueryError) -> QueryResponse:
        """Build an error response from a QueryError.

        Args:
            error: The QueryError that occurred.

        Returns:
            QueryResponse with error information.
        """
        return QueryResponse(
            success=False,
            error=error.message,
            error_code=error.code.value,
            generated_at=datetime.now(timezone.utc),
        )
