# Research: Natural Language SQL Explorer

**Feature**: 001-nl-sql-explorer  
**Date**: 2026-01-11  
**Status**: Complete

## Technology Decisions

### 1. LLM Provider: Alibaba Qwen (DashScope)

**Decision**: Use Alibaba's Qwen model via DashScope API instead of OpenAI.

**Rationale**:
- User explicitly specified 通义千问 (Qwen) with DASHSCOPE_API_KEY
- DashScope API is compatible with OpenAI SDK format
- Lower cost for Chinese language queries
- Good performance on SQL generation tasks

**Configuration**:
```python
# Use OpenAI SDK with DashScope base URL
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```

**Alternatives Considered**:
- OpenAI GPT-4: Higher cost, requires separate API key
- Local LLM: Complex setup, variable performance

---

### 2. SQL Parsing: sqlglot

**Decision**: Use sqlglot for SQL parsing and validation.

**Rationale**:
- Pure Python, no external dependencies
- Supports PostgreSQL dialect
- Can parse, validate, and transform SQL
- Enables automatic LIMIT injection

**Usage Pattern**:
```python
import sqlglot

# Parse and validate
try:
    ast = sqlglot.parse_one(sql, dialect="postgres")
except sqlglot.errors.ParseError as e:
    raise InvalidSQLError(str(e))

# Check for SELECT only
if not isinstance(ast, sqlglot.exp.Select):
    raise NonSelectQueryError()

# Add LIMIT if missing
if ast.find(sqlglot.exp.Limit) is None:
    ast = ast.limit(1000)

return ast.sql(dialect="postgres")
```

**Alternatives Considered**:
- pg_query: Requires libpg_query C extension
- sqlparse: Less accurate parsing, no AST manipulation

---

### 3. PostgreSQL Metadata Extraction

**Decision**: Query PostgreSQL information_schema for metadata.

**Rationale**:
- Standard SQL approach works across PostgreSQL versions
- No special extensions required
- Returns comprehensive schema information

**Queries**:
```sql
-- Tables and views
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Columns
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_schema = 'public' AND table_name = :table_name;
```

**Alternatives Considered**:
- pg_catalog: More detailed but PostgreSQL-specific syntax
- psycopg2 introspection: Less portable

---

### 4. Local Storage: SQLite with aiosqlite

**Decision**: Use aiosqlite for async SQLite access at `~/.db_query/db_query.db`.

**Rationale**:
- Async compatible with FastAPI
- Simple file-based storage
- User-specified location
- No separate database server needed

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS databases (
    name TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata (
    database_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    table_type TEXT NOT NULL,
    columns_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    PRIMARY KEY (database_name, table_name),
    FOREIGN KEY (database_name) REFERENCES databases(name)
);
```

---

### 5. Frontend Framework: Refine 5 with Ant Design

**Decision**: Use Refine 5 as the React framework with Ant Design components.

**Rationale**:
- User explicitly specified Refine 5
- Built-in data provider pattern for API integration
- Ant Design provides polished UI components
- Good TypeScript support

**Key Packages**:
```json
{
  "@refinedev/core": "^4.0.0",
  "@refinedev/antd": "^5.0.0",
  "@refinedev/simple-rest": "^5.0.0",
  "antd": "^5.0.0",
  "@monaco-editor/react": "^4.6.0"
}
```

---

### 6. SQL Editor: Monaco Editor

**Decision**: Use Monaco Editor React wrapper for SQL editing.

**Rationale**:
- User explicitly specified Monaco
- VS Code-quality editing experience
- SQL syntax highlighting built-in
- Auto-completion support possible

**Configuration**:
```tsx
import Editor from '@monaco-editor/react';

<Editor
  height="200px"
  language="sql"
  theme="vs-dark"
  value={sql}
  onChange={setSql}
  options={{
    minimap: { enabled: false },
    lineNumbers: 'on',
    scrollBeyondLastLine: false
  }}
/>
```

---

### 7. CORS Configuration

**Decision**: Enable CORS for all origins in FastAPI.

**Rationale**:
- User explicitly specified "允许所有origin"
- Local development tool, security not a concern
- Simplifies frontend-backend communication

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Resolved Clarifications

| Item | Resolution |
|------|------------|
| LLM Provider | Alibaba Qwen via DashScope (DASHSCOPE_API_KEY) |
| Storage Location | ~/.db_query/db_query.db |
| API Prefix | /api/v1 |
| Database Support | PostgreSQL only (initial version) |
| Authentication | None required |
