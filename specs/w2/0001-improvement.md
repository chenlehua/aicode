# 数据库查询后端架构分析与重构设计方案

## 一、当前架构分析报告

### 1.1 目录结构概览

```
backend/app/
├── main.py                    # FastAPI 应用入口
├── config.py                  # 配置管理
├── database.py                # 应用自身的 SQLite 数据库（存储连接配置）
├── models/                    # Pydantic 数据模型
│   ├── __init__.py           # CamelModel 基类
│   ├── database.py           # 数据库连接和元数据模型
│   ├── query.py              # 查询请求/响应模型
│   ├── history.py            # 历史记录模型
│   └── error.py              # 错误响应模型
├── services/                  # 业务逻辑层
│   ├── connection_base.py    # 连接服务抽象基类
│   ├── connection.py         # PostgreSQL 连接服务
│   ├── connection_mysql.py   # MySQL 连接服务
│   ├── connection_factory.py # 连接工厂
│   ├── metadata.py           # PostgreSQL 元数据服务
│   ├── metadata_mysql.py     # MySQL 元数据服务
│   ├── metadata_factory.py   # 元数据工厂
│   ├── query.py              # PostgreSQL 查询服务
│   ├── query_mysql.py        # MySQL 查询服务
│   ├── query_factory.py      # 查询工厂
│   ├── database.py           # 数据库 CRUD 服务
│   ├── history.py            # 历史记录服务
│   └── llm.py                # LLM SQL 生成服务
└── routers/                   # API 路由层
    ├── __init__.py
    └── databases.py
```

### 1.2 当前架构的核心组件

| 组件 | 职责 | 当前实现状态 |
|------|------|------------|
| **Connection Service** | 数据库连接池管理 | 有抽象基类，PostgreSQL/MySQL 独立实现 |
| **Metadata Service** | 数据库 Schema 元数据提取 | 无抽象基类，PostgreSQL/MySQL 独立实现 |
| **Query Service** | SQL 验证与执行 | 无抽象基类，PostgreSQL/MySQL 独立实现 |
| **Database Service** | 应用级数据库 CRUD | 单一实现，无需抽象 |
| **LLM Service** | 自然语言转 SQL | 单一实现，依赖数据库类型 |

### 1.3 数据流分析

```
用户请求
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Router Layer                              │
│  databases.py                                                    │
│  - 参数验证                                                       │
│  - 调用 Service 层                                                │
│  - 错误处理与响应格式化                                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                              │
├─────────────────┬─────────────────┬────────────────────────────┤
│  DatabaseService│  QueryFactory   │  MetadataFactory            │
│  (应用数据管理)  │  (查询执行)      │  (元数据提取)                │
├─────────────────┴─────────────────┴────────────────────────────┤
│                     ConnectionFactory                           │
│                     (连接池管理)                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                  │
              ▼                                  ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│     PostgreSQL          │      │        MySQL            │
│  - asyncpg              │      │  - aiomysql             │
│  - information_schema   │      │  - information_schema   │
└─────────────────────────┘      └─────────────────────────┘
```

---

## 二、存在的问题和痛点

### 2.1 抽象层不一致

| 服务类型 | 是否有抽象基类 | 是否有工厂类 | 问题描述 |
|---------|--------------|------------|---------|
| Connection | 是 (`ConnectionServiceBase`) | 是 (`ConnectionFactory`) | 设计较好 |
| Metadata | 否 | 是 (`MetadataFactory`) | **缺少抽象基类，接口不统一** |
| Query | 否 | 是 (`QueryFactory`) | **缺少抽象基类，大量重复代码** |

### 2.2 违反 SOLID 原则的具体问题

#### 2.2.1 单一职责原则 (SRP) 违反

**问题1**: `query.py` 和 `query_mysql.py` 混合了多种职责
- SQL 验证逻辑
- LIMIT 注入逻辑
- 类型推断逻辑
- 查询执行逻辑
- 值序列化逻辑

```python
# 当前代码 - query.py 第14-27行
def _infer_pg_type(value: Any) -> str:
    """Infer PostgreSQL type name from Python value."""
    # 这应该是独立的 TypeMapper 类的职责
```

