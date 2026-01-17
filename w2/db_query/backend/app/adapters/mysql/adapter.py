"""MySQL adapter implementation."""

from app.adapters.base import DatabaseAdapter
from app.adapters.mysql.connection import MySQLConnectionProvider
from app.adapters.mysql.metadata import MySQLMetadataProvider
from app.adapters.mysql.query import MySQLQueryExecutor
from app.adapters.mysql.types import MySQLTypeMapper
from app.core.registry import DatabaseRegistry
from app.core.types import (
    ConnectionProvider,
    DatabaseType,
    MetadataProvider,
    QueryExecutor,
    SQLDialect,
    TypeMapper,
)


@DatabaseRegistry.register(DatabaseType.MYSQL)
class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter."""

    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.MYSQL

    def _create_connection_provider(self) -> ConnectionProvider:
        return MySQLConnectionProvider()

    def _create_metadata_provider(self) -> MetadataProvider:
        return MySQLMetadataProvider(self._connection_provider)

    def _create_query_executor(self) -> QueryExecutor:
        return MySQLQueryExecutor(self._connection_provider)

    def _create_type_mapper(self) -> TypeMapper:
        return MySQLTypeMapper()
