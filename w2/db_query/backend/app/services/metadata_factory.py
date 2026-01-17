"""Factory for metadata services based on database type.

This module now delegates to the new adapter architecture for backward compatibility.
"""

from app.adapters import DatabaseRegistry
from app.models.database import DatabaseMetadata


class MetadataFactory:
    """Factory class for selecting appropriate metadata service.

    This class now delegates to the new DatabaseAdapter architecture.
    """

    @staticmethod
    async def fetch_metadata(database_name: str, url: str) -> DatabaseMetadata:
        """Fetch metadata using the appropriate service for the database type."""
        adapter = DatabaseRegistry.get_adapter_for_url(url)
        return await adapter.fetch_metadata(database_name, url)