**问题2**: `LLMService` 直接依赖具体的 `QueryService` 和 `MySQLQueryService`

```python
# 当前代码 - llm.py 第139-143行
if db_type == DatabaseType.MYSQL:
    is_valid, error_msg = MySQLQueryService.validate_sql(generated_sql)
else:
    is_valid, error_msg = QueryService.validate_sql(generated_sql)
```

#### 2.2.2 开闭原则 (OCP) 违反

**问题**: 添加新数据库需要修改多个工厂类

```python
# connection_factory.py 第44-46行 - 需要修改
@staticmethod
async def close_all() -> None:
    await PostgreSQLConnectionService.close_all()
    await MySQLConnectionService.close_all()
    # 添加新数据库时必须修改此处
```

```python
# query_factory.py - 每个方法都需要添加新分支
if db_type == DatabaseType.POSTGRESQL:
    return QueryService.validate_sql(sql)
elif db_type == DatabaseType.MYSQL:
    return MySQLQueryService.validate_sql(sql)
# 添加 SQLite 时必须添加新分支
```

#### 2.2.3 里氏替换原则 (LSP) 违反

**问题**: `MetadataService` 和 `MySQLMetadataService` 没有共同的抽象基类，无法互换使用

```python
# metadata.py - PostgreSQL 专用
class MetadataService:
    @staticmethod
    async def fetch_metadata(database_name: str, url: str) -> DatabaseMetadata:
        pool = await ConnectionService.get_pool(url)  # 直接依赖具体实现
```

#### 2.2.4 接口隔离原则 (ISP) 违反

**问题**: `ConnectionServiceBase` 的接口过于宽泛

```python
# connection_base.py - 所有方法都是 @classmethod
class ConnectionServiceBase(ABC):
    _pools: dict[str, Any] = {}  # 类变量在子类间共享可能有问题

    @classmethod
    async def get_pool(cls, url: str) -> Any:  # 返回 Any，类型不明确
```

#### 2.2.5 依赖倒置原则 (DIP) 违反

**问题1**: 高层模块直接依赖低层模块的具体实现

```python
# database.py (service) 第14行
from app.services.metadata import MetadataService  # 直接依赖具体实现

# metadata.py 第9行
from app.services.connection import ConnectionService  # 直接依赖具体实现
```

**问题2**: 工厂类知道所有具体实现

```python
# connection_factory.py 第6-8行
from app.services.connection import PostgreSQLConnectionService
from app.services.connection_base import ConnectionServiceBase
from app.services.connection_mysql import MySQLConnectionService
```

### 2.3 代码重复问题

#### 2.3.1 SQL 验证逻辑重复

`query.py` (第36-64行) 和 `query_mysql.py` (第39-65行) 的 `validate_sql` 方法几乎完全相同，只有 dialect 参数不同。

#### 2.3.2 LIMIT 注入逻辑重复

两个文件的 `inject_limit` 方法结构完全相同。

#### 2.3.3 类型推断逻辑重复

`_infer_pg_type` 和 `_infer_mysql_type` 只有映射表不同。

### 2.4 扩展性问题

添加一个新数据库（如 SQLite）需要：

1. 创建 `connection_sqlite.py`
2. 创建 `metadata_sqlite.py`
3. 创建 `query_sqlite.py`
4. 修改 `connection_factory.py` (3处)
5. 修改 `metadata_factory.py` (1处)
6. 修改 `query_factory.py` (3处)
7. 修改 `models/database.py` 添加类型枚举
8. 修改 `models/error.py` 添加错误码

**至少需要修改 4 个现有文件**，这严重违反了 OCP。

---

## 三、新的接口/抽象层设计方案

### 3.1 设计目标

1. **统一抽象层**: 所有数据库相关服务都有明确的抽象基类
2. **插件式扩展**: 添加新数据库只需添加新文件，不修改现有代码
3. **依赖注入**: 通过注册机制解耦具体实现
4. **职责分离**: 每个类只负责单一职责
5. **类型安全**: 明确的类型定义和协议

