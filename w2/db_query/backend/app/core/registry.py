"""Database adapter registry with auto-discovery."""

from typing import TYPE_CHECKING, Any

from app.core.exceptions import UnsupportedDatabaseError
from app.core.types import DatabaseType

if TYPE_CHECKING:
    from app.adapters.base import DatabaseAdapter


class DatabaseRegistry:
    """
    Central registry for database adapters.

    Implements the Service Locator pattern with support for
    auto-discovery of adapter implementations.
    """

    _adapters: dict[DatabaseType, type["DatabaseAdapter"]] = {}
    _instances: dict[str, "DatabaseAdapter"] = {}  # url -> instance cache

    @classmethod
    def register(cls, db_type: DatabaseType) -> Any:
        """
        Decorator to register an adapter class.

        Usage:
            @DatabaseRegistry.register(DatabaseType.POSTGRESQL)
            class PostgreSQLAdapter(DatabaseAdapter):
                ...
        """

        def decorator(
            adapter_class: type["DatabaseAdapter"],
        ) -> type["DatabaseAdapter"]:
            cls._adapters[db_type] = adapter_class
            return adapter_class

        return decorator

    @classmethod
    def get_adapter_class(cls, db_type: DatabaseType) -> type["DatabaseAdapter"]:
        """Get the adapter class for a database type."""
        if db_type not in cls._adapters:
            raise UnsupportedDatabaseError(db_type.value)
        return cls._adapters[db_type]

    @classmethod
    def get_adapter(cls, db_type: DatabaseType | str) -> "DatabaseAdapter":
        """
        Get or create an adapter instance for the given database type.

        Uses singleton pattern - one adapter instance per database type.
        Accepts both DatabaseType enum and string values for compatibility.
        """
        # Convert string to DatabaseType if needed
        if isinstance(db_type, str):
            db_type = DatabaseType(db_type)

        if db_type not in cls._instances:
            adapter_class = cls.get_adapter_class(db_type)
            cls._instances[db_type] = adapter_class()
        return cls._instances[db_type]

    @classmethod
    def get_adapter_for_url(cls, url: str) -> "DatabaseAdapter":
        """Convenience method to get adapter from URL string."""
        db_type = detect_database_type(url)
        return cls.get_adapter(db_type)

    @classmethod
    async def close_all(cls) -> None:
        """Close all cached adapter instances."""
        for adapter in cls._instances.values():
            await adapter.close()
        cls._instances.clear()

    @classmethod
    def registered_types(cls) -> list[DatabaseType]:
        """List all registered database types."""
        return list(cls._adapters.keys())

    @classmethod
    def is_supported(cls, db_type: DatabaseType) -> bool:
        """Check if a database type is supported."""
        return db_type in cls._adapters


def detect_database_type(url: str) -> DatabaseType:
    """Detect database type from URL scheme."""
    url_lower = url.lower()

    if url_lower.startswith(("postgresql://", "postgres://")):
        return DatabaseType.POSTGRESQL
    elif url_lower.startswith(("mysql://", "mysql+aiomysql://")):
        return DatabaseType.MYSQL

    scheme = url.split("://")[0] if "://" in url else "unknown"
    raise UnsupportedDatabaseError(scheme)
