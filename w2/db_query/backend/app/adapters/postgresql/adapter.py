"""PostgreSQL adapter implementation."""

from app.adapters.base import DatabaseAdapter
from app.adapters.postgresql.connection import PostgreSQLConnectionProvider
from app.adapters.postgresql.metadata import PostgreSQLMetadataProvider
from app.adapters.postgresql.query import PostgreSQLQueryExecutor
from app.adapters.postgresql.types import PostgreSQLTypeMapper
from app.core.registry import DatabaseRegistry
from app.core.types import (
    ConnectionProvider,
    DatabaseType,
    MetadataProvider,
    QueryExecutor,
    SQLDialect,
    TypeMapper,
)


@DatabaseRegistry.register(DatabaseType.POSTGRESQL)
class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter."""

    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.POSTGRES

    def _create_connection_provider(self) -> ConnectionProvider:
        return PostgreSQLConnectionProvider()

    def _create_metadata_provider(self) -> MetadataProvider:
        return PostgreSQLMetadataProvider(self._connection_provider)

    def _create_query_executor(self) -> QueryExecutor:
        return PostgreSQLQueryExecutor(self._connection_provider)

    def _create_type_mapper(self) -> TypeMapper:
        return PostgreSQLTypeMapper()