### 3.2 整体架构设计

```
┌──────────────────────────────────────────────────────────────────┐
│                         Router Layer                              │
│                     (保持不变)                                     │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Application Services                         │
│  DatabaseService / HistoryService / LLMService                   │
│  (通过 DatabaseAdapter 访问数据库)                                 │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                        DatabaseAdapter                            │
│              (统一的数据库操作门面)                                 │
│  - get_adapter(url) -> DatabaseAdapter                           │
│  - 包装 Connection + Metadata + Query                             │
└──────────────────────────────────┬───────────────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
            ▼                      ▼                      ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ ConnectionProvider│  │ MetadataProvider  │  │   QueryExecutor   │
│    (抽象接口)      │  │    (抽象接口)      │  │    (抽象接口)      │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                       DatabaseRegistry                            │
│            (自动发现和注册数据库实现)                               │
│  register_adapter(db_type, adapter_class)                        │
│  get_adapter_class(db_type) -> type[DatabaseAdapter]             │
└──────────────────────────────────────────────────────────────────┘
          │
          ├─────────────────┬─────────────────┬─────────────────┐
          ▼                 ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────┐
│   PostgreSQL    │ │      MySQL      │ │     SQLite      │ │  未来   │
│    Adapter      │ │     Adapter     │ │    Adapter      │ │ 扩展    │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────┘
```

### 3.3 核心模块设计

#### 3.3.1 新目录结构

```
backend/app/
├── core/                          # 核心抽象和基础设施
│   ├── __init__.py
│   ├── types.py                   # 类型定义和协议
│   ├── exceptions.py              # 统一异常体系
│   └── registry.py                # 数据库适配器注册表
├── adapters/                      # 数据库适配器（插件目录）
│   ├── __init__.py                # 自动加载所有适配器
│   ├── base.py                    # 抽象基类
│   ├── postgresql/                # PostgreSQL 适配器
│   │   ├── __init__.py
│   │   ├── adapter.py             # PostgreSQLAdapter
│   │   ├── connection.py          # 连接管理
│   │   ├── metadata.py            # 元数据提取
│   │   ├── query.py               # 查询执行
│   │   └── types.py               # 类型映射
│   ├── mysql/                     # MySQL 适配器
│   │   ├── __init__.py
│   │   ├── adapter.py
│   │   ├── connection.py
│   │   ├── metadata.py
│   │   ├── query.py
│   │   └── types.py
│   └── sqlite/                    # SQLite 适配器（未来扩展示例）
│       └── ...
├── models/                        # (保持不变)
├── services/                      # 业务服务层
│   ├── __init__.py
│   ├── database.py                # 使用 DatabaseAdapter
│   ├── history.py                 # (保持不变)
│   └── llm.py                     # 使用抽象接口验证
└── routers/                       # (保持不变)
```

---

## 四、详细的实现建议

### 4.1 核心类型定义 (`core/types.py`)

