"""SQLite database CRUD operations for stored connections."""

from datetime import datetime

from app.database import get_db
from app.models.database import (
    DatabaseMetadata,
    DatabaseResponse,
    DatabaseWithMetadata,
    TableMetadata,
)
from app.services.metadata import MetadataService


class DatabaseService:
    """Service for managing database connections in SQLite."""

    @staticmethod
    async def list_databases() -> list[DatabaseResponse]:
        """List all stored database connections."""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT name, url, created_at, updated_at FROM databases ORDER BY name"
            )
            rows = await cursor.fetchall()
            return [
                DatabaseResponse(
                    name=row["name"],
                    url=row["url"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                )
                for row in rows
            ]
        finally:
            await db.close()

    @staticmethod
    async def get_database(name: str) -> DatabaseWithMetadata | None:
        """Get a database connection with its metadata."""
        db = await get_db()
        try:
            # Get database connection info
            cursor = await db.execute(
                "SELECT name, url, created_at, updated_at FROM databases WHERE name = ?",
                (name,),
            )
            db_row = await cursor.fetchone()
            if not db_row:
                return None

            # Get metadata
            cursor = await db.execute(
                "SELECT columns_json, fetched_at FROM metadata WHERE database_name = ?",
                (name,),
            )
            metadata_rows = await cursor.fetchall()

            if metadata_rows:
                # Reconstruct metadata from cached data
                tables: list[TableMetadata] = []
                views: list[TableMetadata] = []
                fetched_at = datetime.now()

                # Get full metadata with table names
                cursor = await db.execute(
                    """
                    SELECT table_name, table_type, columns_json, fetched_at
                    FROM metadata WHERE database_name = ?
                    ORDER BY table_name
                    """,
                    (name,),
                )
                metadata_full_rows = await cursor.fetchall()

                for metadata_row in metadata_full_rows:
                    table_metadata = MetadataService.deserialize_table_metadata(
                        metadata_row["table_name"],
                        metadata_row["table_type"],
                        metadata_row["columns_json"],
                        metadata_row["fetched_at"],
                    )
                    if metadata_row["table_type"] == "table":
                        tables.append(table_metadata)
                    elif metadata_row["table_type"] == "view":
                        views.append(table_metadata)
                    fetched_at = max(
                        fetched_at,
                        datetime.fromisoformat(metadata_row["fetched_at"]),
                    )

                metadata = DatabaseMetadata(
                    database_name=name,
                    tables=tables,
                    views=views,
                    table_count=len(tables),
                    view_count=len(views),
                    fetched_at=fetched_at,
                )
            else:
                # No cached metadata
                metadata = DatabaseMetadata(
                    database_name=name,
                    tables=[],
                    views=[],
                    table_count=0,
                    view_count=0,
                    fetched_at=datetime.now(),
                )

            return DatabaseWithMetadata(
                name=db_row["name"],
                url=db_row["url"],
                metadata=metadata,
            )
        finally:
            await db.close()

    @staticmethod
    async def create_or_update_database(name: str, url: str) -> DatabaseWithMetadata:
        """Create or update a database connection and fetch metadata."""
        db = await get_db()
        try:
            now = datetime.now().isoformat()

            # Upsert database connection
            await db.execute(
                """
                INSERT INTO databases (name, url, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    url = excluded.url,
                    updated_at = excluded.updated_at
                """,
                (name, url, now, now),
            )

            # Fetch and cache metadata
            metadata = await MetadataService.fetch_metadata(name, url)

            # Delete old metadata
            await db.execute("DELETE FROM metadata WHERE database_name = ?", (name,))

            # Insert new metadata
            for table in metadata.tables + metadata.views:
                table_type_str = "table" if table.table_type == "BASE TABLE" else "view"
                await db.execute(
                    """
                    INSERT INTO metadata (
                        database_name, table_name, table_type, columns_json, fetched_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        table.table_name,
                        table_type_str,
                        MetadataService.serialize_table_metadata(table),
                        table.fetched_at.isoformat(),
                    ),
                )

            await db.commit()

            return DatabaseWithMetadata(
                name=name,
                url=url,
                metadata=metadata,
            )
        finally:
            await db.close()

    @staticmethod
    async def delete_database(name: str) -> bool:
        """Delete a database connection and its metadata."""
        db = await get_db()
        try:
            cursor = await db.execute("DELETE FROM databases WHERE name = ?", (name,))
            await db.commit()
            return cursor.rowcount > 0
        finally:
            await db.close()
