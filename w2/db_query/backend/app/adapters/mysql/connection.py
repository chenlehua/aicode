"""MySQL connection pool management using aiomysql."""

from typing import Any
from urllib.parse import urlparse

import aiomysql

from app.core.types import ConnectionProvider


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


class MySQLConnectionProvider(ConnectionProvider):
    """MySQL connection pool manager using aiomysql."""

    _pools: dict[str, aiomysql.Pool] = {}

    async def get_pool(self, url: str) -> aiomysql.Pool:
        """Get or create a connection pool for a database URL."""
        if url not in self._pools:
            params = parse_mysql_url(url)
            self._pools[url] = await aiomysql.create_pool(
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
        return self._pools[url]

    async def test_connection(self, url: str) -> bool:
        """Test if a database connection URL is valid."""
        try:
            pool = await self.get_pool(url)
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def close_pool(self, url: str) -> None:
        """Close a connection pool."""
        if url in self._pools:
            self._pools[url].close()
            await self._pools[url].wait_closed()
            del self._pools[url]

    async def close_all(self) -> None:
        """Close all connection pools."""
        for pool in self._pools.values():
            pool.close()
            await pool.wait_closed()
        self._pools.clear()

    async def execute(self, url: str, query: str, *args: Any) -> list[dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        pool = await self.get_pool(url)
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, args if args else None)
                rows = await cursor.fetchall()
                return list(rows) if rows else []