```python
"""Core type definitions and protocols for database adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, TypeVar

from app.models.database import ColumnMetadata, DatabaseMetadata
from app.models.query import QueryResult


class DatabaseType(str, Enum):
    """Supported database types."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    # 未来扩展只需在此添加枚举值


@dataclass(frozen=True)
class DatabaseConfig:
    """Immutable database configuration."""
    url: str
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str | None = None
    password: str | None = None

    @classmethod
    def from_url(cls, url: str) -> "DatabaseConfig":
        """Parse database URL into config object."""
        # URL 解析逻辑
        ...


class SQLDialect(str, Enum):
    """SQL dialects for query parsing."""
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"


# ========== Protocol 定义（接口契约）==========

class ConnectionPool(Protocol):
    """Protocol for database connection pools."""

    async def acquire(self) -> Any:
        """Acquire a connection from the pool."""
        ...

    async def release(self, conn: Any) -> None:
        """Release a connection back to the pool."""
        ...

    async def close(self) -> None:
        """Close all connections in the pool."""
        ...


class ConnectionProvider(ABC):
    """Abstract interface for database connection management."""

    @abstractmethod
    async def get_pool(self, config: DatabaseConfig) -> ConnectionPool:
        """Get or create a connection pool."""
        ...

    @abstractmethod
    async def test_connection(self, config: DatabaseConfig) -> bool:
        """Test if a connection can be established."""
        ...

    @abstractmethod
    async def close_pool(self, config: DatabaseConfig) -> None:
        """Close a specific connection pool."""
        ...

    @abstractmethod
    async def close_all(self) -> None:
        """Close all managed connection pools."""
        ...


class MetadataProvider(ABC):
    """Abstract interface for database metadata extraction."""

    @abstractmethod
    async def fetch_metadata(
        self,
        database_name: str,
        config: DatabaseConfig
    ) -> DatabaseMetadata:
        """Fetch complete database schema metadata."""
        ...

    @abstractmethod
    async def fetch_table_columns(
        self,
        config: DatabaseConfig,
        table_name: str
    ) -> list[ColumnMetadata]:
        """Fetch columns for a specific table."""
        ...


class QueryExecutor(ABC):
    """Abstract interface for SQL query execution."""

    @property
    @abstractmethod
    def dialect(self) -> SQLDialect:
        """The SQL dialect this executor uses."""
        ...

    @property
    @abstractmethod
    def max_rows(self) -> int:
        """Maximum rows to return."""
        ...

    @abstractmethod
    def validate_sql(self, sql: str) -> tuple[bool, str | None]:
        """Validate SQL syntax. Returns (is_valid, error_message)."""
        ...

    @abstractmethod
    def inject_limit(self, sql: str) -> str:
        """Inject LIMIT clause if not present."""
        ...

    @abstractmethod
    async def execute(
        self,
        config: DatabaseConfig,
        sql: str
    ) -> QueryResult:
        """Execute a SQL query and return results."""
        ...


class TypeMapper(ABC):
    """Abstract interface for database type mapping."""

    @abstractmethod
    def python_to_db_type(self, value: Any) -> str:
        """Map Python value to database type name."""
        ...

    @abstractmethod
    def db_to_python_type(self, db_type: str) -> type:
        """Map database type name to Python type."""
        ...

    @abstractmethod
    def serialize_value(self, value: Any) -> Any:
        """Serialize a value for JSON response."""
        ...
```

### 4.2 统一异常体系 (`core/exceptions.py`)

```python
"""Unified exception hierarchy for database operations."""

from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """Standard error codes for database operations."""

    # Connection errors
    CONNECTION_FAILED = "CONNECTION_FAILED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    POOL_EXHAUSTED = "POOL_EXHAUSTED"

    # Query errors
    INVALID_SQL = "INVALID_SQL"
    QUERY_EXECUTION_FAILED = "QUERY_EXECUTION_FAILED"
    QUERY_TIMEOUT = "QUERY_TIMEOUT"

    # Metadata errors
    METADATA_FETCH_FAILED = "METADATA_FETCH_FAILED"
    TABLE_NOT_FOUND = "TABLE_NOT_FOUND"

    # General errors
    UNSUPPORTED_DATABASE = "UNSUPPORTED_DATABASE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class DatabaseError(Exception):
    """Base exception for all database operations."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        """Convert to API error response format."""
        return {
            "error": self.code.value,
            "message": self.message,
            "details": self.details if self.details else None
        }


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, message: str, **kwargs):
        super().__init__(ErrorCode.CONNECTION_FAILED, message, **kwargs)


class AuthenticationError(DatabaseError):
    """Raised when authentication fails."""

    def __init__(self, message: str, **kwargs):
        super().__init__(ErrorCode.AUTHENTICATION_FAILED, message, **kwargs)


class QueryValidationError(DatabaseError):
    """Raised when SQL validation fails."""

    def __init__(self, message: str, sql: str | None = None, **kwargs):
        details = {"sql": sql} if sql else {}
        super().__init__(ErrorCode.INVALID_SQL, message, details=details, **kwargs)


class QueryExecutionError(DatabaseError):
    """Raised when query execution fails."""

    def __init__(self, message: str, sql: str | None = None, **kwargs):
        details = {"sql": sql} if sql else {}
        super().__init__(ErrorCode.QUERY_EXECUTION_FAILED, message, details=details, **kwargs)


class UnsupportedDatabaseError(DatabaseError):
    """Raised when database type is not supported."""

    def __init__(self, db_type: str):
        super().__init__(
            ErrorCode.UNSUPPORTED_DATABASE,
            f"Database type '{db_type}' is not supported",
            details={"database_type": db_type}
        )
```

