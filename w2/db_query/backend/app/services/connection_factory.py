"""Factory for database connection services based on URL scheme."""

from typing import Any

from app.models.database import DatabaseType, detect_database_type
from app.services.connection import PostgreSQLConnectionService
from app.services.connection_base import ConnectionServiceBase
from app.services.connection_mysql import MySQLConnectionService


def get_connection_service(url: str) -> type[ConnectionServiceBase]:
    """Get the appropriate connection service class based on URL scheme."""
    db_type = detect_database_type(url)
    if db_type == DatabaseType.POSTGRESQL:
        return PostgreSQLConnectionService
    elif db_type == DatabaseType.MYSQL:
        return MySQLConnectionService
    raise ValueError(f"Unsupported database type: {db_type}")


class ConnectionFactory:
    """Factory class for unified connection management across database types."""

    @staticmethod
    async def get_pool(url: str) -> Any:
        """Get or create a connection pool for a database URL."""
        service = get_connection_service(url)
        return await service.get_pool(url)

    @staticmethod
    async def test_connection(url: str) -> bool:
        """Test if a database connection URL is valid."""
        service = get_connection_service(url)
        return await service.test_connection(url)

    @staticmethod
    async def close_pool(url: str) -> None:
        """Close a connection pool."""
        service = get_connection_service(url)
        await service.close_pool(url)

    @staticmethod
    async def close_all() -> None:
        """Close all connection pools for all database types."""
        await PostgreSQLConnectionService.close_all()
        await MySQLConnectionService.close_all()

    @staticmethod
    async def execute(url: str, query: str, *args: Any) -> list[dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        service = get_connection_service(url)
        return await service.execute(url, query, *args)
