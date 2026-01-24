# PostgreSQL MCP Server 技术设计文档

## 1. 概述

### 1.1 文档目的

本文档详细描述 PostgreSQL MCP Server 的技术架构、模块设计、数据模型和实现细节，为开发提供完整的技术指导。

### 1.2 技术栈

| 组件 | 技术选型 | 版本要求 | 用途 |
|------|----------|----------|------|
| MCP 框架 | FastMCP | >=2.0.0 | MCP 服务器框架，简化 Tool 注册 |
| SQL 解析 | SQLGlot | >=20.0.0 | SQL 语法解析、安全校验 |
| LLM 调用 | OpenAI SDK | >=1.0.0 | 调用 Qwen/OpenAI 等模型 |
| 数据库驱动 | asyncpg | >=0.29.0 | PostgreSQL 异步连接 |
| 数据验证 | Pydantic | >=2.0.0 | 配置管理、数据模型 |
| 配置管理 | pydantic-settings | >=2.0.0 | 环境变量和配置文件解析 |
| YAML 解析 | PyYAML | >=6.0.0 | 配置文件解析 |

### 1.3 设计原则

- **单一职责**：每个模块只负责一个明确的功能
- **依赖注入**：通过构造函数注入依赖，便于测试
- **异步优先**：全面使用 async/await，提高并发性能
- **防御性编程**：所有外部输入都需验证，SQL 必须经过安全检查
- **配置外置**：所有可变配置通过环境变量或配置文件管理

---

## 2. 系统架构

### 2.1 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client                               │
│                  (Claude Desktop / Cursor)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ MCP Protocol (stdio/SSE)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastMCP Server                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Tool: query                            │  │
│  └───────────────────────────┬───────────────────────────────┘  │
│                              │                                  │
│  ┌───────────────────────────▼───────────────────────────────┐  │
│  │                   QueryService                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │  │
│  │  │ LLMService  │  │ SQLValidator│  │ DatabaseService │    │  │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘    │  │
│  └─────────┼────────────────┼──────────────────┼─────────────┘  │
│            │                │                  │                │
│  ┌─────────▼────────┐ ┌─────▼─────┐  ┌─────────▼─────────┐      │
│  │   OpenAI API     │ │  SQLGlot  │  │   SchemaCache     │      │
│  │ (Qwen/DashScope) │ │  Parser   │  │                   │      │
│  └──────────────────┘ └───────────┘  └─────────┬─────────┘      │
│                                                │                │
│                                      ┌─────────▼─────────┐      │
│                                      │ ConnectionPool    │      │
│                                      │   (asyncpg)       │      │
│                                      └─────────┬─────────┘      │
└────────────────────────────────────────────────┼────────────────┘
                                                 │
                                       ┌─────────▼─────────┐
                                       │   PostgreSQL DB   │
                                       └───────────────────┘
```

### 2.2 核心模块

| 模块 | 职责 | 关键类/函数 |
|------|------|-------------|
| `config` | 配置管理 | `Settings`, `DatabaseConfig` |
| `database` | 数据库连接和 Schema 缓存 | `DatabaseService`, `SchemaCache`, `ConnectionPool` |
| `llm` | LLM 调用封装 | `LLMService` |
| `validator` | SQL 安全校验 | `SQLValidator` |
| `query` | 核心查询编排 | `QueryService` |
| `models` | Pydantic 数据模型 | `QueryResult`, `SchemaInfo`, etc. |
| `server` | FastMCP 服务器入口 | `create_server`, `query` tool |

### 2.3 数据流

```
用户输入 (自然语言)
       │
       ▼
┌──────────────────┐
│  1. LLM 生成 SQL │ ◄─── Schema 上下文
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. SQL 安全校验  │ ◄─── SQLGlot AST 解析
└────────┬─────────┘
         │ (通过校验)
         ▼
┌──────────────────┐
│ 3. 执行 SQL 查询 │ ◄─── asyncpg 连接池
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. LLM 验证结果  │ ◄─── 用户意图 + SQL + 结果样本
└────────┬─────────┘
         │
         ▼
    返回结果 (JSON)
```

---

## 3. 项目结构

```
pg-mcp/
├── pyproject.toml              # 项目配置和依赖
├── README.md                   # 项目说明
├── config.example.yaml         # 配置文件示例
│
├── src/
│   └── pg_mcp/
│       ├── __init__.py
│       ├── __main__.py         # 入口点: python -m pg_mcp
│       ├── server.py           # FastMCP 服务器定义
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py     # Pydantic Settings 配置
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── schema.py       # Schema 相关模型
│       │   ├── query.py        # 查询请求/响应模型
│       │   └── errors.py       # 错误模型
│       │
│       ├── database/
│       │   ├── __init__.py
│       │   ├── connection.py   # 连接池管理
│       │   ├── schema_cache.py # Schema 缓存
│       │   └── service.py      # 数据库服务
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── client.py       # OpenAI 客户端封装
│       │   ├── prompts.py      # Prompt 模板
│       │   └── service.py      # LLM 服务
│       │
│       ├── validator/
│       │   ├── __init__.py
│       │   └── sql_validator.py # SQL 安全校验
│       │
│       └── query/
│           ├── __init__.py
│           └── service.py      # 查询编排服务
│
└── tests/
    ├── __init__.py
    ├── conftest.py             # pytest fixtures
    ├── test_config.py
    ├── test_validator.py
    ├── test_llm.py
    ├── test_database.py
    └── test_query.py
```

---

## 4. 配置管理

### 4.1 环境变量

```python
# src/pg_mcp/config/settings.py

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """LLM 相关配置"""
    
    model_config = SettingsConfigDict(env_prefix="LLM_")
    
    api_key: SecretStr = Field(..., description="LLM API 密钥")
    base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="LLM API 地址"
    )
    model: str = Field(default="qwen-plus", description="模型名称")
    temperature: float = Field(default=0.1, ge=0, le=2, description="生成温度")
    timeout: float = Field(default=30.0, description="请求超时(秒)")
    max_tokens: int = Field(default=2048, description="最大生成 token 数")


class QuerySettings(BaseSettings):
    """查询相关配置"""
    
    model_config = SettingsConfigDict(env_prefix="QUERY_")
    
    default_limit: int = Field(default=100, ge=1, le=10000, description="默认返回行数限制")
    statement_timeout: int = Field(default=30000, ge=1000, description="SQL 执行超时(毫秒)")
    enable_validation: bool = Field(default=True, description="是否启用 LLM 结果验证")


