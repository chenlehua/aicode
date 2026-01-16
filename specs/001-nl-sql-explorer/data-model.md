# Data Model: Natural Language SQL Explorer

**Feature**: 001-nl-sql-explorer  
**Date**: 2026-01-11

## Entities

### DatabaseConnection

Represents a saved database connection.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| name | string | Unique identifier/display name | Primary key, required |
| url | string | PostgreSQL connection URL | Required, validated format |
| createdAt | datetime | When connection was added | Auto-generated |
| updatedAt | datetime | Last modification time | Auto-updated |

**Validation Rules**:
- `name`: 1-64 characters, alphanumeric with underscores/hyphens
- `url`: Must match PostgreSQL URL pattern `postgres://...`

**State Transitions**:
- Created → Active (on successful connection test)
- Active → Updated (on URL change)
- Any → Deleted (on user removal)

---

### DatabaseMetadata

Aggregated metadata for a database, containing all tables and views.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| databaseName | string | Reference to database connection | Foreign key to DatabaseConnection |
| tables | TableMetadata[] | List of all tables | Required |
| views | TableMetadata[] | List of all views | Required |
| tableCount | number | Total number of tables | >= 0 |
| viewCount | number | Total number of views | >= 0 |
| fetchedAt | datetime | When metadata was last fetched | Auto-generated |

**Usage**: This entity is used as the API response when retrieving database metadata.
It provides a structured view of the entire database schema.

---

### TableMetadata

Cached schema information for a table or view.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| databaseName | string | Reference to parent database | Foreign key to DatabaseConnection |
| tableName | string | Name of table/view | Required |
| tableType | string | "table" or "view" | Enum: table, view |
| columns | ColumnMetadata[] | List of column definitions | Required, non-empty |
| fetchedAt | datetime | When metadata was retrieved | Auto-generated |

**Composite Key**: (databaseName, tableName)

---

### ColumnMetadata

Represents a column within a table/view (embedded in TableMetadata).

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| name | string | Column name | Required |
| dataType | string | PostgreSQL data type | Required |
| isNullable | boolean | Whether NULL is allowed | Required |
| defaultValue | string? | Default value expression | Optional |
| isPrimaryKey | boolean | Whether column is part of primary key | Required |
| isForeignKey | boolean | Whether column is a foreign key | Required |
| references | string? | Referenced table.column if foreign key | Optional |

**Additional Fields**: Added `isPrimaryKey`, `isForeignKey`, and `references` for better schema understanding
and improved LLM context when generating SQL queries.

---

### QueryRequest

Input for executing a SQL query.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| sql | string | SQL query to execute | Required, must be valid SELECT |

---

### NaturalQueryRequest

Input for generating SQL from natural language.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| prompt | string | Natural language description | Required, 1-1000 chars |

---

### QueryResult

Output from a successful query execution.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| columns | ColumnInfo[] | Column names and types | Required |
| rows | any[][] | Result data as 2D array | Required |
| rowCount | number | Number of rows returned | >= 0 |
| truncated | boolean | Whether results were limited | Required |
| executionTimeMs | number | Query execution time | >= 0 |

---

### ColumnInfo

Column metadata in query results.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| name | string | Column name | Required |
| dataType | string | PostgreSQL data type | Required |

---

### GeneratedSQL

Output from natural language query generation.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| sql | string | Generated SQL query | Required, valid SELECT |
| explanation | string? | LLM explanation of the query | Optional |

---

### ErrorResponse

Standard error response format.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| error | string | Error type/code | Required |
| message | string | Human-readable description | Required |
| details | object? | Additional error context | Optional |

---

### QueryHistory

Stores executed query history for each database.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | number | Unique identifier | Primary key, auto-increment |
| databaseName | string | Reference to database | Foreign key to DatabaseConnection |
| sql | string | Executed SQL query | Required |
| queryType | string | "manual" or "natural" | Enum: manual, natural |
| naturalPrompt | string? | Original NL prompt (if natural) | Optional |
| rowCount | number | Number of rows returned | >= 0 |
| executionTimeMs | number | Query execution time | >= 0 |
| status | string | "success" or "error" | Enum: success, error |
| errorMessage | string? | Error message if failed | Optional |
| executedAt | datetime | When query was executed | Auto-generated |

**Validation Rules**:
- `queryType`: Must be "manual" or "natural"
- `naturalPrompt`: Required when queryType is "natural"
- `status`: Must be "success" or "error"
- `errorMessage`: Required when status is "error"

---

## Relationships

```
DatabaseConnection (1) ──────< (1) DatabaseMetadata (aggregated view)
       │                              │
       │                              └── Contains TableMetadata[]
       │                                         │
       │                                         └── Contains ColumnMetadata[]
       │
       ├──────< (N) TableMetadata (stored individually)
       │               │
       │               └── Contains ColumnMetadata[]
       │
       └──────< (N) QueryHistory
                     │
                     └── Contains executed query history
```

