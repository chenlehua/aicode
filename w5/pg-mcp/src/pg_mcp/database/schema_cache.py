"""Database schema caching for pg-mcp."""

import logging

from asyncpg import Connection

from pg_mcp.models import (
    ColumnInfo,
    DatabaseSchema,
    EnumTypeInfo,
    ForeignKeyRelation,
    IndexInfo,
    TableInfo,
    ViewInfo,
)

logger = logging.getLogger(__name__)


# SQL Queries for schema information
TABLES_QUERY = """
SELECT
    t.table_schema,
    t.table_name,
    obj_description(
        (quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass,
        'pg_class'
    ) as table_comment,
    c.reltuples::bigint as estimated_row_count
FROM information_schema.tables t
LEFT JOIN pg_class c ON c.relname = t.table_name
    AND c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = t.table_schema)
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
    AND t.table_type = 'BASE TABLE'
ORDER BY t.table_schema, t.table_name;
"""

COLUMNS_QUERY = """
SELECT
    c.table_schema,
    c.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable = 'YES' as is_nullable,
    c.column_default,
    col_description(
        (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass,
        c.ordinal_position
    ) as column_comment
FROM information_schema.columns c
WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
"""

PRIMARY_KEYS_QUERY = """
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema');
"""

FOREIGN_KEYS_QUERY = """
SELECT
    tc.table_schema as from_schema,
    tc.table_name as from_table,
    kcu.column_name as from_column,
    ccu.table_schema as to_schema,
    ccu.table_name as to_table,
    ccu.column_name as to_column,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema');
"""

INDEXES_QUERY = """
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename, indexname;
"""

VIEWS_QUERY = """
SELECT
    v.table_schema,
    v.table_name,
    v.view_definition,
    obj_description(
        (quote_ident(v.table_schema) || '.' || quote_ident(v.table_name))::regclass,
        'pg_class'
    ) as view_comment
FROM information_schema.views v
WHERE v.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY v.table_schema, v.table_name;
"""

ENUM_TYPES_QUERY = """
SELECT
    n.nspname as schema_name,
    t.typname as type_name,
    array_agg(e.enumlabel ORDER BY e.enumsortorder) as enum_values
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_namespace n ON t.typnamespace = n.oid
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
GROUP BY n.nspname, t.typname
ORDER BY n.nspname, t.typname;
"""