class Settings(BaseSettings):
    """主配置类"""
    
    model_config = SettingsConfigDict(
        env_prefix="PG_MCP_",
        env_nested_delimiter="__",
    )
    
    config_path: str | None = Field(default=None, description="配置文件路径")
    log_level: str = Field(default="INFO", description="日志级别")
    
    llm: LLMSettings = Field(default_factory=LLMSettings)
    query: QuerySettings = Field(default_factory=QuerySettings)
```

### 4.2 数据库配置文件 (YAML)

```python
# src/pg_mcp/config/settings.py (续)

from pathlib import Path
from typing import Annotated
import yaml


class DatabaseConfig(BaseSettings):
    """单个数据库连接配置"""
    
    name: str = Field(..., description="数据库别名")
    host: str = Field(default="localhost", description="主机地址")
    port: int = Field(default=5432, ge=1, le=65535, description="端口")
    database: str = Field(..., description="数据库名")
    user: str = Field(..., description="用户名")
    password: SecretStr = Field(..., description="密码")
    
    # 连接池配置
    min_pool_size: int = Field(default=2, ge=1, description="最小连接数")
    max_pool_size: int = Field(default=10, ge=1, description="最大连接数")
    
    # SSL 配置
    ssl: bool = Field(default=False, description="是否启用 SSL")
    
    @property
    def dsn(self) -> str:
        """构建 PostgreSQL DSN"""
        return (
            f"postgresql://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.database}"
        )


