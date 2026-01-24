# PostgreSQL MCP Server - Development Guidelines

## Project Overview

A Python MCP server that enables natural language queries to PostgreSQL databases. Uses LLM to generate SQL from user queries, validates SQL safety, executes queries, and returns structured results.

**Tech Stack**: FastMCP, SQLGlot, OpenAI SDK, asyncpg, Pydantic

## Architecture

```
src/pg_mcp/
├── __init__.py
├── __main__.py           # Entry point
├── server.py             # FastMCP server + tool registration
├── config/
│   └── settings.py       # Pydantic Settings configuration
├── models/
│   ├── schema.py         # Database schema models
│   ├── query.py          # Request/response models
│   └── errors.py         # Exception classes
├── database/
│   ├── connection.py     # asyncpg connection pool
│   ├── schema_cache.py   # Schema caching
│   └── service.py        # Database operations
├── llm/
│   ├── client.py         # OpenAI client wrapper
│   ├── prompts.py        # Prompt templates
│   └── service.py        # SQL generation & validation
├── validator/
│   └── sql_validator.py  # SQLGlot-based SQL safety checker
└── query/
    └── service.py        # Query orchestration
```

## Code Quality Standards

### Python Best Practices

1. **Type Hints Required**
   ```python
   # Good
   async def execute_query(self, sql: str, limit: int | None = None) -> QueryResultData:
       ...
   
   # Bad - no type hints
   async def execute_query(self, sql, limit=None):
       ...
   ```

2. **Use Modern Python Syntax (3.10+)**
   ```python
   # Good - use | for union types
   def process(value: str | None) -> dict[str, Any]:
       ...
   
   # Bad - old-style typing
   from typing import Optional, Dict, Any
   def process(value: Optional[str]) -> Dict[str, Any]:
       ...
   ```

3. **Async/Await Everywhere for I/O**
   ```python
   # Good - async for database and HTTP calls
   async def fetch_data(self) -> list[dict]:
       async with self.pool.acquire() as conn:
           return await conn.fetch(query)
   
   # Bad - blocking I/O in async context
   def fetch_data(self) -> list[dict]:
       return psycopg2.connect(...).execute(query)
   ```

4. **Context Managers for Resource Management**
   ```python
   # Good
   async with self.pool.acquire() as conn:
       result = await conn.fetch(sql)
   
   # Bad - manual resource management
   conn = await self.pool.acquire()
   try:
       result = await conn.fetch(sql)
   finally:
       await self.pool.release(conn)
   ```

5. **Dataclasses or Pydantic for Data Structures**
   ```python
   # Good - Pydantic model
   class QueryResult(BaseModel):
       columns: list[str]
       rows: list[list[Any]]
       row_count: int
   
   # Bad - plain dict
   result = {"columns": [...], "rows": [...], "row_count": 0}
   ```

### SOLID Principles

1. **Single Responsibility (S)**
   - `SQLValidator` only validates SQL safety
   - `LLMService` only handles LLM interactions
   - `DatabaseService` only handles database operations
   - `QueryService` orchestrates the workflow

2. **Open/Closed (O)**
   ```python
   # Good - extend via composition
   class SQLValidator:
       def __init__(self, known_tables: set[str] | None = None):
           self.known_tables = known_tables or set()
   
   # Bad - modifying existing class for new features
   ```

3. **Liskov Substitution (L)**
   - All error classes inherit from `QueryError` and maintain the same interface

4. **Interface Segregation (I)**
   - Small, focused interfaces per service
   - Don't add unnecessary methods to classes

5. **Dependency Inversion (D)**
   ```python
   # Good - inject dependencies
   class QueryService:
       def __init__(
           self,
           database_service: DatabaseService,
           llm_service: LLMService,
       ):
           self.database = database_service
           self.llm = llm_service
   
   # Bad - create dependencies internally
   class QueryService:
       def __init__(self):
           self.database = DatabaseService()  # Hard dependency
   ```

### DRY (Don't Repeat Yourself)