### 4.3 数据库注册表 (`core/registry.py`)

```python
"""Database adapter registry with auto-discovery."""

from typing import TYPE_CHECKING

from app.core.exceptions import UnsupportedDatabaseError
from app.core.types import DatabaseConfig, DatabaseType

if TYPE_CHECKING:
    from app.adapters.base import DatabaseAdapter


class DatabaseRegistry:
    """
    Central registry for database adapters.

    Implements the Service Locator pattern with support for
    auto-discovery of adapter implementations.
    """

    _adapters: dict[DatabaseType, type["DatabaseAdapter"]] = {}
    _instances: dict[str, "DatabaseAdapter"] = {}  # url -> instance cache

    @classmethod
    def register(cls, db_type: DatabaseType):
        """
        Decorator to register an adapter class.

        Usage:
            @DatabaseRegistry.register(DatabaseType.POSTGRESQL)
            class PostgreSQLAdapter(DatabaseAdapter):
                ...
        """
        def decorator(adapter_class: type["DatabaseAdapter"]) -> type["DatabaseAdapter"]:
            cls._adapters[db_type] = adapter_class
            return adapter_class
        return decorator

    @classmethod
    def get_adapter_class(cls, db_type: DatabaseType) -> type["DatabaseAdapter"]:
        """Get the adapter class for a database type."""
        if db_type not in cls._adapters:
            raise UnsupportedDatabaseError(db_type.value)
        return cls._adapters[db_type]

    @classmethod
    def get_adapter(cls, config: DatabaseConfig) -> "DatabaseAdapter":
        """
        Get or create an adapter instance for the given configuration.

        Caches instances by URL for connection pool reuse.
        """
        cache_key = config.url
        if cache_key not in cls._instances:
            adapter_class = cls.get_adapter_class(config.db_type)
            cls._instances[cache_key] = adapter_class(config)
        return cls._instances[cache_key]

    @classmethod
    def get_adapter_from_url(cls, url: str) -> "DatabaseAdapter":
        """Convenience method to get adapter from URL string."""
        config = DatabaseConfig.from_url(url)
        return cls.get_adapter(config)

    @classmethod
    async def close_all(cls) -> None:
        """Close all cached adapter instances."""
        for adapter in cls._instances.values():
            await adapter.close()
        cls._instances.clear()

    @classmethod
    def registered_types(cls) -> list[DatabaseType]:
        """List all registered database types."""
        return list(cls._adapters.keys())

    @classmethod
    def is_supported(cls, db_type: DatabaseType) -> bool:
        """Check if a database type is supported."""
        return db_type in cls._adapters


def detect_database_type(url: str) -> DatabaseType:
    """Detect database type from URL scheme."""
    url_lower = url.lower()

    if url_lower.startswith(("postgresql://", "postgres://")):
        return DatabaseType.POSTGRESQL
    elif url_lower.startswith(("mysql://", "mysql+aiomysql://")):
        return DatabaseType.MYSQL
    elif url_lower.startswith("sqlite://"):
        return DatabaseType.SQLITE

    raise UnsupportedDatabaseError(url.split("://")[0] if "://" in url else "unknown")
```

### 4.4 适配器抽象基类 (`adapters/base.py`)