class ConfigLoader:
    """配置文件加载器"""
    
    @staticmethod
    def load_databases(config_path: str | Path) -> list[DatabaseConfig]:
        """从 YAML 文件加载数据库配置"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        databases = data.get("databases", [])
        if not databases:
            raise ValueError("配置文件中未找到数据库配置")
        
        return [
            DatabaseConfig(**ConfigLoader._expand_env_vars(db))
            for db in databases
        ]
    
    @staticmethod
    def _expand_env_vars(config: dict) -> dict:
        """展开配置中的环境变量引用 ${VAR_NAME}"""
        import os
        import re
        
        result = {}
        pattern = re.compile(r'\$\{(\w+)\}')
        
        for key, value in config.items():
            if isinstance(value, str):
                def replacer(match):
                    var_name = match.group(1)
                    return os.environ.get(var_name, match.group(0))
                result[key] = pattern.sub(replacer, value)
            else:
                result[key] = value
        
        return result
```

### 4.3 配置文件示例

```yaml
# config.example.yaml

databases:
  - name: "default"
    host: "localhost"
    port: 5432
    database: "myapp"
    user: "readonly_user"
    password: "${PG_PASSWORD}"
    min_pool_size: 2
    max_pool_size: 10
    ssl: false
```

---

## 5. 数据模型 (Pydantic)

### 5.1 Schema 模型

```python
# src/pg_mcp/models/schema.py

from pydantic import BaseModel, Field
from enum import Enum


class ColumnInfo(BaseModel):
    """列信息"""
    name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    is_foreign_key: bool = False
    default_value: str | None = None
    comment: str | None = None
    
    # 外键信息
    foreign_table: str | None = None
    foreign_column: str | None = None


class IndexInfo(BaseModel):
    """索引信息"""
    name: str
    columns: list[str]
    is_unique: bool = False
    is_primary: bool = False
    index_type: str = "btree"  # btree, hash, gin, gist, etc.


class ConstraintType(str, Enum):
    PRIMARY_KEY = "PRIMARY KEY"
    FOREIGN_KEY = "FOREIGN KEY"
    UNIQUE = "UNIQUE"
    CHECK = "CHECK"


class ConstraintInfo(BaseModel):
    """约束信息"""
    name: str
    constraint_type: ConstraintType
    columns: list[str]
    
    # 外键特有
    foreign_table: str | None = None
    foreign_columns: list[str] | None = None


class TableInfo(BaseModel):
    """表信息"""
    schema_name: str = "public"
    name: str
    columns: list[ColumnInfo]
    indexes: list[IndexInfo] = Field(default_factory=list)
    constraints: list[ConstraintInfo] = Field(default_factory=list)
    comment: str | None = None
    estimated_row_count: int | None = None


class ViewInfo(BaseModel):
    """视图信息"""
    schema_name: str = "public"
    name: str
    columns: list[ColumnInfo]
    definition: str | None = None
    comment: str | None = None


class EnumTypeInfo(BaseModel):
    """枚举类型信息"""
    schema_name: str = "public"
    name: str
    values: list[str]


class ForeignKeyRelation(BaseModel):
    """外键关系（用于生成关系图）"""
    from_table: str
    from_columns: list[str]
    to_table: str
    to_columns: list[str]
    constraint_name: str


class DatabaseSchema(BaseModel):
    """完整的数据库 Schema 信息"""
    database_name: str
    tables: list[TableInfo] = Field(default_factory=list)
    views: list[ViewInfo] = Field(default_factory=list)
    enum_types: list[EnumTypeInfo] = Field(default_factory=list)
    foreign_key_relations: list[ForeignKeyRelation] = Field(default_factory=list)
    
    def to_llm_context(self) -> str:
        """将 Schema 转换为 LLM 可理解的文本格式"""
        lines = [f"# Database: {self.database_name}\n"]
        
        # 表信息
        if self.tables:
            lines.append("## Tables\n")
            for table in self.tables:
                lines.append(f"### {table.schema_name}.{table.name}")
                if table.comment:
                    lines.append(f"  -- {table.comment}")
                lines.append("")
                
                for col in table.columns:
                    pk = " [PK]" if col.is_primary_key else ""
                    fk = f" -> {col.foreign_table}.{col.foreign_column}" if col.is_foreign_key else ""
                    nullable = " NOT NULL" if not col.is_nullable else ""
                    comment = f"  -- {col.comment}" if col.comment else ""
                    lines.append(f"  - {col.name}: {col.data_type}{pk}{fk}{nullable}{comment}")
                lines.append("")
        
        # 视图信息
        if self.views:
            lines.append("## Views\n")
            for view in self.views:
                lines.append(f"### {view.schema_name}.{view.name}")
                for col in view.columns:
                    lines.append(f"  - {col.name}: {col.data_type}")
                lines.append("")
        
        # 外键关系
        if self.foreign_key_relations:
            lines.append("## Relationships\n")
            for rel in self.foreign_key_relations:
                from_cols = ", ".join(rel.from_columns)
                to_cols = ", ".join(rel.to_columns)
                lines.append(f"  - {rel.from_table}({from_cols}) -> {rel.to_table}({to_cols})")
            lines.append("")
        
        # 枚举类型
        if self.enum_types:
            lines.append("## Enum Types\n")
            for enum in self.enum_types:
                values = ", ".join(f"'{v}'" for v in enum.values)
                lines.append(f"  - {enum.name}: [{values}]")
            lines.append("")
        
        return "\n".join(lines)
```

### 5.2 查询模型

```python
# src/pg_mcp/models/query.py

from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., min_length=1, max_length=4096, description="自然语言查询")


class QueryResultData(BaseModel):
    """查询结果数据"""
    columns: list[str] = Field(description="列名列表")
    rows: list[list[Any]] = Field(description="行数据")
    row_count: int = Field(description="返回行数")
    execution_time_ms: float = Field(description="执行耗时(毫秒)")


class ValidationResult(BaseModel):
    """LLM 验证结果"""
    passed: bool = Field(description="验证是否通过")
    message: str = Field(description="验证说明")


class QueryResponse(BaseModel):
    """查询响应"""
    success: bool = Field(description="是否成功")
    sql: str | None = Field(default=None, description="生成的 SQL")
    result: QueryResultData | None = Field(default=None, description="查询结果")
    validation: ValidationResult | None = Field(default=None, description="验证结果")
    error: str | None = Field(default=None, description="错误信息")
    
    # 元信息
    generated_at: datetime = Field(default_factory=datetime.now)
```

### 5.3 错误模型

```python
# src/pg_mcp/models/errors.py

from enum import Enum


class ErrorCode(str, Enum):
    """错误代码"""
    SQL_GENERATION_FAILED = "SQL_GENERATION_FAILED"
    SQL_VALIDATION_FAILED = "SQL_VALIDATION_FAILED"
    SQL_UNSAFE = "SQL_UNSAFE"
    SQL_EXECUTION_FAILED = "SQL_EXECUTION_FAILED"
    SQL_TIMEOUT = "SQL_TIMEOUT"
    RESULT_VALIDATION_FAILED = "RESULT_VALIDATION_FAILED"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"
    SCHEMA_NOT_FOUND = "SCHEMA_NOT_FOUND"
    LLM_API_ERROR = "LLM_API_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class QueryError(Exception):
    """查询错误基类"""
    
    def __init__(self, code: ErrorCode, message: str, details: str | None = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class SQLGenerationError(QueryError):
    """SQL 生成失败"""
    def __init__(self, message: str, details: str | None = None):
        super().__init__(ErrorCode.SQL_GENERATION_FAILED, message, details)


class SQLUnsafeError(QueryError):
    """SQL 安全校验失败"""
    def __init__(self, message: str, sql: str | None = None):
        super().__init__(ErrorCode.SQL_UNSAFE, message, sql)


class SQLExecutionError(QueryError):
    """SQL 执行失败"""
    def __init__(self, message: str, sql: str | None = None):
        super().__init__(ErrorCode.SQL_EXECUTION_FAILED, message, sql)


class SQLTimeoutError(QueryError):
    """SQL 执行超时"""
    def __init__(self, timeout_ms: int):
        super().__init__(
            ErrorCode.SQL_TIMEOUT, 
            f"查询执行超时 ({timeout_ms}ms)",
            f"建议优化查询或增加超时时间"
        )


class LLMError(QueryError):
    """LLM API 调用失败"""
    def __init__(self, message: str, details: str | None = None):
        super().__init__(ErrorCode.LLM_API_ERROR, message, details)
```

---

## 6. 数据库模块

### 6.1 连接池管理

```python
# src/pg_mcp/database/connection.py

import asyncpg
from asyncpg import Pool
from contextlib import asynccontextmanager
from typing import AsyncIterator

from ..config.settings import DatabaseConfig


class ConnectionPool:
    """asyncpg 连接池管理"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool: Pool | None = None
    
    async def initialize(self) -> None:
        """初始化连接池"""
        if self._pool is not None:
            return
        
        self._pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password.get_secret_value(),
            min_size=self.config.min_pool_size,
            max_size=self.config.max_pool_size,
            ssl=self.config.ssl if self.config.ssl else None,
            command_timeout=60,  # 连接级别超时
        )
    
    async def close(self) -> None:
        """关闭连接池"""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
    
    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        """获取数据库连接"""
        if self._pool is None:
            raise RuntimeError("连接池未初始化")
        
        async with self._pool.acquire() as conn:
            yield conn
    
    @property
    def is_initialized(self) -> bool:
        return self._pool is not None
```

### 6.2 Schema 缓存

```python
# src/pg_mcp/database/schema_cache.py

import asyncpg
from ..models.schema import (
    DatabaseSchema, TableInfo, ViewInfo, ColumnInfo,
    IndexInfo, ConstraintInfo, ConstraintType,
    EnumTypeInfo, ForeignKeyRelation
)


