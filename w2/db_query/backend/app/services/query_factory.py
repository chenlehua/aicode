"""Factory for query services based on database type."""

from app.models.database import DatabaseType, detect_database_type
from app.models.query import QueryResult
from app.services.query import QueryService
from app.services.query_mysql import MySQLQueryService


class QueryFactory:
    """Factory class for selecting appropriate query service."""

    @staticmethod
    def validate_sql(url: str, sql: str) -> tuple[bool, str | None]:
        """Validate SQL using the appropriate service for the database type."""
        db_type = detect_database_type(url)

        if db_type == DatabaseType.POSTGRESQL:
            return QueryService.validate_sql(sql)
        elif db_type == DatabaseType.MYSQL:
            return MySQLQueryService.validate_sql(sql)

        raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def inject_limit(url: str, sql: str) -> str:
        """Inject LIMIT clause using the appropriate service."""
        db_type = detect_database_type(url)

        if db_type == DatabaseType.POSTGRESQL:
            return QueryService.inject_limit(sql)
        elif db_type == DatabaseType.MYSQL:
            return MySQLQueryService.inject_limit(sql)

        raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    async def execute_query(database_name: str, url: str, sql: str) -> QueryResult:
        """Execute query using the appropriate service for the database type."""
        db_type = detect_database_type(url)

        if db_type == DatabaseType.POSTGRESQL:
            return await QueryService.execute_query(database_name, url, sql)
        elif db_type == DatabaseType.MYSQL:
            return await MySQLQueryService.execute_query(database_name, url, sql)

        raise ValueError(f"Unsupported database type: {db_type}")
