"""Abstract base interface for database connections."""

from abc import ABC, abstractmethod
from typing import Any


class ConnectionServiceBase(ABC):
    """Abstract base class for database connection services."""

    _pools: dict[str, Any] = {}

    @classmethod
    @abstractmethod
    async def get_pool(cls, url: str) -> Any:
        """Get or create a connection pool for a database URL."""
        pass

    @classmethod
    @abstractmethod
    async def test_connection(cls, url: str) -> bool:
        """Test if a database connection URL is valid."""
        pass

    @classmethod
    @abstractmethod
    async def close_pool(cls, url: str) -> None:
        """Close a connection pool."""
        pass

    @classmethod
    @abstractmethod
    async def close_all(cls) -> None:
        """Close all connection pools."""
        pass

    @classmethod
    @abstractmethod
    async def execute(cls, url: str, query: str, *args: Any) -> list[dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        pass
