"""Database management API routes."""

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response

from app.models.database import DatabaseCreate
from app.models.error import ErrorResponse
from app.models.query import GeneratedSQL, NaturalQueryRequest, QueryRequest
from app.services.connection_factory import ConnectionFactory
from app.services.database import DatabaseService
from app.services.history import HistoryService
from app.services.llm import LLMService
from app.services.query_factory import QueryFactory

router = APIRouter()


@router.get("", response_model=list[dict[str, Any]])
async def list_databases() -> list[dict[str, Any]]:
    """List all stored database connections."""
    databases = await DatabaseService.list_databases()
    return [db.model_dump(by_alias=True) for db in databases]


@router.put("/{name}", response_model=dict[str, Any])
async def upsert_database(name: str, request: DatabaseCreate) -> dict[str, Any]:
    """Add or update a database connection and fetch metadata."""
    # Validate name format
    if not (1 <= len(name) <= 64) or not all(c.isalnum() or c in ("_", "-") for c in name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="INVALID_NAME",
                message=(
                    "Database name must be 1-64 characters, alphanumeric with underscores/hyphens"
                ),
            ).model_dump(by_alias=True),
        )

    # Test connection
    if not await ConnectionFactory.test_connection(request.url):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ErrorResponse(
                error="CONNECTION_FAILED",
                message="Could not connect to database. Please check the connection URL.",
            ).model_dump(by_alias=True),
        )

    try:
        result = await DatabaseService.create_or_update_database(
            name, request.url, request.description
        )
        return result.model_dump(by_alias=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ErrorResponse(
                error="METADATA_FETCH_FAILED",
                message=f"Failed to fetch database metadata: {str(e)}",
            ).model_dump(by_alias=True),
        )


@router.get("/{name}", response_model=dict[str, Any])
async def get_database(name: str) -> dict[str, Any]:
    """Get a database connection with its cached metadata."""
    database = await DatabaseService.get_database(name)
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="NOT_FOUND", message=f"Database '{name}' not found"
            ).model_dump(by_alias=True),
        )
    return database.model_dump(by_alias=True)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(name: str) -> Response:
    """Delete a database connection and its cached metadata."""
    deleted = await DatabaseService.delete_database(name)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="NOT_FOUND", message=f"Database '{name}' not found"
            ).model_dump(by_alias=True),
        )

    # Close connection pool if exists
    database = await DatabaseService.get_database(name)
    if database:
        await ConnectionFactory.close_pool(database.url)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{name}/query", response_model=dict[str, Any])
async def execute_query(name: str, request: QueryRequest) -> dict[str, Any]:
    """Execute a SQL query against the database."""
    # Get database connection
    database = await DatabaseService.get_database(name)
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="NOT_FOUND", message=f"Database '{name}' not found"
            ).model_dump(by_alias=True),
        )

    start_time = time.time()
    try:
        # Execute query using factory
        result = await QueryFactory.execute_query(name, database.url, request.sql)

        # Save to history
        await HistoryService.save_query(
            database_name=name,
            sql=request.sql,
            query_type="manual",
            natural_prompt=None,
            row_count=result.row_count,
            execution_time_ms=result.execution_time_ms,
            status="success",
        )

        return result.model_dump(by_alias=True)
    except ValueError as e:
        # SQL validation error
        execution_time_ms = int((time.time() - start_time) * 1000)
        await HistoryService.save_query(
            database_name=name,
            sql=request.sql,
            query_type="manual",
            natural_prompt=None,
            row_count=0,
            execution_time_ms=execution_time_ms,
            status="error",
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="INVALID_SQL", message=str(e)).model_dump(by_alias=True),
        )
    except RuntimeError as e:
        # Query execution error
        execution_time_ms = int((time.time() - start_time) * 1000)
        await HistoryService.save_query(
            database_name=name,
            sql=request.sql,
            query_type="manual",
            natural_prompt=None,
            row_count=0,
            execution_time_ms=execution_time_ms,
            status="error",
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ErrorResponse(error="QUERY_EXECUTION_FAILED", message=str(e)).model_dump(
                by_alias=True
            ),
        )


@router.get("/{name}/history", response_model=dict[str, Any])
async def get_query_history(
    name: str, page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)
) -> dict[str, Any]:
    """Get query history for a database."""
    # Verify database exists
    database = await DatabaseService.get_database(name)
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="NOT_FOUND", message=f"Database '{name}' not found"
            ).model_dump(by_alias=True),
        )

    history = await HistoryService.get_history(name, page, page_size)
    return history.model_dump(by_alias=True)


@router.post("/{name}/query/natural", response_model=dict[str, Any])
async def generate_natural_query(name: str, request: NaturalQueryRequest) -> dict[str, Any]:
    """Generate SQL from natural language prompt."""
    # Get database connection and metadata
    database = await DatabaseService.get_database(name)
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="NOT_FOUND", message=f"Database '{name}' not found"
            ).model_dump(by_alias=True),
        )

    try:
        # Initialize LLM service
        llm_service = LLMService()

        # Generate SQL (synchronous call)
        generated_sql, explanation = llm_service.generate_sql(request.prompt, database.metadata)

        result = GeneratedSQL(sql=generated_sql, explanation=explanation)
        return result.model_dump(by_alias=True)
    except ValueError as e:
        # Validation or configuration error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error="LLM_GENERATION_FAILED", message=str(e)).model_dump(
                by_alias=True
            ),
        )
    except RuntimeError as e:
        # LLM API error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ErrorResponse(error="LLM_SERVICE_ERROR", message=str(e)).model_dump(
                by_alias=True
            ),
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="INTERNAL_ERROR",
                message=f"Unexpected error: {str(e)}",
            ).model_dump(by_alias=True),
        )