```python
"""Abstract base class for database adapters."""

from abc import ABC, abstractmethod
from typing import Any

from app.core.types import (
    ConnectionProvider,
    DatabaseConfig,
    MetadataProvider,
    QueryExecutor,
    SQLDialect,
    TypeMapper,
)
from app.models.database import DatabaseMetadata
from app.models.query import QueryResult


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters.

    This is the main entry point for all database operations.
    Each database type should implement this class.

    The adapter composes specialized providers for different operations:
    - ConnectionProvider: manages connection pools
    - MetadataProvider: extracts schema information
    - QueryExecutor: validates and executes queries
    - TypeMapper: handles type conversions
    """

    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._connection_provider = self._create_connection_provider()
        self._metadata_provider = self._create_metadata_provider()
        self._query_executor = self._create_query_executor()
        self._type_mapper = self._create_type_mapper()

    @property
    def config(self) -> DatabaseConfig:
        """The database configuration."""
        return self._config

    @property
    @abstractmethod
    def dialect(self) -> SQLDialect:
        """The SQL dialect for this database."""
        ...

    @abstractmethod
    def _create_connection_provider(self) -> ConnectionProvider:
        """Factory method for connection provider."""
        ...

    @abstractmethod
    def _create_metadata_provider(self) -> MetadataProvider:
        """Factory method for metadata provider."""
        ...

    @abstractmethod
    def _create_query_executor(self) -> QueryExecutor:
        """Factory method for query executor."""
        ...

    @abstractmethod
    def _create_type_mapper(self) -> TypeMapper:
        """Factory method for type mapper."""
        ...

    # ========== High-level operations ==========

    async def test_connection(self) -> bool:
        """Test if a connection can be established."""
        return await self._connection_provider.test_connection(self._config)

    async def fetch_metadata(self, database_name: str) -> DatabaseMetadata:
        """Fetch complete database schema metadata."""
        return await self._metadata_provider.fetch_metadata(
            database_name, self._config
        )

    def validate_sql(self, sql: str) -> tuple[bool, str | None]:
        """Validate SQL syntax."""
        return self._query_executor.validate_sql(sql)

    def inject_limit(self, sql: str) -> str:
        """Inject LIMIT clause if not present."""
        return self._query_executor.inject_limit(sql)

    async def execute_query(self, sql: str) -> QueryResult:
        """Execute a SQL query."""
        return await self._query_executor.execute(self._config, sql)

    def serialize_value(self, value: Any) -> Any:
        """Serialize a value for JSON response."""
        return self._type_mapper.serialize_value(value)

    def infer_type(self, value: Any) -> str:
        """Infer database type from Python value."""
        return self._type_mapper.python_to_db_type(value)

    async def close(self) -> None:
        """Close all resources held by this adapter."""
        await self._connection_provider.close_all()
```

### 4.5 共享基础实现 (`adapters/shared/`)

为了减少重复代码，创建共享的基础实现：

```python
# adapters/shared/query_base.py
"""Shared query execution logic."""

import re
from abc import ABC

import sqlglot
from sqlglot import exp

from app.core.exceptions import QueryValidationError
from app.core.types import QueryExecutor, SQLDialect


class BaseQueryExecutor(QueryExecutor, ABC):
    """
    Base implementation of QueryExecutor with shared logic.

    Subclasses only need to implement database-specific execution.
    """

    _max_rows: int = 1000

    @property
    def max_rows(self) -> int:
        return self._max_rows

    def validate_sql(self, sql: str) -> tuple[bool, str | None]:
        """
        Validate SQL syntax and ensure it's a SELECT query.

        Uses sqlglot with the appropriate dialect.
        """
        try:
            parsed_statements = sqlglot.parse(sql, dialect=self.dialect.value)

            if len(parsed_statements) > 1:
                return False, "Multiple statements are not allowed"

            if not parsed_statements:
                return False, "No valid statement found"

            parsed = parsed_statements[0]

            if not isinstance(parsed, exp.Select):
                return False, "Only SELECT queries are allowed"

            return True, None

        except Exception as e:
            error_msg = self._clean_error_message(str(e))
            return False, f"SQL syntax error: {error_msg}"

    def inject_limit(self, sql: str) -> str:
        """Inject LIMIT clause if not present."""
        try:
            parsed = sqlglot.parse_one(sql, dialect=self.dialect.value)

            if not isinstance(parsed, exp.Select):
                return sql

            if parsed.args.get("limit"):
                return sql

            limit_expr = exp.Limit(
                expression=exp.Literal(this=str(self.max_rows), is_string=False)
            )
            parsed.set("limit", limit_expr)
            return parsed.sql(dialect=self.dialect.value)

        except Exception:
            # Fallback to string manipulation
            if "LIMIT" not in sql.upper():
                return f"{sql.rstrip(';')} LIMIT {self.max_rows}"
            return sql

    @staticmethod
    def _clean_error_message(error_msg: str) -> str:
        """Remove ANSI escape codes from error messages."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', error_msg)
```