```python
# Good - reusable validation
class SQLValidator:
    DANGEROUS_FUNCTIONS = {"pg_read_file", "dblink", ...}
    
    def _check_dangerous_functions(self, statement, sql):
        for node in statement.walk():
            if isinstance(node, exp.Func) and node.name.lower() in self.DANGEROUS_FUNCTIONS:
                raise SQLUnsafeError(...)

# Bad - duplicated logic
def validate_sql_1(sql):
    if "pg_read_file" in sql.lower():
        raise Error()

def validate_sql_2(sql):
    if "pg_read_file" in sql.lower():  # Same check, duplicated
        raise Error()
```

### YAGNI (You Aren't Gonna Need It)

- Don't implement features not in the PRD
- No multi-database switching in v1 (use first configured DB)
- No query history or caching
- No authentication layer (rely on MCP client)

### KISS (Keep It Simple, Stupid)

```python
# Good - simple and clear
def is_safe_query(sql: str) -> bool:
    try:
        parsed = sqlglot.parse(sql, dialect="postgres")
        return len(parsed) == 1 and isinstance(parsed[0], exp.Select)
    except ParseError:
        return False

# Bad - over-engineered
def is_safe_query(sql: str, config: QueryConfig = None, 
                  validator_factory: ValidatorFactory = None,
                  cache: QueryCache = None) -> ValidationResult:
    # 50 lines of unnecessary abstraction
```

## Error Handling

1. **Use Custom Exceptions**
   ```python
   class QueryError(Exception):
       def __init__(self, code: ErrorCode, message: str, details: str | None = None):
           self.code = code
           self.message = message
           self.details = details
   
   class SQLUnsafeError(QueryError):
       def __init__(self, message: str, sql: str | None = None):
           super().__init__(ErrorCode.SQL_UNSAFE, message, sql)
   ```

2. **Catch Specific Exceptions**
   ```python
   # Good
   except asyncpg.QueryCanceledError:
       raise SQLTimeoutError(timeout_ms)
   except asyncpg.PostgresError as e:
       raise SQLExecutionError(str(e), sql)
   
   # Bad
   except Exception as e:
       raise Error(str(e))
   ```

3. **Never Swallow Exceptions Silently**
   ```python
   # Good - log and re-raise or handle
   except Exception as e:
       logger.exception("Unexpected error")
       raise
   
   # Bad - silent failure
   except Exception:
       pass
   ```

## Testing Requirements

### Test Coverage Target: 80%+

### Unit Tests (tests/test_*.py)

```python
# Test naming: test_<method>_<scenario>_<expected>
def test_validate_select_statement_returns_sql():
    validator = SQLValidator()
    result = validator.validate("SELECT * FROM users")
    assert result == "SELECT * FROM users"

def test_validate_insert_statement_raises_unsafe_error():
    validator = SQLValidator()
    with pytest.raises(SQLUnsafeError):
        validator.validate("INSERT INTO users VALUES (1)")

def test_validate_multiple_statements_raises_unsafe_error():
    validator = SQLValidator()
    with pytest.raises(SQLUnsafeError) as exc:
        validator.validate("SELECT 1; DROP TABLE users")
    assert "多条" in str(exc.value)
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_query_flow_success(mock_db, mock_llm):
    service = QueryService(mock_db, mock_llm, QuerySettings())
    response = await service.execute(QueryRequest(query="查询用户"))
    
    assert response.success is True
    assert response.sql is not None
    assert response.result.row_count >= 0
```

### Test Fixtures

```python
@pytest.fixture
def mock_llm_service():
    service = MagicMock()
    service.generate_sql = AsyncMock(return_value="SELECT * FROM users")
    service.validate_result = AsyncMock(return_value=ValidationResult(
        passed=True, message="OK"
    ))
    return service
```

### Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── test_validator.py     # SQLValidator unit tests
├── test_llm.py           # LLMService tests (mocked API)
├── test_database.py      # DatabaseService tests
├── test_query.py         # QueryService integration tests
└── test_server.py        # FastMCP tool tests
```

## Performance Guidelines

1. **Connection Pooling**
   ```python
   # Use asyncpg pool, not per-request connections
   self._pool = await asyncpg.create_pool(
       min_size=2,
       max_size=10,
       command_timeout=60,
   )
   ```

2. **Schema Caching**
   - Cache schema on startup
   - Avoid repeated schema queries
   - Provide manual refresh mechanism

3. **Parallel Execution Where Possible**
   ```python
   # Good - fetch multiple things in parallel
   tables, columns, pks = await asyncio.gather(
       conn.fetch(TABLES_QUERY),
       conn.fetch(COLUMNS_QUERY),
       conn.fetch(PRIMARY_KEYS_QUERY),
   )
   ```

4. **Limit Result Sets**
   ```python
   # Always add LIMIT to prevent huge result sets
   if "LIMIT" not in sql.upper():
       exec_sql = f"{sql.rstrip(';')} LIMIT {limit}"
   ```

5. **Statement Timeout**
   ```python
   await conn.execute(f"SET statement_timeout = {timeout_ms}")
   ```

## Security Requirements

1. **SQL Validation is Mandatory**
   - All SQL must pass through `SQLValidator` before execution
   - Only `SELECT` statements allowed
   - No multi-statement execution

2. **Use SQLGlot AST Parsing**
   ```python
   # Good - AST-based validation
   statements = sqlglot.parse(sql, dialect="postgres")
   if not isinstance(statements[0], exp.Select):
       raise SQLUnsafeError(...)
   
   # Bad - string matching
   if sql.upper().startswith("SELECT"):
       return True  # Easily bypassed
   ```

3. **Block Dangerous Functions**
   ```python
   DANGEROUS_FUNCTIONS = {
       "pg_read_file", "pg_read_binary_file", "pg_ls_dir",
       "lo_import", "lo_export", "dblink", "dblink_exec"
   }
   ```

4. **Never Log Sensitive Data**
   ```python
   # Good - mask password
   logger.info(f"Connecting to {config.host}:{config.port}/{config.database}")
   
   # Bad - logging secrets
   logger.info(f"DSN: {config.dsn}")  # Contains password!
   ```

5. **Use SecretStr for Passwords**
   ```python
   from pydantic import SecretStr
   
   class DatabaseConfig(BaseModel):
       password: SecretStr  # Won't appear in logs/repr
   ```

## Logging Standards

```python
import logging

logger = logging.getLogger(__name__)

# Levels:
# DEBUG: SQL statements, LLM responses
# INFO: Query summaries, startup/shutdown
# WARNING: Validation failures, recoverable errors
# ERROR: Unrecoverable errors, exceptions

logger.info(f"Query returned {result.row_count} rows in {result.execution_time_ms}ms")
logger.warning(f"SQL validation failed: {sql[:100]}")
logger.exception("Unexpected error during query execution")
```

## Pydantic Usage

1. **Use Field for Metadata**
   ```python
   class QuerySettings(BaseSettings):
       default_limit: int = Field(
           default=100,
           ge=1,
           le=10000,
           description="默认返回行数限制"
       )
   ```

2. **Validate at Boundaries**
   ```python
   # Validate input at API boundary
   request = QueryRequest(query=query)  # Validates query is not empty
   ```

3. **Use model_dump_json for Serialization**
   ```python
   return response.model_dump_json(indent=2)
   ```

## Common Patterns

### Async Context Manager Pattern
```python
@asynccontextmanager
async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
    async with self._pool.acquire() as conn:
        yield conn
```

### Service Initialization Pattern
```python
class DatabaseService:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool: Pool | None = None
    
    async def initialize(self) -> None:
        if self._pool is not None:
            return
        self._pool = await asyncpg.create_pool(...)
    
    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None
```

### Error Wrapping Pattern
```python
try:
    result = await external_call()
except ExternalError as e:
    raise InternalError(f"Failed: {e}") from e
```

## File Naming Conventions

- Module files: `snake_case.py`
- Test files: `test_<module>.py`
- Config files: `config.yaml`, `.env`
- No abbreviations in names

## Import Order

```python
# 1. Standard library
import asyncio
import logging
from contextlib import asynccontextmanager

# 2. Third-party
import asyncpg
import sqlglot
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# 3. Local
from .config import Settings
from .models import QueryRequest, QueryResponse
```

## Documentation

- All public functions/classes need docstrings
- Use Google-style docstrings
- Include type hints in signature, not docstring

```python
async def execute_query(self, sql: str, limit: int | None = None) -> QueryResultData:
    """
    Execute a read-only SQL query.
    
    Args:
        sql: The SQL SELECT statement to execute.
        limit: Maximum number of rows to return.
    
    Returns:
        Query result containing columns, rows, and metadata.
    
    Raises:
        SQLExecutionError: If the query fails.
        SQLTimeoutError: If the query times out.
    """
```
