"""PostgreSQL type mapping."""

from app.adapters.shared.type_mapper_base import BaseTypeMapper


class PostgreSQLTypeMapper(BaseTypeMapper):
    """PostgreSQL-specific type mapper."""

    TYPE_MAP = {
        int: "integer",
        float: "numeric",
        bool: "boolean",
        str: "text",
        bytes: "bytea",
        dict: "jsonb",
        list: "array",
    }

    def db_to_python_type(self, db_type: str) -> type:
        """Map PostgreSQL type to Python type."""
        mapping = {
            "integer": int,
            "bigint": int,
            "smallint": int,
            "numeric": float,
            "real": float,
            "double precision": float,
            "boolean": bool,
            "text": str,
            "varchar": str,
            "char": str,
            "character varying": str,
            "bytea": bytes,
            "jsonb": dict,
            "json": dict,
        }
        return mapping.get(db_type.lower(), str)
