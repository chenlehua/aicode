"""PostgreSQL connection pool management."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Connection, Pool

from pg_mcp.config import DatabaseConfig

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Manages asyncpg connection pool for PostgreSQL.

    Args:
        config: Database connection configuration.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self._pool: Pool | None = None

    @property
    def is_initialized(self) -> bool:
        """Check if the connection pool is initialized."""
        return self._pool is not None

    async def initialize(self) -> None:
        """Initialize the connection pool.

        Creates an asyncpg connection pool with the configured settings.
        This method is idempotent - calling it multiple times has no effect.
        """
        if self._pool is not None:
            logger.debug("Connection pool already initialized")
            return

        logger.info(
            f"Initializing connection pool for {self.config.name} "
            f"({self.config.host}:{self.config.port}/{self.config.database})"
        )

        ssl_context = "require" if self.config.ssl else False

        self._pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password.get_secret_value(),
            min_size=self.config.min_pool_size,
            max_size=self.config.max_pool_size,
            ssl=ssl_context,
            command_timeout=60,  # Default command timeout
        )

        logger.info(f"Connection pool initialized successfully for {self.config.name}")

    async def close(self) -> None:
        """Close the connection pool and release all connections.

        This method is safe to call multiple times.
        """
        if self._pool is None:
            return

        logger.info(f"Closing connection pool for {self.config.name}")
        await self._pool.close()
        self._pool = None
        logger.info(f"Connection pool closed for {self.config.name}")

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[Connection]:
        """Acquire a connection from the pool.

        Yields:
            An asyncpg Connection instance.

        Raises:
            RuntimeError: If the pool is not initialized.
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized. Call initialize() first.")

        async with self._pool.acquire() as conn:
            yield conn