class SchemaCache:
    """数据库 Schema 缓存"""
    
    # 获取表和列信息的 SQL
    TABLES_QUERY = """
    SELECT 
        t.table_schema,
        t.table_name,
        obj_description(
            (quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass
        ) as table_comment,
        (SELECT reltuples::bigint FROM pg_class WHERE oid = 
            (quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass
        ) as estimated_rows
    FROM information_schema.tables t
    WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
      AND t.table_type = 'BASE TABLE'
    ORDER BY t.table_schema, t.table_name
    """
    
    COLUMNS_QUERY = """
    SELECT 
        c.table_schema,
        c.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable = 'YES' as is_nullable,
        c.column_default,
        col_description(
            (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass,
            c.ordinal_position
        ) as column_comment
    FROM information_schema.columns c
    WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY c.table_schema, c.table_name, c.ordinal_position
    """
    
    PRIMARY_KEYS_QUERY = """
    SELECT 
        kcu.table_schema,
        kcu.table_name,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
      AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    """
    
    FOREIGN_KEYS_QUERY = """
    SELECT
        kcu.table_schema as from_schema,
        kcu.table_name as from_table,
        kcu.column_name as from_column,
        ccu.table_schema as to_schema,
        ccu.table_name as to_table,
        ccu.column_name as to_column,
        tc.constraint_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
      AND tc.table_schema NOT IN ('pg_catalog', 'information_schema')
    """
    
    VIEWS_QUERY = """
    SELECT 
        v.table_schema,
        v.table_name,
        v.view_definition,
        obj_description(
            (quote_ident(v.table_schema) || '.' || quote_ident(v.table_name))::regclass
        ) as view_comment
    FROM information_schema.views v
    WHERE v.table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY v.table_schema, v.table_name
    """
    
    ENUMS_QUERY = """
    SELECT 
        n.nspname as schema_name,
        t.typname as type_name,
        array_agg(e.enumlabel ORDER BY e.enumsortorder) as enum_values
    FROM pg_type t
    JOIN pg_enum e ON t.oid = e.enumtypid
    JOIN pg_namespace n ON t.typnamespace = n.oid
    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    GROUP BY n.nspname, t.typname
    """
    
    INDEXES_QUERY = """
    SELECT
        schemaname as table_schema,
        tablename as table_name,
        indexname as index_name,
        indexdef
    FROM pg_indexes
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    """
    
    def __init__(self, database_name: str):
        self.database_name = database_name
        self._schema: DatabaseSchema | None = None
    
    async def refresh(self, conn: asyncpg.Connection) -> DatabaseSchema:
        """刷新 Schema 缓存"""
        
        # 并行获取所有元数据
        tables_data = await conn.fetch(self.TABLES_QUERY)
        columns_data = await conn.fetch(self.COLUMNS_QUERY)
        pk_data = await conn.fetch(self.PRIMARY_KEYS_QUERY)
        fk_data = await conn.fetch(self.FOREIGN_KEYS_QUERY)
        views_data = await conn.fetch(self.VIEWS_QUERY)
        enums_data = await conn.fetch(self.ENUMS_QUERY)
        indexes_data = await conn.fetch(self.INDEXES_QUERY)
        
        # 构建主键集合
        pk_set = {
            (row['table_schema'], row['table_name'], row['column_name'])
            for row in pk_data
        }
        
        # 构建外键映射
        fk_map = {}
        for row in fk_data:
            key = (row['from_schema'], row['from_table'], row['from_column'])
            fk_map[key] = (row['to_table'], row['to_column'])
        
        # 构建列信息映射
        columns_map: dict[tuple[str, str], list[ColumnInfo]] = {}
        for row in columns_data:
            key = (row['table_schema'], row['table_name'])
            col_key = (row['table_schema'], row['table_name'], row['column_name'])
            
            fk_info = fk_map.get(col_key)
            
            col = ColumnInfo(
                name=row['column_name'],
                data_type=row['data_type'],
                is_nullable=row['is_nullable'],
                is_primary_key=col_key in pk_set,
                is_foreign_key=fk_info is not None,
                default_value=row['column_default'],
                comment=row['column_comment'],
                foreign_table=fk_info[0] if fk_info else None,
                foreign_column=fk_info[1] if fk_info else None,
            )
            columns_map.setdefault(key, []).append(col)
        
        # 构建表信息
        tables = []
        for row in tables_data:
            key = (row['table_schema'], row['table_name'])
            tables.append(TableInfo(
                schema_name=row['table_schema'],
                name=row['table_name'],
                columns=columns_map.get(key, []),
                comment=row['table_comment'],
                estimated_row_count=row['estimated_rows'],
            ))
        
        # 构建视图信息
        views = []
        for row in views_data:
            key = (row['table_schema'], row['table_name'])
            views.append(ViewInfo(
                schema_name=row['table_schema'],
                name=row['table_name'],
                columns=columns_map.get(key, []),
                definition=row['view_definition'],
                comment=row['view_comment'],
            ))
        
        # 构建枚举类型
        enum_types = [
            EnumTypeInfo(
                schema_name=row['schema_name'],
                name=row['type_name'],
                values=list(row['enum_values']),
            )
            for row in enums_data
        ]
        
        # 构建外键关系
        fk_relations_map: dict[str, ForeignKeyRelation] = {}
        for row in fk_data:
            constraint = row['constraint_name']
            if constraint not in fk_relations_map:
                fk_relations_map[constraint] = ForeignKeyRelation(
                    from_table=f"{row['from_schema']}.{row['from_table']}",
                    from_columns=[],
                    to_table=f"{row['to_schema']}.{row['to_table']}",
                    to_columns=[],
                    constraint_name=constraint,
                )
            fk_relations_map[constraint].from_columns.append(row['from_column'])
            fk_relations_map[constraint].to_columns.append(row['to_column'])
        
        self._schema = DatabaseSchema(
            database_name=self.database_name,
            tables=tables,
            views=views,
            enum_types=enum_types,
            foreign_key_relations=list(fk_relations_map.values()),
        )
        
        return self._schema
    
    @property
    def schema(self) -> DatabaseSchema | None:
        return self._schema
    
    def get_table_names(self) -> set[str]:
        """获取所有表名（用于 SQL 校验）"""
        if not self._schema:
            return set()
        return {
            f"{t.schema_name}.{t.name}" for t in self._schema.tables
        } | {t.name for t in self._schema.tables}
    
    def get_column_names(self, table: str) -> set[str]:
        """获取指定表的所有列名"""
        if not self._schema:
            return set()
        for t in self._schema.tables:
            if t.name == table or f"{t.schema_name}.{t.name}" == table:
                return {c.name for c in t.columns}
        return set()
```

### 6.3 数据库服务

```python
# src/pg_mcp/database/service.py

import asyncio
import time
from typing import Any

import asyncpg

from ..config.settings import DatabaseConfig, QuerySettings
from ..models.schema import DatabaseSchema
from ..models.query import QueryResultData
from ..models.errors import SQLExecutionError, SQLTimeoutError
from .connection import ConnectionPool
from .schema_cache import SchemaCache


