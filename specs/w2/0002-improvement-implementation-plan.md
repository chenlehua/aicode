# 数据库适配器重构实现计划

> 基于 [0001-improvement.md](./0001-improvement.md) 设计方案的详细实现计划

## 一、实现概述

### 1.1 目标

将现有的数据库服务层重构为基于适配器模式的插件式架构，实现：
- 统一的抽象接口
- 自动注册机制
- 零修改扩展新数据库

### 1.2 当前文件清单

```
backend/app/
├── main.py
├── config.py
├── database.py
├── models/
│   ├── __init__.py
│   ├── database.py
│   ├── query.py
│   ├── history.py
│   └── error.py
├── services/
│   ├── __init__.py
│   ├── connection_base.py      # 保留参考，最终删除
│   ├── connection.py           # PostgreSQL，迁移后删除
│   ├── connection_mysql.py     # MySQL，迁移后删除
│   ├── connection_factory.py   # 迁移后删除
│   ├── metadata.py             # PostgreSQL，迁移后删除
│   ├── metadata_mysql.py       # MySQL，迁移后删除
│   ├── metadata_factory.py     # 迁移后删除
│   ├── query.py                # PostgreSQL，迁移后删除
│   ├── query_mysql.py          # MySQL，迁移后删除
│   ├── query_factory.py        # 迁移后删除
│   ├── database.py             # 需要更新
│   ├── history.py              # 保持不变
│   └── llm.py                  # 需要更新
└── routers/
    ├── __init__.py
    └── databases.py            # 可能需要微调
```

### 1.3 实现阶段划分

| 阶段 | 名称 | 主要任务 | 风险等级 |
|------|------|---------|---------|
| 1 | 基础设施搭建 | 创建 core/ 和 adapters/ 骨架 | 低 |
| 2 | PostgreSQL 适配器 | 实现第一个完整适配器 | 中 |
| 3 | MySQL 适配器 | 迁移 MySQL 实现 | 中 |
| 4 | 服务层集成 | 更新 Service 使用新架构 | 高 |
| 5 | 清理与优化 | 删除旧代码，完善测试 | 低 |

---

## 二、第一阶段：基础设施搭建

### 2.1 任务清单

| 任务ID | 任务描述 | 新建/修改 | 依赖 |
|--------|---------|----------|------|
| 1.1 | 创建 `app/core/__init__.py` | 新建 | 无 |
| 1.2 | 创建 `app/core/types.py` - 类型定义 | 新建 | 无 |
| 1.3 | 创建 `app/core/exceptions.py` - 异常体系 | 新建 | 无 |
| 1.4 | 创建 `app/core/registry.py` - 注册表 | 新建 | 1.2, 1.3 |
| 1.5 | 创建 `app/adapters/__init__.py` - 自动加载 | 新建 | 1.4 |
| 1.6 | 创建 `app/adapters/base.py` - 抽象基类 | 新建 | 1.2 |
| 1.7 | 创建 `app/adapters/shared/__init__.py` | 新建 | 无 |
| 1.8 | 创建 `app/adapters/shared/query_base.py` | 新建 | 1.2 |
| 1.9 | 创建 `app/adapters/shared/type_mapper_base.py` | 新建 | 1.2 |

### 2.2 详细实现步骤

#### 任务 1.1: 创建 `app/core/__init__.py`

```python
"""Core module for database adapter infrastructure."""

from app.core.exceptions import (
    AuthenticationError,
    ConnectionError,
    DatabaseError,
    QueryExecutionError,
    QueryValidationError,
    UnsupportedDatabaseError,
)
from app.core.registry import DatabaseRegistry, detect_database_type
from app.core.types import (
    ConnectionProvider,
    DatabaseConfig,
    DatabaseType,
    MetadataProvider,
    QueryExecutor,
    SQLDialect,
    TypeMapper,
)

__all__ = [
    # Types
    "DatabaseType",
    "DatabaseConfig",
    "SQLDialect",
    "ConnectionProvider",
    "MetadataProvider",
    "QueryExecutor",
    "TypeMapper",
    # Registry
    "DatabaseRegistry",
    "detect_database_type",
    # Exceptions
    "DatabaseError",
    "ConnectionError",
    "AuthenticationError",
    "QueryValidationError",
    "QueryExecutionError",
    "UnsupportedDatabaseError",
]
```

