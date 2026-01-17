"""SQLite database connection and initialization."""

import aiosqlite

from app.config import settings


async def get_db() -> aiosqlite.Connection:
    """Get async SQLite database connection."""
    # Ensure database directory exists
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(settings.db_path))
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    """Initialize database schema."""
    db = await get_db()
    try:
        # Create databases table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS databases (
                name TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )

        # Add description column if not exists (for migration)
        try:
            await db.execute("ALTER TABLE databases ADD COLUMN description TEXT DEFAULT ''")
        except Exception:
            pass  # Column already exists

        # Create metadata table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                database_name TEXT NOT NULL,
                table_name TEXT NOT NULL,
                table_type TEXT NOT NULL CHECK (table_type IN ('table', 'view')),
                columns_json TEXT NOT NULL,
                fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (database_name, table_name),
                FOREIGN KEY (database_name) REFERENCES databases(name) ON DELETE CASCADE
            )
            """
        )

        # Create query_history table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                database_name TEXT NOT NULL,
                sql TEXT NOT NULL,
                query_type TEXT NOT NULL CHECK (query_type IN ('manual', 'natural')),
                natural_prompt TEXT,
                row_count INTEGER NOT NULL DEFAULT 0,
                execution_time_ms INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL CHECK (status IN ('success', 'error')),
                error_message TEXT,
                executed_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (database_name) REFERENCES databases(name) ON DELETE CASCADE
            )
            """
        )

        # Create indexes
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_metadata_database ON metadata(database_name)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_query_history_database ON query_history(database_name)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_query_history_executed_at "
            "ON query_history(executed_at DESC)"
        )

        await db.commit()
    finally:
        await db.close()