```python
# adapters/shared/type_mapper_base.py
"""Shared type mapping logic."""

from abc import ABC
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.core.types import TypeMapper


class BaseTypeMapper(TypeMapper, ABC):
    """Base implementation of TypeMapper with common serialization."""

    # Override in subclasses
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
        if value is None:
            return "unknown"
        return self.TYPE_MAP.get(type(value), "unknown")

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
```

### 4.6 PostgreSQL 适配器实现示例 (`adapters/postgresql/`)

```python
# adapters/postgresql/__init__.py
"""PostgreSQL database adapter."""

from app.adapters.postgresql.adapter import PostgreSQLAdapter

__all__ = ["PostgreSQLAdapter"]
```

```python
# adapters/postgresql/adapter.py
"""PostgreSQL adapter implementation."""

from app.adapters.base import DatabaseAdapter
from app.adapters.postgresql.connection import PostgreSQLConnectionProvider
from app.adapters.postgresql.metadata import PostgreSQLMetadataProvider
from app.adapters.postgresql.query import PostgreSQLQueryExecutor
from app.adapters.postgresql.types import PostgreSQLTypeMapper
from app.core.registry import DatabaseRegistry
from app.core.types import (
    ConnectionProvider,
    DatabaseConfig,
    DatabaseType,
    MetadataProvider,
    QueryExecutor,
    SQLDialect,
    TypeMapper,
)


@DatabaseRegistry.register(DatabaseType.POSTGRESQL)
class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter."""

    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.POSTGRES

    def _create_connection_provider(self) -> ConnectionProvider:
        return PostgreSQLConnectionProvider()

    def _create_metadata_provider(self) -> MetadataProvider:
        return PostgreSQLMetadataProvider(self._connection_provider)

    def _create_query_executor(self) -> QueryExecutor:
        return PostgreSQLQueryExecutor(self._connection_provider, self._type_mapper)

    def _create_type_mapper(self) -> TypeMapper:
        return PostgreSQLTypeMapper()
```

```python
# adapters/postgresql/types.py
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
            "bytea": bytes,
            "jsonb": dict,
            "json": dict,
        }
        return mapping.get(db_type.lower(), str)
```

### 4.7 适配器自动加载 (`adapters/__init__.py`)

```python
"""
Database adapters package.

This module automatically discovers and loads all adapter implementations
when the package is imported.
"""

import importlib
import pkgutil
from pathlib import Path

# Auto-discover and import all adapter subpackages
_package_dir = Path(__file__).parent

for _, module_name, is_pkg in pkgutil.iter_modules([str(_package_dir)]):
    if is_pkg and module_name not in ("base", "shared"):
        # Import the package to trigger registration
        importlib.import_module(f".{module_name}", package=__name__)

# Re-export the registry for convenience
from app.core.registry import DatabaseRegistry, detect_database_type

__all__ = ["DatabaseRegistry", "detect_database_type"]
```

### 4.8 更新后的业务服务层

