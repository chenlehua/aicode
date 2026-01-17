"""MySQL type mapping."""

from decimal import Decimal

from app.adapters.shared.type_mapper_base import BaseTypeMapper


class MySQLTypeMapper(BaseTypeMapper):
    """MySQL-specific type mapper."""

    TYPE_MAP = {
        int: "int",
        float: "double",
        bool: "tinyint",
        str: "varchar",
        bytes: "blob",
        dict: "json",
        list: "json",
        Decimal: "decimal",
    }

    def db_to_python_type(self, db_type: str) -> type:
        """Map MySQL type to Python type."""
        mapping = {
            "int": int,
            "integer": int,
            "bigint": int,
            "smallint": int,
            "tinyint": int,
            "mediumint": int,
            "double": float,
            "float": float,
            "decimal": float,
            "numeric": float,
            "varchar": str,
            "char": str,
            "text": str,
            "longtext": str,
            "mediumtext": str,
            "tinytext": str,
            "blob": bytes,
            "longblob": bytes,
            "mediumblob": bytes,
            "tinyblob": bytes,
            "json": dict,
        }
        return mapping.get(db_type.lower(), str)
