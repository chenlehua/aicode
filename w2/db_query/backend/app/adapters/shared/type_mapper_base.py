"""Shared type mapping logic."""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.types import TypeMapper


class BaseTypeMapper(TypeMapper, ABC):
    """Base implementation of TypeMapper with common serialization."""

    # Override in subclasses with database-specific mappings
    TYPE_MAP: dict[type, str] = {
        int: "integer",
        float: "float",
        bool: "boolean",
        str: "text",
        bytes: "binary",
        dict: "json",
        list: "array",
    }

    def python_to_db_type(self, value: Any) -> str:
        """Map Python value to database type name."""
        if value is None:
            return "unknown"
        return self.TYPE_MAP.get(type(value), "unknown")

    @abstractmethod
    def db_to_python_type(self, db_type: str) -> type:
        """Map database type name to Python type."""
        ...

    def serialize_value(self, value: Any) -> Any:
        """Common serialization logic."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value
