"""Core type definitions and protocols for database adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol
from urllib.parse import urlparse


class DatabaseType(str, Enum):
    """Supported database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


@dataclass(frozen=True)
class DatabaseConfig:
    """Immutable database configuration."""

    url: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str | None = None
    password: str | None = None

    @classmethod
    def from_url(cls, url: str) -> "DatabaseConfig":
        """Parse database URL into config object."""
        # Handle different URL schemes
        url_lower = url.lower()

        if url_lower.startswith(("postgresql://", "postgres://")):
            db_type = DatabaseType.POSTGRESQL
            default_port = 5432
        elif url_lower.startswith(("mysql://", "mysql+aiomysql://")):
            db_type = DatabaseType.MYSQL
            default_port = 3306
            # Normalize mysql+aiomysql:// to mysql:// for parsing
            if url.startswith("mysql+aiomysql://"):
                url = url.replace("mysql+aiomysql://", "mysql://", 1)
        else:
            raise ValueError(f"Unsupported database URL scheme: {url}")

        parsed = urlparse(url)

        return cls(
            url=url,
            db_type=db_type,
            host=parsed.hostname or "localhost",
            port=parsed.port or default_port,
            database=parsed.path.lstrip("/") if parsed.path else "",
            username=parsed.username,
            password=parsed.password,
        )


class SQLDialect(str, Enum):
    """SQL dialects for query parsing."""

    POSTGRES = "postgres"
    MYSQL = "mysql"


# ========== Protocol Definitions (Interface Contracts) ==========


class ConnectionPool(Protocol):
    """Protocol for database connection pools."""

    async def acquire(self) -> Any:
        """Acquire a connection from the pool."""
        ...

    def release(self, conn: Any) -> None:
        """Release a connection back to the pool."""
        ...

    async def close(self) -> None:
        """Close all connections in the pool."""
        ...


class ConnectionProvider(ABC):
    """Abstract interface for database connection management."""

    @abstractmethod
    async def get_pool(self, url: str) -> Any:
        """Get or create a connection pool."""
        ...

    @abstractmethod
    async def test_connection(self, url: str) -> bool:
        """Test if a connection can be established."""
        ...

    @abstractmethod
    async def close_pool(self, url: str) -> None:
        """Close a specific connection pool."""
        ...

    @abstractmethod
    async def close_all(self) -> None:
        """Close all managed connection pools."""
        ...


class MetadataProvider(ABC):
    """Abstract interface for database metadata extraction."""

    @abstractmethod
    async def fetch_metadata(
        self,
        database_name: str,
        url: str,
    ) -> Any:  # Returns DatabaseMetadata
        """Fetch complete database schema metadata."""
        ...


class QueryExecutor(ABC):
    """Abstract interface for SQL query execution."""

    @property
    @abstractmethod
    def dialect(self) -> SQLDialect:
        """The SQL dialect this executor uses."""
        ...

    @property
    @abstractmethod
    def max_rows(self) -> int:
        """Maximum rows to return."""
        ...

    @abstractmethod
    def validate_sql(self, sql: str) -> tuple[bool, str | None]:
        """Validate SQL syntax. Returns (is_valid, error_message)."""
        ...

    @abstractmethod
    def inject_limit(self, sql: str) -> str:
        """Inject LIMIT clause if not present."""
        ...

    @abstractmethod
    async def execute(
        self,
        url: str,
        sql: str,
    ) -> Any:  # Returns QueryResult
        """Execute a SQL query and return results."""
        ...


class TypeMapper(ABC):
    """Abstract interface for database type mapping."""

    @abstractmethod
    def python_to_db_type(self, value: Any) -> str:
        """Map Python value to database type name."""
        ...

    @abstractmethod
    def db_to_python_type(self, db_type: str) -> type:
        """Map database type name to Python type."""
        ...

    @abstractmethod
    def serialize_value(self, value: Any) -> Any:
        """Serialize a value for JSON response."""
        ...