**Note**: DatabaseMetadata is an aggregated response model (not stored separately).
TableMetadata records are stored individually in SQLite and assembled into
DatabaseMetadata when requested via API.

## Storage Schema (SQLite)

```sql
-- ~/.db_query/db_query.db

CREATE TABLE IF NOT EXISTS databases (
    name TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS metadata (
    database_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    table_type TEXT NOT NULL CHECK (table_type IN ('table', 'view')),
    columns_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (database_name, table_name),
    FOREIGN KEY (database_name) REFERENCES databases(name) ON DELETE CASCADE
);

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
);

CREATE INDEX idx_metadata_database ON metadata(database_name);
CREATE INDEX idx_query_history_database ON query_history(database_name);
CREATE INDEX idx_query_history_executed_at ON query_history(executed_at DESC);
```

## Pydantic Models (Backend)

```python
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from datetime import datetime
from typing import Any


class CamelModel(BaseModel):
    """Base model with camelCase JSON serialization."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class DatabaseCreate(CamelModel):
    url: str = Field(..., pattern=r"^postgres(ql)?://.*")


class DatabaseResponse(CamelModel):
    name: str
    url: str
    created_at: datetime
    updated_at: datetime


class ColumnMetadata(CamelModel):
    name: str
    data_type: str
    is_nullable: bool
    default_value: str | None = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: str | None = None  # "table.column" format


class TableMetadata(CamelModel):
    table_name: str
    table_type: str  # "table" | "view"
    columns: list[ColumnMetadata]
    fetched_at: datetime


class DatabaseMetadata(CamelModel):
    database_name: str
    tables: list[TableMetadata]
    views: list[TableMetadata]
    table_count: int
    view_count: int
    fetched_at: datetime


class DatabaseWithMetadata(CamelModel):
    name: str
    url: str
    metadata: DatabaseMetadata


class QueryRequest(CamelModel):
    sql: str


class NaturalQueryRequest(CamelModel):
    prompt: str = Field(..., min_length=1, max_length=1000)


class ColumnInfo(CamelModel):
    name: str
    data_type: str


class QueryResult(CamelModel):
    columns: list[ColumnInfo]
    rows: list[list[Any]]
    row_count: int
    truncated: bool
    execution_time_ms: int


class GeneratedSQL(CamelModel):
    sql: str
    explanation: str | None = None


class ErrorResponse(CamelModel):
    error: str
    message: str
    details: dict[str, Any] | None = None


class QueryHistoryItem(CamelModel):
    id: int
    database_name: str
    sql: str
    query_type: str  # "manual" | "natural"
    natural_prompt: str | None = None
    row_count: int
    execution_time_ms: int
    status: str  # "success" | "error"
    error_message: str | None = None
    executed_at: datetime


class QueryHistoryList(CamelModel):
    items: list[QueryHistoryItem]
    total: int
    page: int
    page_size: int
```

## TypeScript Interfaces (Frontend)

```typescript
interface Database {
  name: string;
  url: string;
  createdAt: string;
  updatedAt: string;
}

interface ColumnMetadata {
  name: string;
  dataType: string;
  isNullable: boolean;
  defaultValue?: string;
  isPrimaryKey: boolean;
  isForeignKey: boolean;
  references?: string;  // "table.column" format
}

interface TableMetadata {
  tableName: string;
  tableType: 'table' | 'view';
  columns: ColumnMetadata[];
  fetchedAt: string;
}

interface DatabaseMetadata {
  databaseName: string;
  tables: TableMetadata[];
  views: TableMetadata[];
  tableCount: number;
  viewCount: number;
  fetchedAt: string;
}

interface DatabaseWithMetadata extends Database {
  metadata: DatabaseMetadata;
}

interface QueryRequest {
  sql: string;
}

interface NaturalQueryRequest {
  prompt: string;
}

interface ColumnInfo {
  name: string;
  dataType: string;
}

interface QueryResult {
  columns: ColumnInfo[];
  rows: unknown[][];
  rowCount: number;
  truncated: boolean;
  executionTimeMs: number;
}

interface GeneratedSQL {
  sql: string;
  explanation?: string;
}

interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

interface QueryHistoryItem {
  id: number;
  databaseName: string;
  sql: string;
  queryType: 'manual' | 'natural';
  naturalPrompt?: string;
  rowCount: number;
  executionTimeMs: number;
  status: 'success' | 'error';
  errorMessage?: string;
  executedAt: string;
}

interface QueryHistoryList {
  items: QueryHistoryItem[];
  total: number;
  page: number;
  pageSize: number;
}
```