class SchemaCache:
    """Caches database schema information.

    Args:
        database_name: Name of the database for this cache.
    """

    def __init__(self, database_name: str) -> None:
        self.database_name = database_name
        self._schema: DatabaseSchema | None = None

    @property
    def schema(self) -> DatabaseSchema | None:
        """Get the cached schema."""
        return self._schema

    def get_table_names(self) -> set[str]:
        """Get all cached table names.

        Returns:
            Set of table names, or empty set if schema not loaded.
        """
        if self._schema is None:
            return set()
        return self._schema.get_table_names()

    def get_column_names(self, table: str) -> set[str]:
        """Get column names for a specific table.

        Args:
            table: Table name (with or without schema prefix).

        Returns:
            Set of column names, or empty set if table not found.
        """
        if self._schema is None:
            return set()

        for t in self._schema.tables:
            if t.name == table or t.full_name == table:
                return {col.name for col in t.columns}

        for v in self._schema.views:
            if v.name == table or v.full_name == table:
                return {col.name for col in v.columns}

        return set()

    async def refresh(self, conn: Connection) -> DatabaseSchema:
        """Refresh the schema cache from the database.

        Args:
            conn: Active database connection.

        Returns:
            The updated DatabaseSchema.
        """
        logger.info(f"Refreshing schema cache for {self.database_name}")

        # Fetch all schema information in parallel
        tables_data, columns_data, pk_data, fk_data, indexes_data, views_data, enum_data = (
            await conn.fetch(TABLES_QUERY),
            await conn.fetch(COLUMNS_QUERY),
            await conn.fetch(PRIMARY_KEYS_QUERY),
            await conn.fetch(FOREIGN_KEYS_QUERY),
            await conn.fetch(INDEXES_QUERY),
            await conn.fetch(VIEWS_QUERY),
            await conn.fetch(ENUM_TYPES_QUERY),
        )

        # Build primary key lookup
        pk_lookup: dict[tuple[str, str], set[str]] = {}
        for row in pk_data:
            key = (row["table_schema"], row["table_name"])
            if key not in pk_lookup:
                pk_lookup[key] = set()
            pk_lookup[key].add(row["column_name"])

        # Build foreign key lookup
        fk_lookup: dict[tuple[str, str, str], tuple[str, str]] = {}
        for row in fk_data:
            key = (row["from_schema"], row["from_table"], row["from_column"])
            fk_lookup[key] = (
                f"{row['to_schema']}.{row['to_table']}",
                row["to_column"],
            )

        # Build columns lookup
        columns_lookup: dict[tuple[str, str], list[ColumnInfo]] = {}
        for row in columns_data:
            key = (row["table_schema"], row["table_name"])
            if key not in columns_lookup:
                columns_lookup[key] = []

            is_pk = row["column_name"] in pk_lookup.get(key, set())
            fk_key = (row["table_schema"], row["table_name"], row["column_name"])
            fk_info = fk_lookup.get(fk_key)

            columns_lookup[key].append(
                ColumnInfo(
                    name=row["column_name"],
                    data_type=row["data_type"],
                    is_nullable=row["is_nullable"],
                    is_primary_key=is_pk,
                    is_foreign_key=fk_info is not None,
                    default_value=row["column_default"],
                    comment=row["column_comment"],
                    foreign_table=fk_info[0] if fk_info else None,
                    foreign_column=fk_info[1] if fk_info else None,
                )
            )

        # Build indexes lookup
        indexes_lookup: dict[tuple[str, str], list[IndexInfo]] = {}
        for row in indexes_data:
            key = (row["schemaname"], row["tablename"])
            if key not in indexes_lookup:
                indexes_lookup[key] = []

            # Parse index definition to extract columns (simplified)
            indexdef = row["indexdef"] or ""
            is_unique = "UNIQUE" in indexdef.upper()
            is_primary = "PRIMARY" in indexdef.upper()

            # Extract columns from index definition (basic parsing)
            columns: list[str] = []
            if "(" in indexdef and ")" in indexdef:
                cols_str = indexdef.split("(")[-1].split(")")[0]
                columns = [c.strip().strip('"') for c in cols_str.split(",")]

            indexes_lookup[key].append(
                IndexInfo(
                    name=row["indexname"],
                    columns=columns,
                    is_unique=is_unique,
                    is_primary=is_primary,
                )
            )

        # Build tables
        tables: list[TableInfo] = []
        for row in tables_data:
            key = (row["table_schema"], row["table_name"])
            tables.append(
                TableInfo(
                    schema_name=row["table_schema"],
                    name=row["table_name"],
                    columns=columns_lookup.get(key, []),
                    indexes=indexes_lookup.get(key, []),
                    comment=row["table_comment"],
                    estimated_row_count=row["estimated_row_count"] if row["estimated_row_count"] > 0 else None,
                )
            )

        # Build views
        views: list[ViewInfo] = []
        for row in views_data:
            key = (row["table_schema"], row["table_name"])
            views.append(
                ViewInfo(
                    schema_name=row["table_schema"],
                    name=row["table_name"],
                    columns=columns_lookup.get(key, []),
                    definition=row["view_definition"],
                    comment=row["view_comment"],
                )
            )

        # Build enum types
        enum_types: list[EnumTypeInfo] = []
        for row in enum_data:
            enum_types.append(
                EnumTypeInfo(
                    schema_name=row["schema_name"],
                    name=row["type_name"],
                    values=list(row["enum_values"]) if row["enum_values"] else [],
                )
            )

        # Build foreign key relations
        fk_relations: list[ForeignKeyRelation] = []
        fk_grouped: dict[str, dict] = {}
        for row in fk_data:
            constraint = row["constraint_name"]
            if constraint not in fk_grouped:
                fk_grouped[constraint] = {
                    "from_table": f"{row['from_schema']}.{row['from_table']}",
                    "to_table": f"{row['to_schema']}.{row['to_table']}",
                    "from_columns": [],
                    "to_columns": [],
                    "constraint_name": constraint,
                }
            fk_grouped[constraint]["from_columns"].append(row["from_column"])
            fk_grouped[constraint]["to_columns"].append(row["to_column"])

        for fk in fk_grouped.values():
            fk_relations.append(ForeignKeyRelation(**fk))

        # Create schema
        self._schema = DatabaseSchema(
            database_name=self.database_name,
            tables=tables,
            views=views,
            enum_types=enum_types,
            foreign_key_relations=fk_relations,
        )

        logger.info(
            f"Schema cache refreshed: {len(tables)} tables, {len(views)} views, "
            f"{len(enum_types)} enum types, {len(fk_relations)} foreign keys"
        )

        return self._schema