class DatabaseService:
    """数据库服务 - 管理连接池、Schema 缓存和查询执行"""
    
    def __init__(
        self,
        config: DatabaseConfig,
        query_settings: QuerySettings,
    ):
        self.config = config
        self.query_settings = query_settings
        self._pool = ConnectionPool(config)
        self._schema_cache = SchemaCache(config.name)
    
    async def initialize(self) -> None:
        """初始化数据库服务"""
        await self._pool.initialize()
        await self.refresh_schema()
    
    async def close(self) -> None:
        """关闭数据库服务"""
        await self._pool.close()
    
    async def refresh_schema(self) -> DatabaseSchema:
        """刷新 Schema 缓存"""
        async with self._pool.acquire() as conn:
            return await self._schema_cache.refresh(conn)
    
    @property
    def schema(self) -> DatabaseSchema | None:
        """获取缓存的 Schema"""
        return self._schema_cache.schema
    
    def get_table_names(self) -> set[str]:
        """获取所有表名"""
        return self._schema_cache.get_table_names()
    
    async def execute_query(
        self,
        sql: str,
        limit: int | None = None,
    ) -> QueryResultData:
        """执行只读查询"""
        
        effective_limit = limit or self.query_settings.default_limit
        timeout_ms = self.query_settings.statement_timeout
        
        async with self._pool.acquire() as conn:
            try:
                # 设置语句超时
                await conn.execute(
                    f"SET statement_timeout = {timeout_ms}"
                )
                
                # 执行查询
                start_time = time.perf_counter()
                
                # 如果 SQL 没有 LIMIT，添加一个
                exec_sql = sql
                if "LIMIT" not in sql.upper():
                    exec_sql = f"{sql.rstrip(';')} LIMIT {effective_limit}"
                
                rows = await conn.fetch(exec_sql)
                
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000
                
                # 构建结果
                if rows:
                    columns = list(rows[0].keys())
                    data = [list(row.values()) for row in rows]
                else:
                    columns = []
                    data = []
                
                return QueryResultData(
                    columns=columns,
                    rows=self._serialize_rows(data),
                    row_count=len(data),
                    execution_time_ms=round(execution_time_ms, 2),
                )
                
            except asyncpg.QueryCanceledError:
                raise SQLTimeoutError(timeout_ms)
            except asyncpg.PostgresError as e:
                raise SQLExecutionError(str(e), sql)
    
    def _serialize_rows(self, rows: list[list[Any]]) -> list[list[Any]]:
        """序列化行数据（处理特殊类型）"""
        result = []
        for row in rows:
            serialized_row = []
            for value in row:
                if hasattr(value, 'isoformat'):  # datetime, date, time
                    serialized_row.append(value.isoformat())
                elif isinstance(value, bytes):
                    serialized_row.append(value.hex())
                else:
                    serialized_row.append(value)
            result.append(serialized_row)
        return result
```

---

## 7. LLM 模块

### 7.1 Prompt 模板

```python
# src/pg_mcp/llm/prompts.py

SQL_GENERATION_SYSTEM_PROMPT = """你是一个专业的 SQL 查询助手。你的任务是根据用户的自然语言描述，生成正确的 PostgreSQL SELECT 查询语句。

## 规则
1. 只生成 SELECT 查询语句，禁止生成任何修改数据的语句（INSERT/UPDATE/DELETE/DROP 等）
2. 必须基于提供的数据库 Schema 信息生成查询
3. 正确处理表之间的关联（JOIN）
4. 使用适当的聚合函数和 GROUP BY
5. 如果需要排序，使用 ORDER BY
6. 不要添加 LIMIT 子句（系统会自动处理）

## 输出格式
只输出 SQL 语句本身，不要包含任何解释、markdown 代码块标记或其他文本。
"""

SQL_GENERATION_USER_TEMPLATE = """## 数据库 Schema
{schema}

## 用户查询需求
{query}

请生成对应的 SQL 查询语句："""


RESULT_VALIDATION_SYSTEM_PROMPT = """你是一个数据分析验证助手。你的任务是验证 SQL 查询结果是否与用户的原始查询意图匹配。

## 验证内容
1. 查询结果是否回答了用户的问题
2. 结果数据是否合理（非异常值）
3. 如果结果为空，分析可能的原因

## 输出格式
请用以下 JSON 格式输出验证结果：
{
  "passed": true/false,
  "message": "验证说明（简洁的中文）"
}
"""

RESULT_VALIDATION_USER_TEMPLATE = """## 用户原始查询
{query}

## 执行的 SQL
{sql}

## 查询结果（前 {sample_size} 行）
列名: {columns}
数据:
{rows}

共返回 {total_rows} 行数据。

请验证此结果是否正确回答了用户的查询需求："""
```

### 7.2 LLM 客户端

```python
# src/pg_mcp/llm/client.py

from openai import AsyncOpenAI

from ..config.settings import LLMSettings


def create_llm_client(settings: LLMSettings) -> AsyncOpenAI:
    """创建 OpenAI 兼容客户端"""
    return AsyncOpenAI(
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url,
        timeout=settings.timeout,
    )
```

### 7.3 LLM 服务

```python
# src/pg_mcp/llm/service.py

import json
import re
from openai import AsyncOpenAI

from ..config.settings import LLMSettings
from ..models.schema import DatabaseSchema
from ..models.query import QueryResultData, ValidationResult
from ..models.errors import SQLGenerationError, LLMError
from .prompts import (
    SQL_GENERATION_SYSTEM_PROMPT,
    SQL_GENERATION_USER_TEMPLATE,
    RESULT_VALIDATION_SYSTEM_PROMPT,
    RESULT_VALIDATION_USER_TEMPLATE,
)
from .client import create_llm_client