#### 任务 1.2: 创建 `app/core/types.py`

**关键实现点：**
- `DatabaseType` 枚举：支持 postgresql, mysql（预留 sqlite）
- `DatabaseConfig` 数据类：包含 URL 解析逻辑
- `SQLDialect` 枚举：用于 sqlglot 解析
- 四个抽象接口：`ConnectionProvider`, `MetadataProvider`, `QueryExecutor`, `TypeMapper`

**URL 解析实现：**
```python
@classmethod
def from_url(cls, url: str) -> "DatabaseConfig":
    """Parse database URL into config object."""
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    # 检测数据库类型
    if scheme in ("postgresql", "postgres"):
        db_type = DatabaseType.POSTGRESQL
    elif scheme in ("mysql", "mysql+aiomysql"):
        db_type = DatabaseType.MYSQL
    else:
        raise ValueError(f"Unsupported database scheme: {scheme}")

    return cls(
        url=url,
        db_type=db_type,
        host=parsed.hostname or "localhost",
        port=parsed.port or (5432 if db_type == DatabaseType.POSTGRESQL else 3306),
        database=parsed.path.lstrip("/"),
        username=parsed.username,
        password=parsed.password,
    )
```

#### 任务 1.3: 创建 `app/core/exceptions.py`

**异常层次结构：**
```
DatabaseError (基类)
├── ConnectionError
├── AuthenticationError
├── QueryValidationError
├── QueryExecutionError
└── UnsupportedDatabaseError
```

#### 任务 1.4: 创建 `app/core/registry.py`

**核心功能：**
- `@DatabaseRegistry.register(db_type)` 装饰器
- `get_adapter(config)` / `get_adapter_from_url(url)` 获取适配器
- `close_all()` 关闭所有连接池
- `detect_database_type(url)` URL 类型检测

#### 任务 1.5: 创建 `app/adapters/__init__.py`

**自动发现机制：**
```python
import importlib
import pkgutil
from pathlib import Path

_package_dir = Path(__file__).parent

for _, module_name, is_pkg in pkgutil.iter_modules([str(_package_dir)]):
    if is_pkg and module_name not in ("base", "shared"):
        importlib.import_module(f".{module_name}", package=__name__)
```

#### 任务 1.6: 创建 `app/adapters/base.py`

**DatabaseAdapter 抽象基类：**
- 组合四个 Provider
- 提供高层操作方法
- 使用工厂方法模式

#### 任务 1.7-1.9: 创建共享基础实现

**BaseQueryExecutor:**
- 通用 `validate_sql()` 实现（基于 sqlglot）
- 通用 `inject_limit()` 实现
- 子类只需实现 `execute()` 和 `dialect` 属性

**BaseTypeMapper:**
- 通用 `serialize_value()` 实现
- 子类只需覆盖 `TYPE_MAP` 和 `db_to_python_type()`

### 2.3 验证标准

- [ ] 所有新文件创建完成
- [ ] `from app.core import *` 无导入错误
- [ ] `from app.adapters import DatabaseRegistry` 无导入错误
- [ ] 类型检查通过 (`mypy app/core app/adapters/base.py`)

---

## 三、第二阶段：PostgreSQL 适配器实现

### 3.1 任务清单

| 任务ID | 任务描述 | 新建/修改 | 依赖 |
|--------|---------|----------|------|
| 2.1 | 创建 `app/adapters/postgresql/__init__.py` | 新建 | 1.* |
| 2.2 | 创建 `app/adapters/postgresql/connection.py` | 新建 | 1.* |
| 2.3 | 创建 `app/adapters/postgresql/metadata.py` | 新建 | 2.2 |
| 2.4 | 创建 `app/adapters/postgresql/query.py` | 新建 | 2.2 |
| 2.5 | 创建 `app/adapters/postgresql/types.py` | 新建 | 1.9 |
| 2.6 | 创建 `app/adapters/postgresql/adapter.py` | 新建 | 2.2-2.5 |
| 2.7 | 编写 PostgreSQL 适配器单元测试 | 新建 | 2.6 |

### 3.2 详细实现步骤

#### 任务 2.2: PostgreSQLConnectionProvider

**迁移自:** `services/connection.py`

