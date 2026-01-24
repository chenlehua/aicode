"""Database schema models for pg-mcp."""

from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    """Information about a table column."""

    name: str = Field(description="Column name")
    data_type: str = Field(description="PostgreSQL data type")
    is_nullable: bool = Field(default=True, description="Whether the column allows NULL")
    is_primary_key: bool = Field(default=False, description="Whether this is a primary key column")
    is_foreign_key: bool = Field(default=False, description="Whether this is a foreign key column")
    default_value: str | None = Field(default=None, description="Default value expression")
    comment: str | None = Field(default=None, description="Column comment")
    foreign_table: str | None = Field(default=None, description="Referenced table for foreign key")
    foreign_column: str | None = Field(default=None, description="Referenced column for foreign key")


class IndexInfo(BaseModel):
    """Information about a table index."""

    name: str = Field(description="Index name")
    columns: list[str] = Field(description="Columns in the index")
    is_unique: bool = Field(default=False, description="Whether the index is unique")
    is_primary: bool = Field(default=False, description="Whether this is the primary key index")
    index_type: str = Field(default="btree", description="Index type (btree, hash, gin, gist, etc.)")


class ConstraintInfo(BaseModel):
    """Information about a table constraint."""

    name: str = Field(description="Constraint name")
    constraint_type: str = Field(description="Constraint type (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)")
    columns: list[str] = Field(description="Columns involved in the constraint")
    definition: str | None = Field(default=None, description="Constraint definition for CHECK constraints")


class TableInfo(BaseModel):
    """Information about a database table."""

    schema_name: str = Field(default="public", description="Schema name")
    name: str = Field(description="Table name")
    columns: list[ColumnInfo] = Field(default_factory=list, description="Table columns")
    indexes: list[IndexInfo] = Field(default_factory=list, description="Table indexes")
    constraints: list[ConstraintInfo] = Field(default_factory=list, description="Table constraints")
    comment: str | None = Field(default=None, description="Table comment")
    estimated_row_count: int | None = Field(default=None, description="Estimated row count from pg_class")

    @property
    def full_name(self) -> str:
        """Get fully qualified table name."""
        return f"{self.schema_name}.{self.name}"


class ViewInfo(BaseModel):
    """Information about a database view."""

    schema_name: str = Field(default="public", description="Schema name")
    name: str = Field(description="View name")
    columns: list[ColumnInfo] = Field(default_factory=list, description="View columns")
    definition: str | None = Field(default=None, description="View definition SQL")
    comment: str | None = Field(default=None, description="View comment")

    @property
    def full_name(self) -> str:
        """Get fully qualified view name."""
        return f"{self.schema_name}.{self.name}"


class EnumTypeInfo(BaseModel):
    """Information about a PostgreSQL enum type."""

    schema_name: str = Field(default="public", description="Schema name")
    name: str = Field(description="Enum type name")
    values: list[str] = Field(default_factory=list, description="Enum values")


class ForeignKeyRelation(BaseModel):
    """Information about a foreign key relationship."""

    from_table: str = Field(description="Source table (with schema)")
    from_columns: list[str] = Field(description="Source columns")
    to_table: str = Field(description="Target table (with schema)")
    to_columns: list[str] = Field(description="Target columns")
    constraint_name: str = Field(description="Foreign key constraint name")


class DatabaseSchema(BaseModel):
    """Aggregated database schema information."""

    database_name: str = Field(description="Database name")
    tables: list[TableInfo] = Field(default_factory=list, description="Database tables")
    views: list[ViewInfo] = Field(default_factory=list, description="Database views")
    enum_types: list[EnumTypeInfo] = Field(default_factory=list, description="Enum types")
    foreign_key_relations: list[ForeignKeyRelation] = Field(
        default_factory=list, description="Foreign key relationships"
    )

    def to_llm_context(self) -> str:
        """Convert schema to a string context for LLM.

        Returns:
            A formatted string representation of the schema suitable for LLM context.
        """
        lines: list[str] = [f"Database: {self.database_name}", ""]

        # Tables
        if self.tables:
            lines.append("## Tables")
            lines.append("")
            for table in self.tables:
                lines.append(f"### {table.full_name}")
                if table.comment:
                    lines.append(f"Comment: {table.comment}")
                if table.estimated_row_count is not None:
                    lines.append(f"Estimated rows: ~{table.estimated_row_count:,}")
                lines.append("")
                lines.append("| Column | Type | Nullable | Key | Default | Comment |")
                lines.append("|--------|------|----------|-----|---------|---------|")
                for col in table.columns:
                    key = ""
                    if col.is_primary_key:
                        key = "PK"
                    elif col.is_foreign_key:
                        key = f"FK -> {col.foreign_table}.{col.foreign_column}"
                    nullable = "YES" if col.is_nullable else "NO"
                    default = col.default_value or ""
                    comment = col.comment or ""
                    lines.append(
                        f"| {col.name} | {col.data_type} | {nullable} | {key} | {default} | {comment} |"
                    )
                lines.append("")

        # Views
        if self.views:
            lines.append("## Views")
            lines.append("")
            for view in self.views:
                lines.append(f"### {view.full_name}")
                if view.comment:
                    lines.append(f"Comment: {view.comment}")
                lines.append("")
                lines.append("Columns: " + ", ".join(f"{c.name} ({c.data_type})" for c in view.columns))
                lines.append("")

        # Enum types
        if self.enum_types:
            lines.append("## Enum Types")
            lines.append("")
            for enum in self.enum_types:
                values = ", ".join(f"'{v}'" for v in enum.values)
                lines.append(f"- {enum.schema_name}.{enum.name}: [{values}]")
            lines.append("")

        # Foreign key relationships
        if self.foreign_key_relations:
            lines.append("## Relationships")
            lines.append("")
            for fk in self.foreign_key_relations:
                from_cols = ", ".join(fk.from_columns)
                to_cols = ", ".join(fk.to_columns)
                lines.append(f"- {fk.from_table}({from_cols}) -> {fk.to_table}({to_cols})")
            lines.append("")

        return "\n".join(lines)

    def get_table_names(self) -> set[str]:
        """Get all table names (including schema-qualified names).

        Returns:
            Set of table names.
        """
        names: set[str] = set()
        for table in self.tables:
            names.add(table.name)
            names.add(table.full_name)
        for view in self.views:
            names.add(view.name)
            names.add(view.full_name)
        return names
