"""PostgreSQL database connection management."""

import asyncpg
from asyncpg import Pool


class ConnectionService:
    """Service for managing PostgreSQL database connections."""

    _pools: dict[str, Pool] = {}

    @classmethod
    async def get_pool(cls, url: str) -> Pool:
        """Get or create a connection pool for a database URL."""
        if url not in cls._pools:
            cls._pools[url] = await asyncpg.create_pool(url, min_size=1, max_size=5)
        return cls._pools[url]

    @classmethod
    async def test_connection(cls, url: str) -> bool:
        """Test if a database connection URL is valid."""
        try:
            pool = await cls.get_pool(url)
            async with pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    @classmethod
    async def close_pool(cls, url: str) -> None:
        """Close a connection pool."""
        if url in cls._pools:
            await cls._pools[url].close()
            del cls._pools[url]

    @classmethod
    async def close_all(cls) -> None:
        """Close all connection pools."""
        for pool in cls._pools.values():
            await pool.close()
        cls._pools.clear()