**关键改动：**
```python
class PostgreSQLConnectionProvider(ConnectionProvider):
    """PostgreSQL connection pool manager using asyncpg."""

    _pools: dict[str, asyncpg.Pool] = {}

    async def get_pool(self, config: DatabaseConfig) -> asyncpg.Pool:
        if config.url not in self._pools:
            self._pools[config.url] = await asyncpg.create_pool(
                config.url,
                min_size=1,
                max_size=10,
            )
        return self._pools[config.url]

    async def test_connection(self, config: DatabaseConfig) -> bool:
        try:
            pool = await self.get_pool(config)
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
```

#### 任务 2.3: PostgreSQLMetadataProvider

**迁移自:** `services/metadata.py`

**关键改动：**
- 接收 `ConnectionProvider` 作为依赖
- 使用 `DatabaseConfig` 替代 URL 字符串

```python
class PostgreSQLMetadataProvider(MetadataProvider):
    def __init__(self, connection_provider: ConnectionProvider):
        self._connection_provider = connection_provider

    async def fetch_metadata(
        self, database_name: str, config: DatabaseConfig
    ) -> DatabaseMetadata:
        pool = await self._connection_provider.get_pool(config)
        # ... 复用现有 SQL 查询逻辑
```

#### 任务 2.4: PostgreSQLQueryExecutor

**迁移自:** `services/query.py`

**关键改动：**
- 继承 `BaseQueryExecutor`
- 只实现 `execute()` 和 `dialect` 属性

```python
class PostgreSQLQueryExecutor(BaseQueryExecutor):
    def __init__(
        self,
        connection_provider: ConnectionProvider,
        type_mapper: TypeMapper
    ):
        self._connection_provider = connection_provider
        self._type_mapper = type_mapper

    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.POSTGRES

    async def execute(
        self, config: DatabaseConfig, sql: str
    ) -> QueryResult:
        pool = await self._connection_provider.get_pool(config)
        async with pool.acquire() as conn:
            # ... 复用现有执行逻辑
```

#### 任务 2.5: PostgreSQLTypeMapper

**迁移自:** `services/query.py` 中的 `_infer_pg_type` 函数

```python
class PostgreSQLTypeMapper(BaseTypeMapper):
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
        # PostgreSQL 特定的类型映射
        ...
```

#### 任务 2.6: PostgreSQLAdapter

```python
@DatabaseRegistry.register(DatabaseType.POSTGRESQL)
class PostgreSQLAdapter(DatabaseAdapter):
    @property
    def dialect(self) -> SQLDialect:
        return SQLDialect.POSTGRES

    def _create_connection_provider(self) -> ConnectionProvider:
        return PostgreSQLConnectionProvider()

    def _create_metadata_provider(self) -> MetadataProvider:
        return PostgreSQLMetadataProvider(self._connection_provider)

    def _create_query_executor(self) -> QueryExecutor:
        return PostgreSQLQueryExecutor(
            self._connection_provider,
            self._type_mapper
        )

    def _create_type_mapper(self) -> TypeMapper:
        return PostgreSQLTypeMapper()
```

### 3.3 验证标准

- [ ] `from app.adapters.postgresql import PostgreSQLAdapter` 无错误
- [ ] `DatabaseRegistry.is_supported(DatabaseType.POSTGRESQL)` 返回 `True`
- [ ] 单元测试通过（连接、元数据、查询）
- [ ] 与现有 PostgreSQL 服务功能对等

---

## 四、第三阶段：MySQL 适配器实现

### 4.1 任务清单

| 任务ID | 任务描述 | 新建/修改 | 依赖 |
|--------|---------|----------|------|
| 3.1 | 创建 `app/adapters/mysql/__init__.py` | 新建 | 2.* |
| 3.2 | 创建 `app/adapters/mysql/connection.py` | 新建 | 1.* |
| 3.3 | 创建 `app/adapters/mysql/metadata.py` | 新建 | 3.2 |
| 3.4 | 创建 `app/adapters/mysql/query.py` | 新建 | 3.2 |
| 3.5 | 创建 `app/adapters/mysql/types.py` | 新建 | 1.9 |
| 3.6 | 创建 `app/adapters/mysql/adapter.py` | 新建 | 3.2-3.5 |
| 3.7 | 编写 MySQL 适配器单元测试 | 新建 | 3.6 |

### 4.2 详细实现步骤

与 PostgreSQL 类似，迁移自：
- `services/connection_mysql.py` → `adapters/mysql/connection.py`
- `services/metadata_mysql.py` → `adapters/mysql/metadata.py`
- `services/query_mysql.py` → `adapters/mysql/query.py`