class LLMService:
    """LLM 服务 - SQL 生成和结果验证"""
    
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self._client = create_llm_client(settings)
    
    async def generate_sql(
        self,
        query: str,
        schema: DatabaseSchema,
    ) -> str:
        """根据自然语言生成 SQL"""
        
        user_prompt = SQL_GENERATION_USER_TEMPLATE.format(
            schema=schema.to_llm_context(),
            query=query,
        )
        
        try:
            response = await self._client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {"role": "system", "content": SQL_GENERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
            )
            
            sql = response.choices[0].message.content
            if not sql:
                raise SQLGenerationError("LLM 返回空响应")
            
            # 清理 SQL（移除可能的 markdown 代码块标记）
            sql = self._clean_sql(sql)
            
            return sql
            
        except Exception as e:
            if isinstance(e, SQLGenerationError):
                raise
            raise LLMError(f"SQL 生成失败: {str(e)}")
    
    async def validate_result(
        self,
        query: str,
        sql: str,
        result: QueryResultData,
        sample_size: int = 5,
    ) -> ValidationResult:
        """验证查询结果是否有意义"""
        
        # 取样本数据
        sample_rows = result.rows[:sample_size]
        rows_text = "\n".join(
            str(row) for row in sample_rows
        )
        
        user_prompt = RESULT_VALIDATION_USER_TEMPLATE.format(
            query=query,
            sql=sql,
            columns=result.columns,
            rows=rows_text,
            sample_size=min(sample_size, result.row_count),
            total_rows=result.row_count,
        )
        
        try:
            response = await self._client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {"role": "system", "content": RESULT_VALIDATION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,  # 验证需要更确定的输出
                max_tokens=256,
            )
            
            content = response.choices[0].message.content
            if not content:
                return ValidationResult(passed=True, message="验证服务无响应，默认通过")
            
            # 解析 JSON 响应
            validation_data = self._parse_validation_response(content)
            return ValidationResult(**validation_data)
            
        except Exception as e:
            # 验证失败不应阻止返回结果
            return ValidationResult(
                passed=True,
                message=f"验证过程出现问题，默认通过: {str(e)}"
            )
    
    def _clean_sql(self, sql: str) -> str:
        """清理 SQL 字符串"""
        sql = sql.strip()
        
        # 移除 markdown 代码块标记
        if sql.startswith("```"):
            lines = sql.split("\n")
            # 移除首行 ```sql 或 ```
            if lines[0].startswith("```"):
                lines = lines[1:]
            # 移除末行 ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            sql = "\n".join(lines)
        
        return sql.strip()
    
    def _parse_validation_response(self, content: str) -> dict:
        """解析验证响应的 JSON"""
        # 尝试提取 JSON
        json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # 如果无法解析，返回默认值
        return {"passed": True, "message": content[:200]}
```

---

## 8. SQL 安全校验模块

### 8.1 SQL 校验器

```python
# src/pg_mcp/validator/sql_validator.py

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

from ..models.errors import SQLUnsafeError


class SQLValidator:
    """SQL 安全校验器 - 使用 SQLGlot 进行 AST 分析"""
    
    # 允许的语句类型（只允许 SELECT）
    ALLOWED_STATEMENT_TYPES = (exp.Select,)
    
    # 危险的表达式类型
    DANGEROUS_EXPRESSION_TYPES = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Create,
        exp.Alter,
        exp.Truncate,
        exp.Grant,
        exp.Merge,
        exp.Command,  # 包括 COPY, EXECUTE 等
    )
    
    # 危险的函数名
    DANGEROUS_FUNCTIONS = {
        'pg_read_file',
        'pg_read_binary_file',
        'pg_ls_dir',
        'lo_import',
        'lo_export',
        'dblink',
        'dblink_exec',
    }
    
    def __init__(self, known_tables: set[str] | None = None):
        """
        Args:
            known_tables: 已知的表名集合，用于额外的校验
        """
        self.known_tables = known_tables or set()
    
    def validate(self, sql: str) -> str:
        """
        验证 SQL 语句安全性
        
        Args:
            sql: 待验证的 SQL 语句
            
        Returns:
            验证通过的 SQL 语句
            
        Raises:
            SQLUnsafeError: 如果 SQL 不安全
        """
        
        # 1. 解析 SQL
        try:
            statements = sqlglot.parse(sql, dialect="postgres")
        except ParseError as e:
            raise SQLUnsafeError(f"SQL 语法错误: {str(e)}", sql)
        
        # 2. 检查语句数量（只允许单条语句）
        if len(statements) == 0:
            raise SQLUnsafeError("空的 SQL 语句", sql)
        
        if len(statements) > 1:
            raise SQLUnsafeError(
                "不允许执行多条 SQL 语句，请只提供一条 SELECT 查询",
                sql
            )
        
        statement = statements[0]
        
        # 3. 检查语句类型
        if not isinstance(statement, self.ALLOWED_STATEMENT_TYPES):
            stmt_type = type(statement).__name__
            raise SQLUnsafeError(
                f"不允许的 SQL 语句类型: {stmt_type}，只允许 SELECT 查询",
                sql
            )
        
        # 4. 检查是否包含子查询中的危险操作
        self._check_dangerous_expressions(statement, sql)
        
        # 5. 检查危险函数调用
        self._check_dangerous_functions(statement, sql)
        
        # 6. 可选：检查表名是否存在于 Schema 中
        if self.known_tables:
            self._check_table_references(statement, sql)
        
        return sql
    
    def _check_dangerous_expressions(
        self,
        statement: exp.Expression,
        sql: str
    ) -> None:
        """检查是否包含危险的表达式"""
        
        for node in statement.walk():
            if isinstance(node, self.DANGEROUS_EXPRESSION_TYPES):
                node_type = type(node).__name__
                raise SQLUnsafeError(
                    f"SQL 包含不允许的操作: {node_type}",
                    sql
                )
    
    def _check_dangerous_functions(
        self,
        statement: exp.Expression,
        sql: str
    ) -> None:
        """检查是否调用了危险函数"""
        
        for node in statement.walk():
            if isinstance(node, exp.Func):
                func_name = node.name.lower() if hasattr(node, 'name') else ""
                if func_name in self.DANGEROUS_FUNCTIONS:
                    raise SQLUnsafeError(
                        f"SQL 包含不允许的函数调用: {func_name}",
                        sql
                    )
    
    def _check_table_references(
        self,
        statement: exp.Expression,
        sql: str
    ) -> None:
        """检查引用的表是否存在"""
        
        for table in statement.find_all(exp.Table):
            table_name = table.name
            schema_name = table.db if hasattr(table, 'db') else None
            
            # 构建完整表名
            full_name = f"{schema_name}.{table_name}" if schema_name else table_name
            
            # 检查表是否存在
            if table_name not in self.known_tables and full_name not in self.known_tables:
                raise SQLUnsafeError(
                    f"引用了未知的表: {full_name}",
                    sql
                )
    
    @staticmethod
    def is_select_only(sql: str) -> bool:
        """快速检查是否只是 SELECT 语句（不抛异常）"""
        try:
            statements = sqlglot.parse(sql, dialect="postgres")
            return (
                len(statements) == 1 
                and isinstance(statements[0], exp.Select)
            )
        except Exception:
            return False
