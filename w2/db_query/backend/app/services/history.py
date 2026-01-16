"""Query history storage and retrieval."""

from datetime import datetime

from app.database import get_db
from app.models.history import QueryHistoryItem, QueryHistoryList


class HistoryService:
    """Service for managing query history in SQLite."""

    @staticmethod
    async def save_query(
        database_name: str,
        sql: str,
        query_type: str,
        natural_prompt: str | None,
        row_count: int,
        execution_time_ms: int,
        status: str,
        error_message: str | None = None,
    ) -> int:
        """Save a query execution to history."""
        db = await get_db()
        try:
            cursor = await db.execute(
                """
                INSERT INTO query_history (
                    database_name, sql, query_type, natural_prompt,
                    row_count, execution_time_ms, status, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    database_name,
                    sql,
                    query_type,
                    natural_prompt,
                    row_count,
                    execution_time_ms,
                    status,
                    error_message,
                ),
            )
            await db.commit()
            return cursor.lastrowid or 0
        finally:
            await db.close()

    @staticmethod
    async def get_history(
        database_name: str, page: int = 1, page_size: int = 20
    ) -> QueryHistoryList:
        """Get query history for a database."""
        db = await get_db()
        try:
            offset = (page - 1) * page_size

            # Get total count
            cursor = await db.execute(
                "SELECT COUNT(*) as total FROM query_history WHERE database_name = ?",
                (database_name,),
            )
            total_row = await cursor.fetchone()
            total = total_row["total"] if total_row else 0

            # Get paginated results
            cursor = await db.execute(
                """
                SELECT id, database_name, sql, query_type, natural_prompt,
                       row_count, execution_time_ms, status, error_message, executed_at
                FROM query_history
                WHERE database_name = ?
                ORDER BY executed_at DESC
                LIMIT ? OFFSET ?
                """,
                (database_name, page_size, offset),
            )
            rows = await cursor.fetchall()

            items = [
                QueryHistoryItem(
                    id=row["id"],
                    database_name=row["database_name"],
                    sql=row["sql"],
                    query_type=row["query_type"],
                    natural_prompt=row["natural_prompt"],
                    row_count=row["row_count"],
                    execution_time_ms=row["execution_time_ms"],
                    status=row["status"],
                    error_message=row["error_message"],
                    executed_at=datetime.fromisoformat(row["executed_at"]),
                )
                for row in rows
            ]

            return QueryHistoryList(
                items=items,
                total=total,
                page=page,
                page_size=page_size,
            )
        finally:
            await db.close()
