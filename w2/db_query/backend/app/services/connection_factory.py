"""Factory for database connection services based on URL scheme.

This module now delegates to the new adapter architecture for backward compatibility.
"""

from typing import Any

from app.adapters import DatabaseRegistry


class ConnectionFactory:
    """Factory class for unified connection management across database types.

    This class now delegates to the new DatabaseAdapter architecture.
    """

    @staticmethod
    async def get_pool(url: str) -> Any:
        """Get or create a connection pool for a database URL."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        return await adapter._connection_provider.get_pool(url)

    @staticmethod
    async def test_connection(url: str) -> bool:
        """Test if a database connection URL is valid."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        return await adapter.test_connection(url)

    @staticmethod
    async def close_pool(url: str) -> None:
        """Close a connection pool."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        await adapter._connection_provider.close_pool(url)

    @staticmethod
    async def close_all() -> None:
        """Close all connection pools for all database types."""
        await DatabaseRegistry.close_all()

    @staticmethod
    async def execute(url: str, query: str, *args: Any) -> list[dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        return await adapter._connection_provider.execute(url, query, *args)
