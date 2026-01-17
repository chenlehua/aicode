"""PostgreSQL metadata extraction."""

from datetime import datetime
from typing import Any

import asyncpg

from app.core.types import MetadataProvider
from app.models.database import (
    ColumnMetadata,
    DatabaseMetadata,
    DatabaseType,
    TableMetadata,
)


class PostgreSQLMetadataProvider(MetadataProvider):
    """PostgreSQL metadata extraction provider."""

    def __init__(self, connection_provider: Any) -> None:
        self._connection_provider = connection_provider

    async def fetch_metadata(self, database_name: str, url: str) -> DatabaseMetadata:
        """Fetch metadata for a PostgreSQL database."""
        pool = await self._connection_provider.get_pool(url)

        async with pool.acquire() as conn:
            # Get all tables and views
            tables_query = """
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            table_rows = await conn.fetch(tables_query)

            tables: list[TableMetadata] = []
            views: list[TableMetadata] = []

            for row in table_rows:
                table_name = row["table_name"]
                table_type = row["table_type"]

                # Get columns for this table/view
                columns = await self._fetch_columns(conn, table_name)

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
                database_type=DatabaseType.POSTGRESQL,
                tables=tables,
                views=views,
                table_count=len(tables),
                view_count=len(views),
                fetched_at=datetime.now(),
            )

    async def _fetch_columns(
        self, conn: asyncpg.Connection, table_name: str
    ) -> list[ColumnMetadata]:
        """Fetch column metadata for a table/view."""
        # Get basic column info
        columns_query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1
            ORDER BY ordinal_position
        """
        column_rows = await conn.fetch(columns_query, table_name)

        # Get primary key columns
        pk_query = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = $1::regclass AND i.indisprimary
        """
        try:
            pk_rows = await conn.fetch(pk_query, table_name)
            pk_columns = {row["attname"] for row in pk_rows}
        except Exception:
            pk_columns = set()

        # Get foreign key columns
        fk_query = """
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                AND tc.table_name = $1
        """
        fk_rows = await conn.fetch(fk_query, table_name)
        fk_map = {
            row["column_name"]: f"{row['foreign_table_name']}.{row['foreign_column_name']}"
            for row in fk_rows
        }

        columns: list[ColumnMetadata] = []
        for row in column_rows:
            column_name = row["column_name"]
            is_pk = column_name in pk_columns
            is_fk = column_name in fk_map

            columns.append(
                ColumnMetadata(
                    name=column_name,
                    data_type=row["data_type"],
                    is_nullable=row["is_nullable"] == "YES",
                    default_value=row["column_default"],
                    is_primary_key=is_pk,
                    is_foreign_key=is_fk,
                    references=fk_map.get(column_name),
                )
            )

        return columns
