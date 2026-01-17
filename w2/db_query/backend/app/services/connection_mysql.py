"""MySQL database connection management using aiomysql."""

from typing import Any
from urllib.parse import urlparse

import aiomysql

from app.services.connection_base import ConnectionServiceBase


def parse_mysql_url(url: str) -> dict[str, Any]:
    """Parse MySQL connection URL into connection parameters."""
    # Handle mysql+aiomysql:// prefix
    if url.startswith("mysql+aiomysql://"):
        url = url.replace("mysql+aiomysql://", "mysql://")

    parsed = urlparse(url)

    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": parsed.username or "root",
        "password": parsed.password or "",
        "db": parsed.path.lstrip("/") if parsed.path else "",
    }


class MySQLConnectionService(ConnectionServiceBase):
    """Service for managing MySQL database connections."""

    _pools: dict[str, aiomysql.Pool] = {}

    @classmethod
    async def get_pool(cls, url: str) -> aiomysql.Pool:
        """Get or create a connection pool for a database URL."""
        if url not in cls._pools:
            params = parse_mysql_url(url)
            cls._pools[url] = await aiomysql.create_pool(
                host=params["host"],
                port=params["port"],
                user=params["user"],
                password=params["password"],
                db=params["db"],
                minsize=1,
                maxsize=5,
                autocommit=True,
                charset="utf8mb4",
            )
        return cls._pools[url]

    @classmethod
    async def test_connection(cls, url: str) -> bool:
        """Test if a database connection URL is valid."""
        try:
            pool = await cls.get_pool(url)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    @classmethod
    async def close_pool(cls, url: str) -> None:
        """Close a connection pool."""
        if url in cls._pools:
            cls._pools[url].close()
            await cls._pools[url].wait_closed()
            del cls._pools[url]

    @classmethod
    async def close_all(cls) -> None:
        """Close all connection pools."""
        for pool in cls._pools.values():
            pool.close()
            await pool.wait_closed()
        cls._pools.clear()

    @classmethod
    async def execute(cls, url: str, query: str, *args: Any) -> list[dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        pool = await cls.get_pool(url)
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args if args else None)
                rows = await cursor.fetchall()
                return list(rows) if rows else []
