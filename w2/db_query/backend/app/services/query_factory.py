"""Factory for query services based on database type.

This module now delegates to the new adapter architecture for backward compatibility.
"""

from app.adapters import DatabaseRegistry
from app.models.query import QueryResult


class QueryFactory:
    """Factory class for selecting appropriate query service.

    This class now delegates to the new DatabaseAdapter architecture.
    """

    @staticmethod
    def validate_sql(url: str, sql: str) -> tuple[bool, str | None]:
        """Validate SQL using the appropriate service for the database type."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        return adapter.validate_sql(sql)

    @staticmethod
    def inject_limit(url: str, sql: str) -> str:
        """Inject LIMIT clause using the appropriate service."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        return adapter.inject_limit(sql)

    @staticmethod
    async def execute_query(database_name: str, url: str, sql: str) -> QueryResult:
        """Execute query using the appropriate service for the database type."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        return await adapter.execute_query(database_name, url, sql)