**MySQL 特殊处理：**
- 使用 `aiomysql` 库
- 处理 MySQL 特有的类型（如 `TINYINT(1)` 作为布尔值）
- `information_schema` 查询语法差异

### 4.3 验证标准

- [ ] `from app.adapters.mysql import MySQLAdapter` 无错误
- [ ] `DatabaseRegistry.is_supported(DatabaseType.MYSQL)` 返回 `True`
- [ ] 单元测试通过
- [ ] 与现有 MySQL 服务功能对等

---

## 五、第四阶段：服务层集成

### 5.1 任务清单

| 任务ID | 任务描述 | 新建/修改 | 依赖 |
|--------|---------|----------|------|
| 4.1 | 更新 `services/database.py` 使用 Registry | 修改 | 3.* |
| 4.2 | 更新 `services/llm.py` 使用抽象接口 | 修改 | 3.* |
| 4.3 | 更新 `routers/databases.py`（如需要） | 修改 | 4.1, 4.2 |
| 4.4 | 更新 `main.py` 的 shutdown 逻辑 | 修改 | 4.1 |
| 4.5 | 编写集成测试 | 新建 | 4.1-4.4 |

### 5.2 详细实现步骤

#### 任务 4.1: 更新 `services/database.py`

**当前代码（需要修改的部分）：**
```python
# 旧代码
from app.services.metadata_factory import MetadataFactory
from app.services.connection_factory import ConnectionFactory

# 在 create_or_update_database 中
metadata = await MetadataFactory.fetch_metadata(name, url)
```

**新代码：**
```python
# 新代码
from app.adapters import DatabaseRegistry

# 在 create_or_update_database 中
adapter = DatabaseRegistry.get_adapter_from_url(url)
if not await adapter.test_connection():
    raise ConnectionError(f"Could not connect to database at {url}")
metadata = await adapter.fetch_metadata(name)
```

#### 任务 4.2: 更新 `services/llm.py`

**当前代码：**
```python
# 旧代码
from app.services.query import QueryService
from app.services.query_mysql import MySQLQueryService

if db_type == DatabaseType.MYSQL:
    is_valid, error_msg = MySQLQueryService.validate_sql(generated_sql)
else:
    is_valid, error_msg = QueryService.validate_sql(generated_sql)
```

**新代码：**
```python
# 新代码
from app.adapters import DatabaseRegistry
from app.core import DatabaseConfig

config = DatabaseConfig.from_url(url)
adapter = DatabaseRegistry.get_adapter(config)
is_valid, error_msg = adapter.validate_sql(generated_sql)
```

#### 任务 4.3: 更新 `routers/databases.py`

检查是否有直接使用工厂类的地方，统一改为通过 Service 层调用。

#### 任务 4.4: 更新 `main.py`

**shutdown 事件：**
```python
@app.on_event("shutdown")
async def shutdown():
    await DatabaseRegistry.close_all()
```

### 5.3 验证标准

- [ ] 所有 API 端点正常工作
- [ ] PostgreSQL 和 MySQL 数据库操作正常
- [ ] 无直接依赖旧工厂类的代码
- [ ] 集成测试通过

---

## 六、第五阶段：清理与优化

### 6.1 任务清单

| 任务ID | 任务描述 | 操作 | 依赖 |
|--------|---------|------|------|
| 5.1 | 删除 `services/connection.py` | 删除 | 4.* |
| 5.2 | 删除 `services/connection_mysql.py` | 删除 | 4.* |
| 5.3 | 删除 `services/connection_factory.py` | 删除 | 4.* |
| 5.4 | 删除 `services/connection_base.py` | 删除 | 4.* |
| 5.5 | 删除 `services/metadata.py` | 删除 | 4.* |
| 5.6 | 删除 `services/metadata_mysql.py` | 删除 | 4.* |
| 5.7 | 删除 `services/metadata_factory.py` | 删除 | 4.* |
| 5.8 | 删除 `services/query.py` | 删除 | 4.* |
| 5.9 | 删除 `services/query_mysql.py` | 删除 | 4.* |
| 5.10 | 删除 `services/query_factory.py` | 删除 | 4.* |
| 5.11 | 更新 `models/database.py` 移除冗余类型 | 修改 | 5.1-5.10 |
| 5.12 | 完善文档和注释 | 新建/修改 | 5.11 |
| 5.13 | 运行完整测试套件 | 验证 | 5.12 |

