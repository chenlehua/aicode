"""SQLite database CRUD operations for stored connections."""

import json
from datetime import datetime

from app.database import get_db
from app.models.database import (
    ColumnMetadata,
    DatabaseMetadata,
    DatabaseResponse,
    DatabaseType,
    DatabaseWithMetadata,
    TableMetadata,
    detect_database_type,
)
from app.services.metadata_factory import MetadataFactory


def serialize_table_metadata(table: TableMetadata) -> str:
    """Serialize a single table metadata to JSON string."""
    return json.dumps(
        [
            {
                "name": c.name,
                "data_type": c.data_type,
                "is_nullable": c.is_nullable,
                "default_value": c.default_value,
                "is_primary_key": c.is_primary_key,
                "is_foreign_key": c.is_foreign_key,
                "references": c.references,
            }
            for c in table.columns
        ]
    )


def deserialize_table_metadata(
    table_name: str, table_type: str, columns_json: str, fetched_at: str
) -> TableMetadata:
    """Deserialize a single table metadata from JSON string."""
    columns_data = json.loads(columns_json)
    columns = [
        ColumnMetadata(
            name=c["name"],
            data_type=c["data_type"],
            is_nullable=c["is_nullable"],
            default_value=c.get("default_value"),
            is_primary_key=c.get("is_primary_key", False),
            is_foreign_key=c.get("is_foreign_key", False),
            references=c.get("references"),
        )
        for c in columns_data
    ]

    return TableMetadata(
        table_name=table_name,
        table_type=table_type,
        columns=columns,
        fetched_at=datetime.fromisoformat(fetched_at),
    )


class DatabaseService:
    """Service for managing database connections in SQLite."""

    @staticmethod
    async def list_databases() -> list[DatabaseResponse]:
        """List all stored database connections."""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT name, url, description, created_at, updated_at FROM databases ORDER BY name"
            )
            rows = await cursor.fetchall()
            return [
                DatabaseResponse(
                    name=row["name"],
                    url=row["url"],
                    description=row["description"] or "",
                    database_type=detect_database_type(row["url"]),
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
                "SELECT name, url, description, created_at, updated_at FROM databases WHERE name = ?",
                (name,),
            )
            db_row = await cursor.fetchone()
            if not db_row:
                return None

            url = db_row["url"]
            db_type = detect_database_type(url)

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
                    table_metadata = deserialize_table_metadata(
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
                    database_type=db_type,
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
                    database_type=db_type,
                    tables=[],
                    views=[],
                    table_count=0,
                    view_count=0,
                    fetched_at=datetime.now(),
                )

            return DatabaseWithMetadata(
                name=db_row["name"],
                url=url,
                description=db_row["description"] or "",
                database_type=db_type,
                created_at=datetime.fromisoformat(db_row["created_at"]),
                updated_at=datetime.fromisoformat(db_row["updated_at"]),
                metadata=metadata,
            )
        finally:
            await db.close()

    @staticmethod
    async def create_or_update_database(
        name: str, url: str, description: str = ""
    ) -> DatabaseWithMetadata:
        """Create or update a database connection and fetch metadata."""
        db = await get_db()
        try:
            now = datetime.now()
            now_iso = now.isoformat()
            db_type = detect_database_type(url)

            # Upsert database connection
            await db.execute(
                """
                INSERT INTO databases (name, url, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    url = excluded.url,
                    description = excluded.description,
                    updated_at = excluded.updated_at
                """,
                (name, url, description, now_iso, now_iso),
            )

            # Fetch and cache metadata using factory
            metadata = await MetadataFactory.fetch_metadata(name, url)

            # Delete old metadata
            await db.execute("DELETE FROM metadata WHERE database_name = ?", (name,))

            # Insert new metadata
            for table in metadata.tables + metadata.views:
                # table.table_type is already "table" or "view" from MetadataService
                await db.execute(
                    """
                    INSERT INTO metadata (
                        database_name, table_name, table_type, columns_json, fetched_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        table.table_name,
                        table.table_type,
                        serialize_table_metadata(table),
                        table.fetched_at.isoformat(),
                    ),
                )

            await db.commit()

            return DatabaseWithMetadata(
                name=name,
                url=url,
                description=description,
                database_type=db_type,
                created_at=now,
                updated_at=now,
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
