"""Abstract base class for database adapters."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.types import (
    ConnectionProvider,
    MetadataProvider,
    QueryExecutor,
    SQLDialect,
    TypeMapper,
)


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters.

    This is the main entry point for all database operations.
    Each database type should implement this class.

    The adapter composes specialized providers for different operations:
    - ConnectionProvider: manages connection pools
    - MetadataProvider: extracts schema information
    - QueryExecutor: validates and executes queries
    - TypeMapper: handles type conversions
    """

    def __init__(self) -> None:
        self._connection_provider = self._create_connection_provider()
        self._metadata_provider = self._create_metadata_provider()
        self._query_executor = self._create_query_executor()
        self._type_mapper = self._create_type_mapper()

    @property
    @abstractmethod
    def dialect(self) -> SQLDialect:
        """The SQL dialect for this database."""
        ...

    @abstractmethod
    def _create_connection_provider(self) -> ConnectionProvider:
        """Factory method for connection provider."""
        ...

    @abstractmethod
    def _create_metadata_provider(self) -> MetadataProvider:
        """Factory method for metadata provider."""
        ...

    @abstractmethod
    def _create_query_executor(self) -> QueryExecutor:
        """Factory method for query executor."""
        ...

    @abstractmethod
    def _create_type_mapper(self) -> TypeMapper:
        """Factory method for type mapper."""
        ...

    # ========== High-level operations ==========

    async def test_connection(self, url: str) -> bool:
        """Test if a connection can be established."""
        return await self._connection_provider.test_connection(url)

    async def fetch_metadata(self, database_name: str, url: str) -> Any:
        """Fetch complete database schema metadata."""
        return await self._metadata_provider.fetch_metadata(database_name, url)

    def validate_sql(self, sql: str) -> tuple[bool, str | None]:
        """Validate SQL syntax."""
        return self._query_executor.validate_sql(sql)

    def inject_limit(self, sql: str) -> str:
        """Inject LIMIT clause if not present."""
        return self._query_executor.inject_limit(sql)

    async def execute_query(self, database_name: str, url: str, sql: str) -> Any:
        """Execute a SQL query."""
        return await self._query_executor.execute(url, sql)

    def serialize_value(self, value: Any) -> Any:
        """Serialize a value for JSON response."""
        return self._type_mapper.serialize_value(value)

    def infer_type(self, value: Any) -> str:
        """Infer database type from Python value."""
        return self._type_mapper.python_to_db_type(value)

    async def close(self) -> None:
        """Close all resources held by this adapter."""
        await self._connection_provider.close_all()
