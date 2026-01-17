"""PostgreSQL connection pool management."""

from typing import Any

import asyncpg
from asyncpg import Pool

from app.core.types import ConnectionProvider


class PostgreSQLConnectionProvider(ConnectionProvider):
    """PostgreSQL connection pool manager using asyncpg."""

    _pools: dict[str, Pool] = {}

    async def get_pool(self, url: str) -> Pool:
        """Get or create a connection pool for a database URL."""
        if url not in self._pools:
            self._pools[url] = await asyncpg.create_pool(url, min_size=1, max_size=5)
        return self._pools[url]

    async def test_connection(self, url: str) -> bool:
        """Test if a database connection URL is valid."""
        try:
            pool = await self.get_pool(url)
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def close_pool(self, url: str) -> None:
        """Close a connection pool."""
        if url in self._pools:
            await self._pools[url].close()
            del self._pools[url]

    async def close_all(self) -> None:
        """Close all connection pools."""
        for pool in self._pools.values():
            await pool.close()
        self._pools.clear()

    async def execute(self, url: str, query: str, *args: Any) -> list[dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        pool = await self.get_pool(url)
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
