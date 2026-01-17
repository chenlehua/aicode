"""MySQL metadata extraction."""

from datetime import datetime
from typing import Any

from app.core.types import MetadataProvider
from app.models.database import (
    ColumnMetadata,
    DatabaseMetadata,
    DatabaseType,
    TableMetadata,
)


class MySQLMetadataProvider(MetadataProvider):
    """MySQL metadata extraction provider."""

    def __init__(self, connection_provider: Any) -> None:
        self._connection_provider = connection_provider

    async def fetch_metadata(self, database_name: str, url: str) -> DatabaseMetadata:
        """Fetch metadata for a MySQL database."""
        pool = await self._connection_provider.get_pool(url)

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Get current database name from connection
                await cursor.execute("SELECT DATABASE()")
                row = await cursor.fetchone()
                db_name = row[0] if row else database_name

                # Get all tables and views
                tables_query = """
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    ORDER BY table_name
                """
                await cursor.execute(tables_query, (db_name,))
                table_rows = await cursor.fetchall()

                tables: list[TableMetadata] = []
                views: list[TableMetadata] = []

                for row in table_rows:
                    table_name = row[0]
                    table_type = row[1]

                    # Get columns for this table/view
                    columns = await self._fetch_columns(cursor, db_name, table_name)

                    table_metadata = TableMetadata(
                        table_name=table_name,
                        table_type="table" if table_type == "BASE TABLE" else "view",
                        columns=columns,
                        fetched_at=datetime.now(),
                    )

                    if table_type == "BASE TABLE":
                        tables.append(table_metadata)
                    elif table_type == "VIEW":
                        views.append(table_metadata)

                return DatabaseMetadata(
                    database_name=database_name,
                    database_type=DatabaseType.MYSQL,
                    tables=tables,
                    views=views,
                    table_count=len(tables),
                    view_count=len(views),
                    fetched_at=datetime.now(),
                )

    async def _fetch_columns(
        self, cursor: Any, db_name: str, table_name: str
    ) -> list[ColumnMetadata]:
        """Fetch column metadata for a table/view in MySQL."""
        # Get basic column info from information_schema
        columns_query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                column_key
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        await cursor.execute(columns_query, (db_name, table_name))
        column_rows = await cursor.fetchall()

        # Get primary key columns from statistics
        pk_query = """
            SELECT column_name
            FROM information_schema.statistics
            WHERE table_schema = %s
              AND table_name = %s
              AND index_name = 'PRIMARY'
        """
        await cursor.execute(pk_query, (db_name, table_name))
        pk_rows = await cursor.fetchall()
        pk_columns = {row[0] for row in pk_rows}

        # Get foreign key columns from key_column_usage
        fk_query = """
            SELECT
                kcu.column_name,
                kcu.referenced_table_name,
                kcu.referenced_column_name
            FROM information_schema.key_column_usage kcu
            WHERE kcu.table_schema = %s
              AND kcu.table_name = %s
              AND kcu.referenced_table_name IS NOT NULL
        """
        await cursor.execute(fk_query, (db_name, table_name))
        fk_rows = await cursor.fetchall()
        fk_map = {row[0]: f"{row[1]}.{row[2]}" for row in fk_rows}

        columns: list[ColumnMetadata] = []
        for row in column_rows:
            column_name = row[0]
            is_pk = column_name in pk_columns or row[4] == "PRI"
            is_fk = column_name in fk_map

            columns.append(
                ColumnMetadata(
                    name=column_name,
                    data_type=row[1],
                    is_nullable=row[2] == "YES",
                    default_value=row[3],
                    is_primary_key=is_pk,
                    is_foreign_key=is_fk,
                    references=fk_map.get(column_name),
                )
            )

        return columns