### 6.2 删除文件清单

```bash
# 待删除文件（共 10 个）
rm app/services/connection.py
rm app/services/connection_mysql.py
rm app/services/connection_factory.py
rm app/services/connection_base.py
rm app/services/metadata.py
rm app/services/metadata_mysql.py
rm app/services/metadata_factory.py
rm app/services/query.py          # 注意：这个文件名与 models/query.py 不同
rm app/services/query_mysql.py
rm app/services/query_factory.py
```

### 6.3 验证标准

- [ ] 无未使用的导入
- [ ] 无死代码
- [ ] 所有测试通过
- [ ] 代码覆盖率 >= 80%

---

## 七、最终目录结构

```
backend/app/
├── main.py
├── config.py
├── database.py
├── core/                              # 新增
│   ├── __init__.py
│   ├── types.py
│   ├── exceptions.py
│   └── registry.py
├── adapters/                          # 新增
│   ├── __init__.py
│   ├── base.py
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── query_base.py
│   │   └── type_mapper_base.py
│   ├── postgresql/
│   │   ├── __init__.py
│   │   ├── adapter.py
│   │   ├── connection.py
│   │   ├── metadata.py
│   │   ├── query.py
│   │   └── types.py
│   └── mysql/
│       ├── __init__.py
│       ├── adapter.py
│       ├── connection.py
│       ├── metadata.py
│       ├── query.py
│       └── types.py
├── models/
│   ├── __init__.py
│   ├── database.py                    # 可能需要清理
│   ├── query.py
│   ├── history.py
│   └── error.py
├── services/
│   ├── __init__.py
│   ├── database.py                    # 已更新
│   ├── history.py                     # 保持不变
│   └── llm.py                         # 已更新
└── routers/
    ├── __init__.py
    └── databases.py
```

---

## 八、风险与缓解措施

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|---------|
| 功能回归 | 中 | 高 | 每阶段完成后运行完整测试 |
| 连接池泄漏 | 低 | 高 | 确保 `close_all()` 正确调用 |
| 类型不兼容 | 中 | 中 | 使用 mypy 进行静态类型检查 |
| 并发问题 | 低 | 高 | 使用线程安全的注册表实现 |
| 性能下降 | 低 | 中 | 保持连接池复用，避免重复创建 |

---

## 九、测试策略

### 9.1 单元测试

每个适配器组件独立测试：
- `test_postgresql_connection.py`
- `test_postgresql_metadata.py`
- `test_postgresql_query.py`
- `test_mysql_connection.py`
- `test_mysql_metadata.py`
- `test_mysql_query.py`

### 9.2 集成测试

- `test_registry_integration.py` - 测试注册和自动发现
- `test_database_service_integration.py` - 测试服务层
- `test_api_integration.py` - 测试 API 端点

### 9.3 测试数据库

使用 Docker 容器运行测试数据库：
```yaml
# docker-compose.test.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: test
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: test
```

---

## 十、执行检查清单

### 第一阶段完成检查
- [ ] `app/core/` 目录创建完成
- [ ] `app/adapters/` 骨架创建完成
- [ ] 基础类型和异常定义完成
- [ ] 注册表实现完成

### 第二阶段完成检查
- [ ] PostgreSQL 适配器实现完成
- [ ] PostgreSQL 单元测试通过
- [ ] 功能与现有实现对等

### 第三阶段完成检查
- [ ] MySQL 适配器实现完成
- [ ] MySQL 单元测试通过
- [ ] 功能与现有实现对等

### 第四阶段完成检查
- [ ] 服务层迁移完成
- [ ] 所有 API 正常工作
- [ ] 集成测试通过

### 第五阶段完成检查
- [ ] 旧代码删除完成
- [ ] 无未使用代码
- [ ] 完整测试套件通过
- [ ] 文档更新完成

---

## 十一、回滚计划

如果重构过程中出现严重问题：

1. **阶段 1-3**：直接删除新增的 `core/` 和 `adapters/` 目录
2. **阶段 4**：使用 git 恢复 `services/` 目录下被修改的文件
3. **阶段 5**：使用 git 恢复删除的文件

**关键原则**：在阶段 4 完成并验证通过之前，不要删除任何旧代码。