```python
# services/database.py (重构后)
"""Database CRUD operations using the adapter layer."""

from datetime import datetime

from app.adapters import DatabaseRegistry, detect_database_type
from app.database import get_db
from app.models.database import (
    DatabaseMetadata,
    DatabaseResponse,
    DatabaseWithMetadata,
    TableMetadata,
)
from app.services.metadata_serializer import MetadataSerializer


class DatabaseService:
    """Service for managing database connections."""

    @staticmethod
    async def create_or_update_database(
        name: str, url: str, description: str = ""
    ) -> DatabaseWithMetadata:
        """Create or update a database connection and fetch metadata."""
        # Get adapter through registry
        adapter = DatabaseRegistry.get_adapter_from_url(url)

        # Test connection
        if not await adapter.test_connection():
            raise ConnectionError(f"Could not connect to database at {url}")

        # Fetch metadata
        metadata = await adapter.fetch_metadata(name)

        # Store in application database
        db = await get_db()
        try:
            now = datetime.now()
            now_iso = now.isoformat()

            await db.execute(
                """
                INSERT INTO databases (name, url, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    url = excluded.url,
                    description = excluded.description,
                    updated_at = excluded.updated_at
                """,
                (name, url, description, now_iso, now_iso),
            )

            # Cache metadata
            await db.execute("DELETE FROM metadata WHERE database_name = ?", (name,))
            for table in metadata.tables + metadata.views:
                await db.execute(
                    """
                    INSERT INTO metadata (
                        database_name, table_name, table_type, columns_json, fetched_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        table.table_name,
                        table.table_type,
                        MetadataSerializer.serialize_table(table),
                        table.fetched_at.isoformat(),
                    ),
                )

            await db.commit()

            return DatabaseWithMetadata(
                name=name,
                url=url,
                description=description,
                database_type=metadata.database_type,
                created_at=now,
                updated_at=now,
                metadata=metadata,
            )
        finally:
            await db.close()
```

### 4.9 添加新数据库的步骤（以 SQLite 为例）

添加 SQLite 支持只需要：

**1. 创建适配器目录 `adapters/sqlite/`**

```python
# adapters/sqlite/__init__.py
from app.adapters.sqlite.adapter import SQLiteAdapter
__all__ = ["SQLiteAdapter"]

# adapters/sqlite/adapter.py
from app.adapters.base import DatabaseAdapter
from app.core.registry import DatabaseRegistry
from app.core.types import DatabaseType, SQLDialect

@DatabaseRegistry.register(DatabaseType.SQLITE)
class SQLiteAdapter(DatabaseAdapter):
    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.SQLITE

    # ... 实现各个 Provider
```

**2. 更新类型枚举（唯一需要修改的现有文件）**

```python
# core/types.py - 仅添加枚举值
class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"  # 添加这一行

class SQLDialect(str, Enum):
    POSTGRES = "postgres"
    MYSQL = "mysql"
    SQLITE = "sqlite"  # 添加这一行
```

**无需修改任何工厂类、服务类或路由！**

---

## 五、总结

### 5.1 设计改进对照表

| 方面 | 当前设计 | 新设计 | 改进 |
|------|---------|--------|-----|
| **抽象层统一性** | 只有 Connection 有抽象基类 | 所有组件都有抽象接口 | 接口一致性 |
| **扩展方式** | 修改多个工厂类 | 装饰器注册 + 自动发现 | 符合 OCP |
| **代码重复** | 大量重复的验证和序列化逻辑 | 共享基类实现 | DRY 原则 |
| **依赖方向** | 高层依赖低层具体实现 | 依赖抽象接口 | 符合 DIP |
| **职责划分** | 混合职责 | 清晰分离 | 符合 SRP |
| **类型安全** | 返回 Any | Protocol + 明确类型 | 更好的 IDE 支持 |
| **错误处理** | 散乱的异常 | 统一异常体系 | 一致的错误响应 |

### 5.2 迁移建议

1. **第一阶段**: 创建核心抽象层 (`core/`)，不改变现有代码
2. **第二阶段**: 实现 PostgreSQL 适配器，验证设计
3. **第三阶段**: 迁移 MySQL 到新适配器
4. **第四阶段**: 更新 Service 层使用新的 Registry
5. **第五阶段**: 删除旧的工厂类和分散的服务

### 5.3 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 破坏现有功能 | 中 | 保持现有代码直到新适配器完全就绪 |
| 性能影响 | 低 | 适配器实例缓存，连接池复用 |
| 学习曲线 | 中 | 清晰的文档和示例代码 |
| 过度设计 | 低 | 保持实现简洁，只抽象必要的部分 |

这个设计方案在保持实用性的同时，充分遵循了 SOLID 原则，特别是开闭原则，使得未来添加新数据库支持变得非常简单。