```

---

## 9. 查询编排服务

```python
# src/pg_mcp/query/service.py

import logging

from ..config.settings import Settings, QuerySettings
from ..database.service import DatabaseService
from ..llm.service import LLMService
from ..validator.sql_validator import SQLValidator
from ..models.query import QueryRequest, QueryResponse, QueryResultData, ValidationResult
from ..models.errors import QueryError, SQLUnsafeError


logger = logging.getLogger(__name__)


class QueryService:
    """查询编排服务 - 协调 LLM、校验器和数据库服务"""
    
    def __init__(
        self,
        database_service: DatabaseService,
        llm_service: LLMService,
        query_settings: QuerySettings,
    ):
        self.database = database_service
        self.llm = llm_service
        self.query_settings = query_settings
    
    async def execute(self, request: QueryRequest) -> QueryResponse:
        """
        执行完整的查询流程
        
        流程:
        1. LLM 生成 SQL
        2. SQL 安全校验
        3. 执行 SQL 查询
        4. LLM 验证结果（可选）
        """
        
        sql: str | None = None
        result: QueryResultData | None = None
        validation: ValidationResult | None = None
        
        try:
            # 1. 获取 Schema
            schema = self.database.schema
            if not schema:
                raise QueryError(
                    code="SCHEMA_NOT_FOUND",
                    message="数据库 Schema 未加载"
                )
            
            logger.info(f"处理查询: {request.query[:100]}...")
            
            # 2. LLM 生成 SQL
            sql = await self.llm.generate_sql(
                query=request.query,
                schema=schema,
            )
            logger.debug(f"生成的 SQL: {sql}")
            
            # 3. SQL 安全校验
            validator = SQLValidator(
                known_tables=self.database.get_table_names()
            )
            sql = validator.validate(sql)
            
            # 4. 执行 SQL 查询
            result = await self.database.execute_query(sql)
            logger.info(f"查询返回 {result.row_count} 行，耗时 {result.execution_time_ms}ms")
            
            # 5. LLM 验证结果（可选）
            if self.query_settings.enable_validation:
                validation = await self.llm.validate_result(
                    query=request.query,
                    sql=sql,
                    result=result,
                )
                logger.debug(f"结果验证: {validation.passed} - {validation.message}")
            else:
                validation = ValidationResult(passed=True, message="验证已禁用")
            
            return QueryResponse(
                success=True,
                sql=sql,
                result=result,
                validation=validation,
            )
            
        except QueryError as e:
            logger.warning(f"查询失败: {e.code} - {e.message}")
            return QueryResponse(
                success=False,
                sql=sql,
                error=f"[{e.code}] {e.message}",
            )
        except Exception as e:
            logger.exception(f"未知错误: {str(e)}")
            return QueryResponse(
                success=False,
                sql=sql,
                error=f"[INTERNAL_ERROR] {str(e)}",
            )
```

---

## 10. FastMCP 服务器

### 10.1 服务器定义

```python
# src/pg_mcp/server.py

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from .config.settings import Settings, ConfigLoader
from .database.service import DatabaseService
from .llm.service import LLMService
from .query.service import QueryService
from .models.query import QueryRequest


logger = logging.getLogger(__name__)


# 全局服务实例（在 lifespan 中初始化）
_query_service: QueryService | None = None


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[None]:
    """服务器生命周期管理"""
    global _query_service
    
    logger.info("PostgreSQL MCP Server 启动中...")
    
    # 加载配置
    settings = Settings()
    
    # 加载数据库配置
    if not settings.config_path:
        raise ValueError("必须设置 PG_MCP_CONFIG_PATH 环境变量指向配置文件")
    
    db_configs = ConfigLoader.load_databases(settings.config_path)
    if not db_configs:
        raise ValueError("配置文件中未找到数据库配置")
    
    # 使用第一个数据库配置（简化版本，后续可扩展为多数据库）
    db_config = db_configs[0]
    
    # 初始化服务
    db_service = DatabaseService(db_config, settings.query)
    llm_service = LLMService(settings.llm)
    
    await db_service.initialize()
    logger.info(f"已连接数据库: {db_config.name}")
    
    schema = db_service.schema
    if schema:
        logger.info(
            f"已缓存 Schema: {len(schema.tables)} 个表, "
            f"{len(schema.views)} 个视图"
        )
    
    _query_service = QueryService(
        database_service=db_service,
        llm_service=llm_service,
        query_settings=settings.query,
    )
    
    logger.info("PostgreSQL MCP Server 已就绪")
    
    try:
        yield
    finally:
        await db_service.close()
        logger.info("PostgreSQL MCP Server 已关闭")


# 创建 FastMCP 服务器
mcp = FastMCP(
    "PostgreSQL MCP Server",
    lifespan=lifespan,
)


@mcp.tool()
async def query(query: str) -> str:
    """
    根据自然语言描述查询数据库
    
    Args:
        query: 自然语言查询描述，例如 "查询最近一个月注册的用户数量"
    
    Returns:
        包含 SQL 语句、查询结果和验证信息的 JSON 响应
    """
    global _query_service
    
    if _query_service is None:
        return '{"success": false, "error": "服务未初始化"}'
    
    request = QueryRequest(query=query)
    response = await _query_service.execute(request)
    
    return response.model_dump_json(indent=2)
```

### 10.2 入口点

```python
# src/pg_mcp/__main__.py

import logging
import sys

from .server import mcp
from .config.settings import Settings


def setup_logging():
    """配置日志"""
    settings = Settings()
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def main():
    """主入口"""
    setup_logging()
    mcp.run()


if __name__ == "__main__":
    main()
```

### 10.3 pyproject.toml

```toml
# pyproject.toml

[project]
name = "pg-mcp"
version = "0.1.0"
description = "PostgreSQL MCP Server - 自然语言查询数据库"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
    "asyncpg>=0.29.0",
    "openai>=1.0.0",
    "sqlglot>=20.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0.0",
]

