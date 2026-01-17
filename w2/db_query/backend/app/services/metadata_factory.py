"""Factory for metadata services based on database type."""

from app.models.database import DatabaseMetadata, DatabaseType, detect_database_type
from app.services.metadata import MetadataService
from app.services.metadata_mysql import MySQLMetadataService


class MetadataFactory:
    """Factory class for selecting appropriate metadata service."""

    @staticmethod
    async def fetch_metadata(database_name: str, url: str) -> DatabaseMetadata:
        """Fetch metadata using the appropriate service for the database type."""
        db_type = detect_database_type(url)

        if db_type == DatabaseType.POSTGRESQL:
            return await MetadataService.fetch_metadata(database_name, url)
        elif db_type == DatabaseType.MYSQL:
            return await MySQLMetadataService.fetch_metadata(database_name, url)

        raise ValueError(f"Unsupported database type: {db_type}")