[project.scripts]
pg-mcp = "pg_mcp.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/pg_mcp"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]
```

---

## 11. 错误处理策略

### 11.1 错误分类

| 错误类型 | 错误码 | 处理策略 | 用户提示 |
|----------|--------|----------|----------|
| SQL 生成失败 | SQL_GENERATION_FAILED | 返回错误，建议重试 | 请尝试更清晰地描述您的查询需求 |
| SQL 语法错误 | SQL_VALIDATION_FAILED | 返回错误，记录日志 | 生成的 SQL 存在语法问题 |
| SQL 安全拒绝 | SQL_UNSAFE | 返回错误，记录安全日志 | 该查询包含不允许的操作 |
| SQL 执行错误 | SQL_EXECUTION_FAILED | 返回数据库错误信息 | 查询执行失败：{db_error} |
| SQL 超时 | SQL_TIMEOUT | 返回超时提示 | 查询执行超时，请尝试简化查询 |
| 结果验证失败 | RESULT_VALIDATION_FAILED | 返回但标记验证失败 | 结果可能不符合预期 |
| LLM API 错误 | LLM_API_ERROR | 重试或返回错误 | AI 服务暂时不可用 |
| 数据库连接失败 | DATABASE_CONNECTION_FAILED | 尝试重连 | 数据库连接失败 |

### 11.2 日志级别

| 场景 | 日志级别 | 记录内容 |
|------|----------|----------|
| 正常查询 | INFO | 查询摘要、执行时间、结果行数 |
| SQL 生成 | DEBUG | 完整 SQL 语句 |
| SQL 校验失败 | WARNING | 被拒绝的 SQL、拒绝原因 |
| 安全相关 | WARNING | 可疑操作、来源信息 |
| 系统错误 | ERROR | 完整异常堆栈 |
| 启动关闭 | INFO | 服务器状态变更 |

---

## 12. 测试策略

### 12.1 单元测试

```python
# tests/test_validator.py

import pytest
from pg_mcp.validator.sql_validator import SQLValidator
from pg_mcp.models.errors import SQLUnsafeError


class TestSQLValidator:
    
    def setup_method(self):
        self.validator = SQLValidator()
    
    def test_valid_select(self):
        sql = "SELECT * FROM users WHERE id = 1"
        result = self.validator.validate(sql)
        assert result == sql
    
    def test_reject_insert(self):
        sql = "INSERT INTO users (name) VALUES ('test')"
        with pytest.raises(SQLUnsafeError) as exc:
            self.validator.validate(sql)
        assert "INSERT" in str(exc.value) or "不允许" in str(exc.value)
    
    def test_reject_update(self):
        sql = "UPDATE users SET name = 'test' WHERE id = 1"
        with pytest.raises(SQLUnsafeError):
            self.validator.validate(sql)
    
    def test_reject_delete(self):
        sql = "DELETE FROM users WHERE id = 1"
        with pytest.raises(SQLUnsafeError):
            self.validator.validate(sql)
    
    def test_reject_drop(self):
        sql = "DROP TABLE users"
        with pytest.raises(SQLUnsafeError):
            self.validator.validate(sql)
    
    def test_reject_multiple_statements(self):
        sql = "SELECT 1; DROP TABLE users"
        with pytest.raises(SQLUnsafeError) as exc:
            self.validator.validate(sql)
        assert "多条" in str(exc.value)
    
    def test_valid_complex_select(self):
        sql = """
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.created_at > '2024-01-01'
        GROUP BY u.id, u.name
        ORDER BY order_count DESC
        """
        result = self.validator.validate(sql)
        assert "SELECT" in result
    
    def test_reject_dangerous_function(self):
        sql = "SELECT pg_read_file('/etc/passwd')"
        with pytest.raises(SQLUnsafeError):
            self.validator.validate(sql)
    
    def test_table_validation(self):
        validator = SQLValidator(known_tables={"users", "orders"})
        
        # 有效的表
        validator.validate("SELECT * FROM users")
        
        # 未知的表
        with pytest.raises(SQLUnsafeError) as exc:
            validator.validate("SELECT * FROM unknown_table")
        assert "未知" in str(exc.value)
```

### 12.2 集成测试

```python
# tests/test_query.py

import pytest
from unittest.mock import AsyncMock, MagicMock

from pg_mcp.query.service import QueryService
from pg_mcp.models.query import QueryRequest, QueryResultData, ValidationResult


@pytest.fixture
def mock_database_service():
    service = MagicMock()
    service.schema = MagicMock()
    service.schema.to_llm_context.return_value = "Table: users (id, name, email)"
    service.get_table_names.return_value = {"users"}
    service.execute_query = AsyncMock(return_value=QueryResultData(
        columns=["id", "name"],
        rows=[[1, "Alice"], [2, "Bob"]],
        row_count=2,
        execution_time_ms=10.5,
    ))
    return service


@pytest.fixture
def mock_llm_service():
    service = MagicMock()
    service.generate_sql = AsyncMock(return_value="SELECT id, name FROM users")
    service.validate_result = AsyncMock(return_value=ValidationResult(
        passed=True,
        message="结果正确"
    ))
    return service


@pytest.fixture
def query_service(mock_database_service, mock_llm_service):
    from pg_mcp.config.settings import QuerySettings
    return QueryService(
        database_service=mock_database_service,
        llm_service=mock_llm_service,
        query_settings=QuerySettings(),
    )


@pytest.mark.asyncio
async def test_successful_query(query_service):
    request = QueryRequest(query="查询所有用户")
    response = await query_service.execute(request)
    
    assert response.success is True
    assert response.sql == "SELECT id, name FROM users"
    assert response.result.row_count == 2
    assert response.validation.passed is True
```

---

## 13. 部署配置

### 13.1 Claude Desktop 配置

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
// %APPDATA%\Claude\claude_desktop_config.json (Windows)

{
  "mcpServers": {
    "pg-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/pg-mcp", "pg-mcp"],
      "env": {
        "LLM_API_KEY": "your-api-key",
        "PG_MCP_CONFIG_PATH": "/path/to/config.yaml",
        "PG_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 13.2 环境变量配置示例

```bash
# .env.example

# LLM 配置
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
LLM_TEMPERATURE=0.1

# 查询配置
QUERY_DEFAULT_LIMIT=100
QUERY_STATEMENT_TIMEOUT=30000
QUERY_ENABLE_VALIDATION=true

# MCP 服务器配置
PG_MCP_CONFIG_PATH=./config.yaml
PG_MCP_LOG_LEVEL=INFO

# 数据库密码（在 config.yaml 中引用）
PG_PASSWORD=your-db-password
```

---

## 14. 修订历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-01-24 | 初始版本 |
