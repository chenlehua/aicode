# PostgreSQL MCP Server 测试计划

## 1. 概述

### 1.1 文档目的

本文档详细规划 PostgreSQL MCP Server 的测试策略、测试用例、测试环境和验收标准，确保代码质量达到生产级别要求。

### 1.2 关联文档

| 文档 | 用途 |
|------|------|
| [0001-pg-mcp-prd.md](./0001-pg-mcp-prd.md) | 产品需求定义 |
| [0002-pg-mcp-design.md](./0002-pg-mcp-design.md) | 技术架构设计 |
| [0003-pg-mcp-impl-plan.md](./0003-pg-mcp-impl-plan.md) | 实现计划 |

### 1.3 测试目标

| 目标 | 具体指标 |
|------|----------|
| 代码覆盖率 | 总体 ≥ 80%，关键模块（validator）100% |
| 安全覆盖 | 所有危险 SQL 类型 100% 拦截 |
| 功能覆盖 | 核心查询流程 100% 覆盖 |
| 回归测试 | CI 自动化运行，阻断式检查 |

### 1.4 当前测试状态

**最后验证日期：2026-01-24**

| 指标 | 状态 |
|------|------|
| 测试总数 | 125 个 |
| 通过率 | 100% (125/125) |
| 总体覆盖率 | 79% |

**模块覆盖率详情：**

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| models/errors.py | 100% | ✅ |
| models/query.py | 100% | ✅ |
| models/schema.py | 71% | ⚠️ 需要补充 |
| config/settings.py | 94% | ✅ |
| database/connection.py | 95% | ✅ |
| database/schema_cache.py | 59% | ⚠️ 需要真实 DB 测试 |
| database/service.py | 97% | ✅ |
| llm/service.py | 95% | ✅ |
| query/service.py | 100% | ✅ |
| validator/sql_validator.py | 84% | ⚠️ 接近目标 |
| server.py | 33% | ⚠️ 需要端到端测试 |

---

## 2. 测试策略

### 2.1 测试金字塔

```
                    ┌─────────────┐
                    │   E2E测试   │  ← 少量关键路径
                    │  (server)   │
                ┌───┴─────────────┴───┐
                │     集成测试        │  ← 跨模块交互
                │ (database, llm,     │
                │  query_service)     │
            ┌───┴─────────────────────┴───┐
            │          单元测试           │  ← 基础、覆盖广
            │ (models, config, validator) │
            └─────────────────────────────┘
```

### 2.2 测试分类

| 分类 | 范围 | 运行频率 | 依赖 |
|------|------|----------|------|
| 单元测试 | 单个函数/类 | 每次提交 | 无外部依赖 |
| 集成测试 | 跨模块交互 | 每次提交 | Mock 外部服务 |
| 数据库集成测试 | 真实数据库操作 | PR 合并前 | PostgreSQL 容器 |
| 端到端测试 | 完整 MCP 流程 | 发布前 | 全部依赖 |

### 2.3 Mock 策略

| 模块 | Mock 对象 | Mock 方式 | 原因 |
|------|-----------|-----------|------|
| llm/ | OpenAI API | `unittest.mock.AsyncMock` | 避免 API 费用，加速测试 |
| database/ | asyncpg Pool | `MagicMock` + `AsyncMock` | 无需真实数据库 |
| server.py | QueryService | Dependency Injection | 隔离测试 |

---

## 3. 测试环境

### 3.1 本地开发环境

```yaml
# 测试依赖 (pyproject.toml)
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "pytest-timeout>=2.2.0",
]
```

### 3.2 测试数据库环境

```yaml
# docker-compose.test.yml
services:
  postgres-test:
    image: postgres:16-alpine
    container_name: pg_mcp_test_postgres
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: testdb
    ports:
      - "5433:5432"
    volumes:
      - ./tests/fixtures/init_test_db.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testuser -d testdb"]
      interval: 5s
      timeout: 3s
      retries: 5
```

### 3.3 测试数据初始化

```sql
-- tests/fixtures/init_test_db.sql

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 订单表
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 产品表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    category VARCHAR(50)
);

-- 测试数据
INSERT INTO users (name, email) VALUES 
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com');

INSERT INTO orders (user_id, total, status) VALUES
    (1, 99.99, 'completed'),
    (1, 149.50, 'pending'),
    (2, 200.00, 'completed');

INSERT INTO products (name, price, category) VALUES
    ('Widget A', 29.99, 'electronics'),
    ('Widget B', 49.99, 'electronics'),
    ('Gadget X', 99.99, 'gadgets');

-- 添加注释
COMMENT ON TABLE users IS '用户账户表';
COMMENT ON TABLE orders IS '用户订单表';
COMMENT ON COLUMN users.email IS '用户邮箱地址，唯一';
```

---

## 4. 测试文件规划

### 4.1 测试目录结构

```
tests/
├── __init__.py
├── conftest.py                 # 共享 fixtures
├── fixtures/
│   ├── __init__.py
│   ├── init_test_db.sql        # 数据库初始化脚本
│   └── sample_data.py          # 示例数据工厂
├── unit/                       # 单元测试
│   ├── __init__.py
│   ├── test_models.py          # 数据模型测试
│   ├── test_config.py          # 配置加载测试
│   └── test_validator.py       # SQL 校验测试
├── integration/                # 集成测试
│   ├── __init__.py
│   ├── test_database.py        # 数据库服务测试
│   ├── test_llm.py             # LLM 服务测试
│   └── test_query_service.py   # 查询服务测试
└── e2e/                        # 端到端测试
    ├── __init__.py
    └── test_server.py          # MCP 服务器测试
```

### 4.2 现有测试文件迁移

| 原文件 | 目标位置 | 说明 |
|--------|----------|------|
| `tests/test_models.py` | `tests/unit/test_models.py` | 纯单元测试 |
| `tests/test_config.py` | `tests/unit/test_config.py` | 纯单元测试 |
| `tests/test_validator.py` | `tests/unit/test_validator.py` | 纯单元测试 |
| `tests/test_query_service.py` | `tests/integration/test_query_service.py` | 使用 Mock 的集成测试 |

---

## 5. 详细测试用例

### 5.1 单元测试：数据模型 (test_models.py)

#### 5.1.1 ErrorCode 和异常类

| 测试 ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|---------|----------|------|----------|--------|
| M-ERR-01 | `test_error_code_values` | 所有 ErrorCode 枚举 | 值与名称一致 | P0 |
| M-ERR-02 | `test_query_error_str_with_details` | `QueryError(code, msg, details)` | 字符串包含所有信息 | P0 |
| M-ERR-03 | `test_query_error_str_no_details` | `QueryError(code, msg)` | 字符串不含 None | P1 |
| M-ERR-04 | `test_sql_generation_error_code` | `SQLGenerationError(msg)` | code == SQL_GENERATION_FAILED | P0 |
| M-ERR-05 | `test_sql_unsafe_error_preserves_sql` | `SQLUnsafeError(msg, sql)` | sql 属性保留原始 SQL | P0 |
| M-ERR-06 | `test_sql_execution_error` | `SQLExecutionError(msg, sql)` | 正确初始化 | P1 |
| M-ERR-07 | `test_sql_timeout_error` | `SQLTimeoutError(timeout_ms)` | 消息包含超时时间 | P1 |
| M-ERR-08 | `test_llm_error` | `LLMError(msg)` | code == LLM_API_ERROR | P1 |

#### 5.1.2 QueryRequest/QueryResponse

| 测试 ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|---------|----------|------|----------|--------|
| M-REQ-01 | `test_query_request_valid` | `query="Find all users"` | 创建成功 | P0 |
| M-REQ-02 | `test_query_request_empty_fails` | `query=""` | 抛出 ValueError | P0 |
| M-REQ-03 | `test_query_request_whitespace_only_fails` | `query="   "` | 抛出 ValueError | P1 |
| M-REQ-04 | `test_query_request_too_long_fails` | `query="a"*5000` | 抛出 ValueError | P0 |
| M-REQ-05 | `test_query_request_max_length` | `query="a"*4096` | 创建成功 | P1 |
| M-RES-01 | `test_query_response_success` | 成功响应数据 | success=True, error=None | P0 |
| M-RES-02 | `test_query_response_error` | 错误响应数据 | success=False, result=None | P0 |
| M-RES-03 | `test_query_response_json_serialization` | 完整响应对象 | JSON 序列化成功 | P0 |
| M-RES-04 | `test_query_result_data_empty` | 空结果 | row_count=0 | P1 |

#### 5.1.3 Schema 模型

| 测试 ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|---------|----------|------|----------|--------|
| M-SCH-01 | `test_column_info_defaults` | 最小参数 | 默认值正确 | P0 |
| M-SCH-02 | `test_column_info_full` | 所有参数 | 全部属性正确 | P1 |
| M-SCH-03 | `test_table_info_full_name` | schema="public", name="users" | "public.users" | P0 |
| M-SCH-04 | `test_table_info_column_access` | 包含多列的表 | 列可访问 | P1 |
| M-SCH-05 | `test_database_schema_to_llm_context` | 多表 Schema | 包含所有表和列信息 | P0 |
| M-SCH-06 | `test_database_schema_to_llm_context_with_pk` | 包含主键的表 | 输出包含 PK 标记 | P0 |
| M-SCH-07 | `test_database_schema_to_llm_context_with_fk` | 包含外键的表 | 输出包含 FK 信息 | P1 |
| M-SCH-08 | `test_database_schema_get_table_names` | 多表 Schema | 返回所有表名（带和不带 schema 前缀） | P0 |
| M-SCH-09 | `test_database_schema_empty` | 空 Schema | 空表列表 | P1 |

### 5.2 单元测试：配置管理 (test_config.py)

#### 5.2.1 LLMSettings

| 测试 ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|---------|----------|------|----------|--------|
| C-LLM-01 | `test_llm_settings_default_values` | 仅 api_key | 默认 model, temperature 等 | P0 |
| C-LLM-02 | `test_llm_settings_api_key_secret` | api_key="secret" | str/repr 不暴露密钥 | P0 |
| C-LLM-03 | `test_llm_settings_custom_values` | 自定义所有参数 | 全部正确设置 | P1 |
| C-LLM-04 | `test_llm_settings_base_url_default` | 仅 api_key | 包含 dashscope URL | P1 |

#### 5.2.2 QuerySettings

| 测试 ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|---------|----------|------|----------|--------|
| C-QRY-01 | `test_query_settings_default_values` | 无参数 | default_limit=100, timeout=30000 | P0 |
| C-QRY-02 | `test_query_settings_limit_min_bound` | default_limit=0 | 抛出 ValueError | P0 |
| C-QRY-03 | `test_query_settings_limit_max_bound` | default_limit=20000 | 抛出 ValueError | P0 |
| C-QRY-04 | `test_query_settings_valid_limit` | default_limit=500 | 创建成功 | P1 |
| C-QRY-05 | `test_query_settings_validation_disabled` | enable_validation=False | 正确设置 | P1 |

#### 5.2.3 DatabaseConfig

| 测试 ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|---------|----------|------|----------|--------|
| C-DB-01 | `test_database_config_dsn_generation` | 完整配置 | DSN 包含所有参数 | P0 |
| C-DB-02 | `test_database_config_dsn_with_ssl` | ssl=True | DSN 包含 sslmode=require | P0 |
| C-DB-03 | `test_database_config_password_secret` | password="secret" | 密码不暴露 | P0 |
| C-DB-04 | `test_database_config_default_pool_sizes` | 最小参数 | min=2, max=10 | P1 |
| C-DB-05 | `test_database_config_custom_port` | port=5433 | DSN 使用自定义端口 | P1 |

#### 5.2.4 ConfigLoader

| 测试 ID | 测试名称 | 输入 | 预期输出 | 优先级 |
|---------|----------|------|----------|--------|
| C-LOAD-01 | `test_load_valid_config` | 有效 YAML 文件 | 正确解析数据库配置 | P0 |
| C-LOAD-02 | `test_load_config_env_var_substitution` | `${ENV_VAR}` 语法 | 环境变量正确替换 | P0 |
| C-LOAD-03 | `test_load_config_env_var_default` | `${VAR:default}` 语法 | 使用默认值 | P1 |
| C-LOAD-04 | `test_load_missing_file` | 不存在的路径 | 抛出 FileNotFoundError | P0 |
| C-LOAD-05 | `test_load_empty_config` | 空文件 | 抛出 ValueError | P0 |
| C-LOAD-06 | `test_load_no_databases_section` | 缺少 databases 键 | 抛出 ValueError | P0 |
| C-LOAD-07 | `test_load_multiple_databases` | 多个数据库配置 | 返回列表 | P1 |
| C-LOAD-08 | `test_load_invalid_yaml` | 无效 YAML 语法 | 抛出异常 | P1 |

### 5.3 单元测试：SQL 校验器 (test_validator.py)

**目标覆盖率：100%**

#### 5.3.1 合法 SELECT 语句

| 测试 ID | 测试名称 | 输入 SQL | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| V-SEL-01 | `test_simple_select` | `SELECT * FROM users` | 通过 | P0 |
| V-SEL-02 | `test_select_with_columns` | `SELECT id, name FROM users` | 通过 | P0 |
| V-SEL-03 | `test_select_with_where` | `SELECT * FROM users WHERE id = 1` | 通过 | P0 |
| V-SEL-04 | `test_select_with_join` | `SELECT * FROM a JOIN b ON a.id = b.a_id` | 通过 | P0 |
| V-SEL-05 | `test_select_with_left_join` | `SELECT * FROM a LEFT JOIN b ON ...` | 通过 | P1 |
| V-SEL-06 | `test_select_with_subquery` | `SELECT * FROM (SELECT ...) AS sub` | 通过 | P0 |
| V-SEL-07 | `test_select_with_in_subquery` | `SELECT * FROM a WHERE id IN (SELECT ...)` | 通过 | P1 |
| V-SEL-08 | `test_select_with_aggregate` | `SELECT COUNT(*), SUM(x) FROM t GROUP BY y` | 通过 | P0 |
| V-SEL-09 | `test_select_with_having` | `SELECT ... GROUP BY x HAVING COUNT(*) > 1` | 通过 | P1 |
| V-SEL-10 | `test_select_with_cte` | `WITH cte AS (SELECT ...) SELECT * FROM cte` | 通过 | P0 |
| V-SEL-11 | `test_select_with_order_by` | `SELECT * FROM t ORDER BY id DESC` | 通过 | P1 |
| V-SEL-12 | `test_select_with_limit` | `SELECT * FROM t LIMIT 10` | 通过 | P1 |
| V-SEL-13 | `test_select_with_offset` | `SELECT * FROM t LIMIT 10 OFFSET 5` | 通过 | P2 |
| V-SEL-14 | `test_select_distinct` | `SELECT DISTINCT name FROM users` | 通过 | P1 |
| V-SEL-15 | `test_select_with_alias` | `SELECT u.name AS user_name FROM users u` | 通过 | P1 |
| V-SEL-16 | `test_select_with_case` | `SELECT CASE WHEN x > 0 THEN 'pos' END` | 通过 | P1 |
| V-SEL-17 | `test_select_with_coalesce` | `SELECT COALESCE(name, 'N/A') FROM users` | 通过 | P2 |
| V-SEL-18 | `test_select_with_cast` | `SELECT CAST(id AS TEXT) FROM users` | 通过 | P2 |
| V-SEL-19 | `test_select_union` | `SELECT a FROM t1 UNION SELECT b FROM t2` | 通过 | P1 |
| V-SEL-20 | `test_select_exists` | `SELECT * FROM t WHERE EXISTS (SELECT 1 ...)` | 通过 | P2 |

#### 5.3.2 禁止的 DML 语句

| 测试 ID | 测试名称 | 输入 SQL | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| V-DML-01 | `test_insert_rejected` | `INSERT INTO users VALUES (1)` | SQLUnsafeError | P0 |
| V-DML-02 | `test_insert_with_select_rejected` | `INSERT INTO t SELECT * FROM s` | SQLUnsafeError | P0 |
| V-DML-03 | `test_update_rejected` | `UPDATE users SET name = 'x'` | SQLUnsafeError | P0 |
| V-DML-04 | `test_update_with_where_rejected` | `UPDATE users SET x = 1 WHERE id = 1` | SQLUnsafeError | P0 |
| V-DML-05 | `test_delete_rejected` | `DELETE FROM users` | SQLUnsafeError | P0 |
| V-DML-06 | `test_delete_with_where_rejected` | `DELETE FROM users WHERE id = 1` | SQLUnsafeError | P0 |
| V-DML-07 | `test_merge_rejected` | `MERGE INTO t USING ...` | SQLUnsafeError | P1 |
| V-DML-08 | `test_upsert_rejected` | `INSERT ... ON CONFLICT DO UPDATE` | SQLUnsafeError | P1 |

#### 5.3.3 禁止的 DDL 语句

| 测试 ID | 测试名称 | 输入 SQL | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| V-DDL-01 | `test_create_table_rejected` | `CREATE TABLE test (id int)` | SQLUnsafeError | P0 |
| V-DDL-02 | `test_create_index_rejected` | `CREATE INDEX idx ON t(c)` | SQLUnsafeError | P0 |
| V-DDL-03 | `test_alter_table_rejected` | `ALTER TABLE users ADD COLUMN x int` | SQLUnsafeError | P0 |
| V-DDL-04 | `test_drop_table_rejected` | `DROP TABLE users` | SQLUnsafeError | P0 |
| V-DDL-05 | `test_drop_database_rejected` | `DROP DATABASE testdb` | SQLUnsafeError | P0 |
| V-DDL-06 | `test_truncate_rejected` | `TRUNCATE TABLE users` | SQLUnsafeError | P0 |
| V-DDL-07 | `test_grant_rejected` | `GRANT SELECT ON users TO public` | SQLUnsafeError | P1 |
| V-DDL-08 | `test_revoke_rejected` | `REVOKE SELECT ON users FROM public` | SQLUnsafeError | P1 |

#### 5.3.4 多语句攻击

| 测试 ID | 测试名称 | 输入 SQL | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| V-MULTI-01 | `test_select_then_drop` | `SELECT 1; DROP TABLE users` | SQLUnsafeError, 消息含"多条" | P0 |
| V-MULTI-02 | `test_select_then_insert` | `SELECT * FROM t; INSERT INTO t VALUES (1)` | SQLUnsafeError | P0 |
| V-MULTI-03 | `test_multiple_selects` | `SELECT 1; SELECT 2` | SQLUnsafeError | P0 |
| V-MULTI-04 | `test_comment_bypass_attempt` | `SELECT 1; -- comment\n DROP TABLE x` | SQLUnsafeError | P0 |

#### 5.3.5 危险函数

| 测试 ID | 测试名称 | 输入 SQL | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| V-FUNC-01 | `test_pg_read_file_rejected` | `SELECT pg_read_file('/etc/passwd')` | SQLUnsafeError, 消息含函数名 | P0 |
| V-FUNC-02 | `test_pg_read_binary_file_rejected` | `SELECT pg_read_binary_file('...')` | SQLUnsafeError | P0 |
| V-FUNC-03 | `test_pg_ls_dir_rejected` | `SELECT pg_ls_dir('/')` | SQLUnsafeError | P0 |
| V-FUNC-04 | `test_pg_stat_file_rejected` | `SELECT pg_stat_file('/etc/passwd')` | SQLUnsafeError | P1 |
| V-FUNC-05 | `test_lo_import_rejected` | `SELECT lo_import('/etc/passwd')` | SQLUnsafeError | P0 |
| V-FUNC-06 | `test_lo_export_rejected` | `SELECT lo_export(12345, '/tmp/x')` | SQLUnsafeError | P0 |
| V-FUNC-07 | `test_dblink_rejected` | `SELECT * FROM dblink('host=evil', 'q')` | SQLUnsafeError | P0 |
| V-FUNC-08 | `test_dblink_exec_rejected` | `SELECT dblink_exec('conn', 'DROP TABLE')` | SQLUnsafeError | P0 |
| V-FUNC-09 | `test_dblink_connect_rejected` | `SELECT dblink_connect('host=evil')` | SQLUnsafeError | P1 |
| V-FUNC-10 | `test_copy_rejected` | `SELECT copy('t', '/tmp/x', 'csv')` | SQLUnsafeError | P1 |
| V-FUNC-11 | `test_nested_dangerous_function` | `SELECT (SELECT pg_read_file('x'))` | SQLUnsafeError | P0 |
| V-FUNC-12 | `test_safe_functions_allowed` | `SELECT COUNT(*), MAX(id), NOW()` | 通过 | P0 |

#### 5.3.6 语法错误和边界情况

| 测试 ID | 测试名称 | 输入 SQL | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| V-EDGE-01 | `test_empty_sql_rejected` | `""` | SQLUnsafeError, 消息含"空" | P0 |
| V-EDGE-02 | `test_whitespace_only_rejected` | `"   "` | SQLUnsafeError | P0 |
| V-EDGE-03 | `test_syntax_error_rejected` | `SELEC * FORM users` | SQLUnsafeError | P0 |
| V-EDGE-04 | `test_incomplete_sql` | `SELECT * FROM` | SQLUnsafeError | P1 |
| V-EDGE-05 | `test_null_input` | `None` | 抛出异常 | P1 |
| V-EDGE-06 | `test_very_long_sql` | 10000 字符的 SELECT | 正常处理 | P2 |
| V-EDGE-07 | `test_unicode_table_name` | `SELECT * FROM 用户表` | 正常解析 | P2 |

#### 5.3.7 表名验证（known_tables 模式）

| 测试 ID | 测试名称 | 输入 | 预期结果 | 优先级 |
|---------|----------|------|----------|--------|
| V-TBL-01 | `test_known_table_passes` | `SELECT * FROM users` (known: {users}) | 通过 | P0 |
| V-TBL-02 | `test_unknown_table_rejected` | `SELECT * FROM unknown` (known: {users}) | SQLUnsafeError, 消息含"未知" | P0 |
| V-TBL-03 | `test_schema_qualified_table` | `SELECT * FROM public.users` (known: {public.users}) | 通过 | P0 |
| V-TBL-04 | `test_no_known_tables_skip_check` | `SELECT * FROM anything` (known: None) | 通过 | P1 |
| V-TBL-05 | `test_join_all_tables_known` | `SELECT * FROM a JOIN b` (known: {a, b}) | 通过 | P1 |
| V-TBL-06 | `test_join_one_table_unknown` | `SELECT * FROM a JOIN c` (known: {a, b}) | SQLUnsafeError | P1 |

#### 5.3.8 辅助方法

| 测试 ID | 测试名称 | 输入 | 预期结果 | 优先级 |
|---------|----------|------|----------|--------|
| V-HELP-01 | `test_is_select_only_true` | `SELECT * FROM users` | True | P0 |
| V-HELP-02 | `test_is_select_only_false_insert` | `INSERT INTO t VALUES (1)` | False | P0 |
| V-HELP-03 | `test_is_select_only_false_invalid` | `NOT VALID SQL` | False | P0 |

### 5.4 集成测试：数据库服务 (test_database.py)

#### 5.4.1 连接池测试 (ConnectionPool)

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| D-POOL-01 | `test_pool_initialize` | 调用 initialize() | 连接池创建成功 | P0 |
| D-POOL-02 | `test_pool_acquire_connection` | 使用 acquire() 获取连接 | 返回可用连接 | P0 |
| D-POOL-03 | `test_pool_connection_released` | acquire() 上下文结束 | 连接返回池中 | P0 |
| D-POOL-04 | `test_pool_close` | 调用 close() | 池关闭，无泄露 | P0 |
| D-POOL-05 | `test_pool_is_initialized_property` | 检查 is_initialized | 初始化前 False，后 True | P1 |
| D-POOL-06 | `test_pool_double_initialize` | 调用 initialize() 两次 | 幂等，无异常 | P1 |
| D-POOL-07 | `test_pool_invalid_config` | 无效数据库配置 | 抛出连接错误 | P1 |

#### 5.4.2 Schema 缓存测试 (SchemaCache)

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| D-SCH-01 | `test_schema_refresh` | 调用 refresh() | 返回 DatabaseSchema | P0 |
| D-SCH-02 | `test_schema_contains_tables` | 刷新后检查 tables | 包含测试表 (users, orders) | P0 |
| D-SCH-03 | `test_schema_contains_columns` | 检查表的列信息 | 列名、类型正确 | P0 |
| D-SCH-04 | `test_schema_primary_keys` | 检查主键标记 | id 列标记为 PK | P0 |
| D-SCH-05 | `test_schema_foreign_keys` | 检查外键信息 | orders.user_id 关联 users.id | P1 |
| D-SCH-06 | `test_schema_comments` | 检查表/列注释 | 正确获取 COMMENT | P2 |
| D-SCH-07 | `test_schema_get_table_names` | 调用 get_table_names() | 返回所有表名集合 | P0 |
| D-SCH-08 | `test_schema_caching` | 多次访问 schema 属性 | 返回相同对象 | P1 |

#### 5.4.3 数据库服务测试 (DatabaseService)

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| D-SVC-01 | `test_service_initialize` | 调用 initialize() | 连接池和 Schema 初始化 | P0 |
| D-SVC-02 | `test_service_schema_property` | 访问 schema 属性 | 返回 DatabaseSchema | P0 |
| D-SVC-03 | `test_service_schema_before_init` | 初始化前访问 schema | 抛出 RuntimeError | P0 |
| D-SVC-04 | `test_execute_query_simple` | `SELECT * FROM users` | 返回正确结果 | P0 |
| D-SVC-05 | `test_execute_query_with_where` | `SELECT * FROM users WHERE id=1` | 返回过滤结果 | P0 |
| D-SVC-06 | `test_execute_query_auto_limit` | 无 LIMIT 的 SELECT | 自动添加 LIMIT | P0 |
| D-SVC-07 | `test_execute_query_preserve_limit` | 有 LIMIT 的 SELECT | 保留原 LIMIT | P1 |
| D-SVC-08 | `test_execute_query_custom_limit` | limit 参数 | 使用自定义 limit | P1 |
| D-SVC-09 | `test_execute_query_empty_result` | 无匹配数据 | row_count=0 | P1 |
| D-SVC-10 | `test_execute_query_execution_time` | 任意查询 | execution_time_ms > 0 | P1 |
| D-SVC-11 | `test_execute_query_timeout` | 超时查询 | 抛出 SQLTimeoutError | P0 |
| D-SVC-12 | `test_execute_query_sql_error` | 无效 SQL | 抛出 SQLExecutionError | P0 |
| D-SVC-13 | `test_refresh_schema` | 调用 refresh_schema() | 返回更新的 Schema | P1 |
| D-SVC-14 | `test_service_close` | 调用 close() | 资源释放 | P0 |

### 5.5 集成测试：LLM 服务 (test_llm.py)

#### 5.5.1 Mock 测试（无真实 API）

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| L-GEN-01 | `test_generate_sql_success` | Mock 返回有效 SQL | 返回清理后的 SQL | P0 |
| L-GEN-02 | `test_generate_sql_markdown_cleanup` | Mock 返回 \`\`\`sql...\`\`\` | 移除 markdown 标记 | P0 |
| L-GEN-03 | `test_generate_sql_with_explanation` | Mock 返回 "这是 SQL: SELECT ..." | 提取纯 SQL | P1 |
| L-GEN-04 | `test_generate_sql_empty_response` | Mock 返回空字符串 | 抛出 SQLGenerationError | P0 |
| L-GEN-05 | `test_generate_sql_no_select` | Mock 返回无效 SQL | 抛出 SQLGenerationError | P1 |
| L-GEN-06 | `test_generate_sql_api_error` | Mock 抛出异常 | 抛出 LLMError | P0 |
| L-VAL-01 | `test_validate_result_passed` | Mock 返回 {"passed": true, ...} | ValidationResult(passed=True) | P0 |
| L-VAL-02 | `test_validate_result_failed` | Mock 返回 {"passed": false, ...} | ValidationResult(passed=False) | P0 |
| L-VAL-03 | `test_validate_result_invalid_json` | Mock 返回非 JSON | 默认通过 | P1 |
| L-VAL-04 | `test_validate_result_api_error` | Mock 抛出异常 | 默认通过，不阻断 | P0 |
| L-VAL-05 | `test_validate_result_empty_response` | Mock 返回空 | 默认通过 | P1 |

#### 5.5.2 辅助方法测试

| 测试 ID | 测试名称 | 输入 | 预期结果 | 优先级 |
|---------|----------|------|----------|--------|
| L-CLEAN-01 | `test_clean_sql_plain` | `SELECT * FROM t` | 不变 | P0 |
| L-CLEAN-02 | `test_clean_sql_markdown` | \`\`\`sql\nSELECT...\n\`\`\` | 移除标记 | P0 |
| L-CLEAN-03 | `test_clean_sql_whitespace` | `  SELECT...  ` | 去除空白 | P1 |
| L-CLEAN-04 | `test_clean_sql_with_text` | `查询结果: SELECT...` | 提取 SELECT 部分 | P1 |
| L-PARSE-01 | `test_parse_validation_json` | `{"passed": true, "message": "OK"}` | 正确解析 | P0 |
| L-PARSE-02 | `test_parse_validation_wrapped_json` | 包含 JSON 的文本 | 提取并解析 | P1 |
| L-PARSE-03 | `test_parse_validation_text_pass` | "结果正确" | passed=True | P1 |
| L-PARSE-04 | `test_parse_validation_text_fail` | "结果不符合预期" | passed=False | P1 |
| L-FORMAT-01 | `test_format_sample_rows_normal` | 正常数据 | 格式化输出 | P1 |
| L-FORMAT-02 | `test_format_sample_rows_empty` | 空数据 | "（无数据）" | P1 |
| L-FORMAT-03 | `test_format_sample_rows_truncate` | 长字符串 | 截断为 47+... | P2 |
| L-FORMAT-04 | `test_format_sample_rows_null` | 包含 NULL | 显示 "NULL" | P2 |

### 5.6 集成测试：查询服务 (test_query_service.py)

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| Q-01 | `test_execute_success` | 完整查询流程 | success=True, 有 sql/result/validation | P0 |
| Q-02 | `test_execute_without_validation` | enable_validation=False | validation=None | P0 |
| Q-03 | `test_execute_sql_generation_error` | LLM 生成失败 | error_code=SQL_GENERATION_FAILED | P0 |
| Q-04 | `test_execute_unsafe_sql` | LLM 返回 DROP TABLE | error_code=SQL_UNSAFE | P0 |
| Q-05 | `test_execute_sql_execution_error` | DB 执行失败 | error_code=SQL_EXECUTION_FAILED | P0 |
| Q-06 | `test_execute_sql_timeout` | DB 超时 | error_code=SQL_TIMEOUT | P0 |
| Q-07 | `test_execute_llm_api_error` | LLM API 调用失败 | error_code=LLM_API_ERROR | P0 |
| Q-08 | `test_execute_unexpected_error` | 未知异常 | error_code=INTERNAL_ERROR | P0 |
| Q-09 | `test_execute_validation_failure` | 验证不通过 | success=True, validation.passed=False | P1 |
| Q-10 | `test_execute_empty_result` | 查询无数据 | success=True, row_count=0 | P1 |
| Q-11 | `test_execute_uses_schema` | 检查 LLM 调用参数 | 传入正确的 schema | P1 |
| Q-12 | `test_execute_uses_limit` | 检查 DB 调用参数 | 传入正确的 limit | P1 |

### 5.7 端到端测试：MCP 服务器 (test_server.py)

#### 5.7.1 服务器生命周期

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| S-LIFE-01 | `test_server_startup` | 启动服务器 | 无异常，日志正确 | P0 |
| S-LIFE-02 | `test_server_shutdown` | 关闭服务器 | 资源释放 | P0 |
| S-LIFE-03 | `test_server_missing_config` | 缺少配置文件 | 抛出 RuntimeError | P0 |
| S-LIFE-04 | `test_server_invalid_config` | 无效配置 | 抛出异常 | P1 |

#### 5.7.2 MCP Tool 测试

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| S-TOOL-01 | `test_query_tool_success` | 调用 query("查询用户") | 返回 JSON，success=true | P0 |
| S-TOOL-02 | `test_query_tool_error` | 无效查询 | 返回 JSON，success=false | P0 |
| S-TOOL-03 | `test_query_tool_unsafe_sql` | 恶意查询 | 返回 SQL_UNSAFE 错误 | P0 |
| S-TOOL-04 | `test_refresh_schema_tool` | 调用 refresh_schema() | 返回成功信息 | P1 |
| S-TOOL-05 | `test_get_schema_tool` | 调用 get_schema() | 返回 schema 信息 | P1 |
| S-TOOL-06 | `test_tool_before_init` | 初始化前调用 tool | 返回"服务未初始化" | P1 |

#### 5.7.3 MCP 协议测试

| 测试 ID | 测试名称 | 测试内容 | 预期结果 | 优先级 |
|---------|----------|----------|----------|--------|
| S-MCP-01 | `test_tools_discoverable` | 列出可用 tools | 包含 query, refresh_schema, get_schema | P0 |
| S-MCP-02 | `test_tool_descriptions` | 检查 tool 描述 | 描述非空，包含用途说明 | P1 |
| S-MCP-03 | `test_tool_parameter_schema` | 检查参数定义 | query 参数必填 | P1 |

---

## 6. 测试执行

### 6.1 测试命令

```bash
# 运行所有测试
uv run pytest

# 运行特定类别测试
uv run pytest tests/unit/          # 单元测试
uv run pytest tests/integration/   # 集成测试
uv run pytest tests/e2e/           # 端到端测试

# 运行特定模块测试
uv run pytest tests/unit/test_validator.py -v

# 运行特定测试用例
uv run pytest tests/unit/test_validator.py::TestSQLValidator::test_insert_rejected -v

# 带覆盖率报告
uv run pytest --cov=pg_mcp --cov-report=html --cov-report=term-missing

# 快速测试（跳过慢测试）
uv run pytest -m "not slow"

# 并行测试
uv run pytest -n auto
```

### 6.2 测试标记

```python
# conftest.py 中定义标记
pytest.mark.unit        # 单元测试
pytest.mark.integration # 集成测试
pytest.mark.e2e         # 端到端测试
pytest.mark.slow        # 慢测试
pytest.mark.db          # 需要数据库
pytest.mark.llm         # 需要 LLM API（或 Mock）
```

### 6.3 pytest 配置

```toml
# pyproject.toml

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests",
    "db: Tests requiring database",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
branch = true
source = ["src/pg_mcp"]
omit = ["*/tests/*", "*/__main__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
fail_under = 80
```

---

## 7. 测试 Fixtures

### 7.1 共享 Fixtures (conftest.py)

```python
# tests/conftest.py

import pytest
from unittest.mock import AsyncMock, MagicMock

from pg_mcp.config import DatabaseConfig, LLMSettings, QuerySettings
from pg_mcp.models import (
    ColumnInfo,
    DatabaseSchema,
    QueryResultData,
    TableInfo,
    ValidationResult,
)


# ============ 配置 Fixtures ============

@pytest.fixture
def sample_llm_settings() -> LLMSettings:
    """Sample LLM settings for testing."""
    return LLMSettings(
        api_key="test-api-key",
        base_url="https://api.example.com/v1",
        model="test-model",
        temperature=0.1,
        timeout=30.0,
        max_tokens=2048,
    )


@pytest.fixture
def sample_query_settings() -> QuerySettings:
    """Sample query settings for testing."""
    return QuerySettings(
        default_limit=100,
        statement_timeout=30000,
        enable_validation=True,
    )


@pytest.fixture
def sample_database_config() -> DatabaseConfig:
    """Sample database configuration for testing."""
    return DatabaseConfig(
        name="test_db",
        host="localhost",
        port=5432,
        database="testdb",
        user="testuser",
        password="testpass",
        min_pool_size=2,
        max_pool_size=5,
        ssl=False,
    )


# ============ 数据模型 Fixtures ============

@pytest.fixture
def sample_column_info() -> ColumnInfo:
    """Sample column info for testing."""
    return ColumnInfo(
        name="id",
        data_type="integer",
        is_nullable=False,
        is_primary_key=True,
    )


@pytest.fixture
def sample_table_info() -> TableInfo:
    """Sample table info for testing."""
    return TableInfo(
        schema_name="public",
        name="users",
        columns=[
            ColumnInfo(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
            ColumnInfo(name="name", data_type="varchar", is_nullable=False),
            ColumnInfo(name="email", data_type="varchar", is_nullable=False),
            ColumnInfo(name="created_at", data_type="timestamp", is_nullable=False),
        ],
        comment="User accounts table",
    )


@pytest.fixture
def sample_schema() -> DatabaseSchema:
    """Sample database schema for testing."""
    return DatabaseSchema(
        database_name="testdb",
        tables=[
            TableInfo(
                schema_name="public",
                name="users",
                columns=[
                    ColumnInfo(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                    ColumnInfo(name="name", data_type="varchar", is_nullable=False),
                    ColumnInfo(name="email", data_type="varchar", is_nullable=False),
                    ColumnInfo(name="created_at", data_type="timestamp", is_nullable=False),
                ],
                comment="User accounts table",
            ),
            TableInfo(
                schema_name="public",
                name="orders",
                columns=[
                    ColumnInfo(name="id", data_type="integer", is_nullable=False, is_primary_key=True),
                    ColumnInfo(
                        name="user_id", 
                        data_type="integer", 
                        is_nullable=False,
                        is_foreign_key=True,
                        foreign_table="public.users",
                        foreign_column="id",
                    ),
                    ColumnInfo(name="total", data_type="numeric", is_nullable=False),
                ],
                comment="Customer orders",
            ),
        ],
    )


@pytest.fixture
def sample_query_result() -> QueryResultData:
    """Sample query result for testing."""
    return QueryResultData(
        columns=["id", "name", "email"],
        rows=[
            [1, "Alice", "alice@example.com"],
            [2, "Bob", "bob@example.com"],
        ],
        row_count=2,
        execution_time_ms=15.5,
    )


@pytest.fixture
def sample_empty_result() -> QueryResultData:
    """Sample empty query result for testing."""
    return QueryResultData(
        columns=[],
        rows=[],
        row_count=0,
        execution_time_ms=5.0,
    )


# ============ Mock 服务 Fixtures ============

@pytest.fixture
def mock_llm_service(sample_query_result: QueryResultData) -> MagicMock:
    """Mock LLM service."""
    service = MagicMock()
    service.generate_sql = AsyncMock(return_value="SELECT * FROM users")
    service.validate_result = AsyncMock(
        return_value=ValidationResult(
            passed=True,
            message="查询结果符合预期",
        )
    )
    return service


@pytest.fixture
def mock_database_service(
    sample_schema: DatabaseSchema,
    sample_query_result: QueryResultData,
) -> MagicMock:
    """Mock database service."""
    service = MagicMock()
    service.schema = sample_schema
    service.get_table_names = MagicMock(
        return_value={"users", "orders", "public.users", "public.orders"}
    )
    service.execute_query = AsyncMock(return_value=sample_query_result)
    service.initialize = AsyncMock()
    service.close = AsyncMock()
    service.refresh_schema = AsyncMock(return_value=sample_schema)
    return service


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Mock OpenAI client for LLM testing."""
    client = MagicMock()
    
    # Mock successful SQL generation response
    sql_response = MagicMock()
    sql_response.choices = [MagicMock()]
    sql_response.choices[0].message.content = "SELECT * FROM users"
    
    # Mock successful validation response
    validation_response = MagicMock()
    validation_response.choices = [MagicMock()]
    validation_response.choices[0].message.content = '{"passed": true, "message": "验证通过"}'
    
    client.chat.completions.create = AsyncMock(return_value=sql_response)
    
    return client


# ============ 数据库测试 Fixtures ============

@pytest.fixture
def test_db_config() -> DatabaseConfig:
    """Database config for integration tests."""
    return DatabaseConfig(
        name="test_integration",
        host="localhost",
        port=5433,  # 测试数据库端口
        database="testdb",
        user="testuser",
        password="testpass",
    )


@pytest.fixture
async def initialized_db_service(test_db_config, sample_query_settings):
    """Initialized database service for integration tests."""
    from pg_mcp.database import DatabaseService
    
    service = DatabaseService(test_db_config, sample_query_settings)
    await service.initialize()
    yield service
    await service.close()
```

### 7.2 数据工厂 (fixtures/sample_data.py)

```python
# tests/fixtures/sample_data.py

"""Test data factories for pg-mcp tests."""

from pg_mcp.models import (
    ColumnInfo,
    DatabaseSchema,
    QueryResultData,
    TableInfo,
    ValidationResult,
)


class SchemaFactory:
    """Factory for creating test database schemas."""
    
    @staticmethod
    def create_simple_schema() -> DatabaseSchema:
        """Create a simple schema with one table."""
        return DatabaseSchema(
            database_name="simple_db",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="items",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(name="name", data_type="varchar"),
                    ],
                )
            ],
        )
    
    @staticmethod
    def create_complex_schema() -> DatabaseSchema:
        """Create a complex schema with multiple tables and relations."""
        return DatabaseSchema(
            database_name="complex_db",
            tables=[
                TableInfo(
                    schema_name="public",
                    name="users",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(name="name", data_type="varchar"),
                        ColumnInfo(name="email", data_type="varchar"),
                    ],
                ),
                TableInfo(
                    schema_name="public",
                    name="orders",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(
                            name="user_id", 
                            data_type="integer",
                            is_foreign_key=True,
                            foreign_table="public.users",
                            foreign_column="id",
                        ),
                        ColumnInfo(name="total", data_type="numeric"),
                    ],
                ),
                TableInfo(
                    schema_name="public",
                    name="order_items",
                    columns=[
                        ColumnInfo(name="id", data_type="integer", is_primary_key=True),
                        ColumnInfo(
                            name="order_id",
                            data_type="integer",
                            is_foreign_key=True,
                            foreign_table="public.orders",
                            foreign_column="id",
                        ),
                        ColumnInfo(name="product_id", data_type="integer"),
                        ColumnInfo(name="quantity", data_type="integer"),
                    ],
                ),
            ],
        )


class ResultFactory:
    """Factory for creating test query results."""
    
    @staticmethod
    def create_user_list() -> QueryResultData:
        """Create a sample user list result."""
        return QueryResultData(
            columns=["id", "name", "email"],
            rows=[
                [1, "Alice", "alice@example.com"],
                [2, "Bob", "bob@example.com"],
                [3, "Charlie", "charlie@example.com"],
            ],
            row_count=3,
            execution_time_ms=10.0,
        )
    
    @staticmethod
    def create_aggregate_result() -> QueryResultData:
        """Create an aggregate query result."""
        return QueryResultData(
            columns=["count", "total"],
            rows=[[100, 9999.99]],
            row_count=1,
            execution_time_ms=5.0,
        )
    
    @staticmethod
    def create_empty_result() -> QueryResultData:
        """Create an empty result."""
        return QueryResultData(
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=2.0,
        )


class SQLFactory:
    """Factory for creating test SQL statements."""
    
    # Valid SELECT statements
    VALID_SELECTS = [
        "SELECT * FROM users",
        "SELECT id, name FROM users WHERE id = 1",
        "SELECT COUNT(*) FROM orders GROUP BY user_id",
        "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id",
        "WITH cte AS (SELECT * FROM users) SELECT * FROM cte",
    ]
    
    # Invalid DML statements
    INVALID_DML = [
        "INSERT INTO users (name) VALUES ('test')",
        "UPDATE users SET name = 'test' WHERE id = 1",
        "DELETE FROM users WHERE id = 1",
    ]
    
    # Invalid DDL statements
    INVALID_DDL = [
        "DROP TABLE users",
        "CREATE TABLE test (id int)",
        "ALTER TABLE users ADD COLUMN x int",
        "TRUNCATE TABLE users",
    ]
    
    # Dangerous function calls
    DANGEROUS_FUNCTIONS = [
        "SELECT pg_read_file('/etc/passwd')",
        "SELECT * FROM dblink('host=evil.com', 'SELECT 1')",
        "SELECT lo_import('/etc/passwd')",
    ]
    
    # Multi-statement attacks
    MULTI_STATEMENTS = [
        "SELECT 1; DROP TABLE users",
        "SELECT * FROM users; INSERT INTO users VALUES (1)",
    ]
```

---

## 8. CI/CD 集成

### 8.1 GitHub Actions 配置

```yaml
# .github/workflows/test.yml

name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Set up Python
        run: uv python install 3.12
      
      - name: Install dependencies
        run: uv sync --all-extras
      
      - name: Run unit tests
        run: uv run pytest tests/unit/ -v --cov=pg_mcp --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5433:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Set up Python
        run: uv python install 3.12
      
      - name: Install dependencies
        run: uv sync --all-extras
      
      - name: Initialize test database
        run: |
          PGPASSWORD=testpass psql -h localhost -p 5433 -U testuser -d testdb \
            -f tests/fixtures/init_test_db.sql
      
      - name: Run integration tests
        run: uv run pytest tests/integration/ -v -m "db"
        env:
          TEST_DB_HOST: localhost
          TEST_DB_PORT: 5433
          TEST_DB_USER: testuser
          TEST_DB_PASSWORD: testpass
          TEST_DB_NAME: testdb

  coverage-check:
    runs-on: ubuntu-latest
    needs: [unit-tests]
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
      
      - name: Set up Python
        run: uv python install 3.12
      
      - name: Install dependencies
        run: uv sync --all-extras
      
      - name: Run all tests with coverage
        run: |
          uv run pytest --cov=pg_mcp --cov-report=term-missing --cov-fail-under=80
```

### 8.2 Pre-commit 配置

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: uv run pytest tests/unit/ -q
        language: system
        pass_filenames: false
        always_run: true
```

---

## 9. 覆盖率目标

### 9.1 模块覆盖率要求

| 模块 | 目标覆盖率 | 关键测试点 |
|------|------------|------------|
| models/errors.py | 95%+ | 所有异常类创建和属性 |
| models/query.py | 95%+ | 请求验证、响应构建 |
| models/schema.py | 90%+ | Schema 转换、表名获取 |
| config/settings.py | 90%+ | 配置加载、默认值、边界校验 |
| validator/sql_validator.py | **100%** | 所有安全规则必须覆盖 |
| database/connection.py | 80%+ | 连接池生命周期 |
| database/schema_cache.py | 85%+ | 缓存刷新、表名获取 |
| database/service.py | 85%+ | 查询执行、错误处理 |
| llm/prompts.py | N/A | 仅常量定义 |
| llm/service.py | 85%+ | SQL 生成、结果验证 |
| query/service.py | 90%+ | 编排流程、错误处理 |
| server.py | 70%+ | 生命周期、Tool 注册 |

### 9.2 覆盖率排除

```python
# 排除覆盖率检查的代码模式
# pragma: no cover - 显式排除
# if TYPE_CHECKING: - 类型检查代码块
# def __repr__ - 调试表示方法
# raise NotImplementedError - 抽象方法
# __main__.py - 入口脚本
```

---

## 10. 安全测试检查清单

### 10.1 SQL 注入防护

| 检查项 | 测试方法 | 状态 |
|--------|----------|------|
| INSERT 语句被拒绝 | `test_insert_rejected` | ⬜ |
| UPDATE 语句被拒绝 | `test_update_rejected` | ⬜ |
| DELETE 语句被拒绝 | `test_delete_rejected` | ⬜ |
| DROP 语句被拒绝 | `test_drop_rejected` | ⬜ |
| CREATE 语句被拒绝 | `test_create_rejected` | ⬜ |
| ALTER 语句被拒绝 | `test_alter_rejected` | ⬜ |
| TRUNCATE 语句被拒绝 | `test_truncate_rejected` | ⬜ |
| GRANT/REVOKE 被拒绝 | `test_grant/revoke_rejected` | ⬜ |
| 多语句注入被拒绝 | `test_multiple_statements_rejected` | ⬜ |
| 注释绕过尝试被拒绝 | `test_comment_bypass_attempt` | ⬜ |

### 10.2 危险函数防护

| 检查项 | 测试方法 | 状态 |
|--------|----------|------|
| pg_read_file 被拒绝 | `test_pg_read_file_rejected` | ⬜ |
| pg_read_binary_file 被拒绝 | `test_pg_read_binary_file_rejected` | ⬜ |
| pg_ls_dir 被拒绝 | `test_pg_ls_dir_rejected` | ⬜ |
| lo_import/lo_export 被拒绝 | `test_lo_import/export_rejected` | ⬜ |
| dblink 函数被拒绝 | `test_dblink_rejected` | ⬜ |
| dblink_exec 被拒绝 | `test_dblink_exec_rejected` | ⬜ |
| copy 函数被拒绝 | `test_copy_rejected` | ⬜ |

### 10.3 敏感信息保护

| 检查项 | 测试方法 | 状态 |
|--------|----------|------|
| API Key 不在日志中暴露 | `test_api_key_secret` | ⬜ |
| 数据库密码不在日志中暴露 | `test_password_secret` | ⬜ |
| DSN 不直接记录日志 | 代码审查 | ⬜ |

---

## 11. 性能测试

### 11.1 性能基准

| 测试场景 | 目标指标 | 测试方法 |
|----------|----------|----------|
| Schema 缓存加载 | < 5 秒 | `test_schema_load_performance` |
| SQL 校验响应 | < 100 毫秒 | `test_validator_performance` |
| 简单查询响应 | < 1 秒 (不含 LLM) | `test_query_performance` |
| 连接池获取 | < 50 毫秒 | `test_pool_acquire_performance` |

### 11.2 性能测试代码示例

```python
# tests/performance/test_performance.py

import pytest
import time


class TestPerformance:
    """Performance tests for pg-mcp."""
    
    @pytest.mark.slow
    def test_validator_performance(self, validator):
        """Test SQL validation performance."""
        sql = "SELECT * FROM users WHERE id = 1"
        
        start = time.perf_counter()
        for _ in range(1000):
            validator.validate(sql)
        elapsed = time.perf_counter() - start
        
        # 1000 次验证应在 1 秒内完成
        assert elapsed < 1.0, f"Validation too slow: {elapsed:.2f}s for 1000 iterations"
    
    @pytest.mark.slow
    @pytest.mark.db
    async def test_schema_load_performance(self, initialized_db_service):
        """Test schema loading performance."""
        start = time.perf_counter()
        await initialized_db_service.refresh_schema()
        elapsed = time.perf_counter() - start
        
        assert elapsed < 5.0, f"Schema load too slow: {elapsed:.2f}s"
```

---

## 12. 验收标准汇总

### 12.1 功能验收

| 验收项 | 验收标准 | 测试用例 |
|--------|----------|----------|
| 查询工具可用 | MCP 客户端可发现并调用 query tool | S-MCP-01, S-TOOL-01 |
| SQL 生成成功 | 自然语言可转换为有效 SQL | Q-01 |
| SQL 安全校验 | 所有危险操作被拦截 | V-DML-*, V-DDL-*, V-FUNC-* |
| 查询执行成功 | SELECT 查询可正常执行返回结果 | D-SVC-04 |
| 结果验证可用 | LLM 可验证查询结果 | L-VAL-01 |
| 错误处理完整 | 各类错误返回正确错误码 | Q-03 ~ Q-08 |

### 12.2 质量验收

| 验收项 | 验收标准 |
|--------|----------|
| 单元测试通过 | `uv run pytest tests/unit/` 全部通过 |
| 集成测试通过 | `uv run pytest tests/integration/` 全部通过 |
| 代码覆盖率 | 总体 ≥ 80%，validator 100% |
| 安全测试通过 | 安全检查清单全部 ✅ |

### 12.3 安全验收

| 验收项 | 验证方法 |
|--------|----------|
| 禁止 DML 操作 | 所有 V-DML-* 测试通过 |
| 禁止 DDL 操作 | 所有 V-DDL-* 测试通过 |
| 禁止多语句 | 所有 V-MULTI-* 测试通过 |
| 禁止危险函数 | 所有 V-FUNC-* 测试通过 |
| 敏感信息保护 | API Key 和密码不暴露 |

---

## 13. 附录

### 13.1 测试命名规范

```
test_<被测方法>_<场景>_<预期结果>

示例：
- test_validate_select_statement_returns_sql
- test_validate_insert_statement_raises_unsafe_error
- test_execute_query_with_timeout_raises_timeout_error
```

### 13.2 断言最佳实践

```python
# 推荐：具体断言
assert response.success is True
assert response.error_code == ErrorCode.SQL_UNSAFE.value
assert "多条" in str(exc.value)

# 避免：模糊断言
assert response  # 不够具体
assert response.success  # 应使用 is True
```

### 13.3 异步测试模式

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test an async function."""
    result = await some_async_function()
    assert result is not None
```

---

## 14. 快速验证指南

### 14.1 运行所有测试

```bash
cd w5/pg-mcp

# 运行所有测试
uv run pytest tests/ -v

# 带覆盖率报告
uv run pytest tests/ --cov=pg_mcp --cov-report=term-missing
```

### 14.2 验证测试通过

预期输出：

```
============================= 125 passed in X.XXs ==============================
```

### 14.3 验证覆盖率

预期覆盖率 ≥ 79%：

```
TOTAL                                     734    123    176     26    79%
```

### 14.4 现有测试文件清单

| 文件 | 测试数 | 描述 |
|------|--------|------|
| `tests/test_models.py` | 16 | 数据模型单元测试 |
| `tests/test_config.py` | 13 | 配置加载单元测试 |
| `tests/test_validator.py` | 26 | SQL 校验器单元测试 |
| `tests/test_database.py` | 24 | 数据库服务集成测试 (Mock) |
| `tests/test_llm.py` | 26 | LLM 服务集成测试 (Mock) |
| `tests/test_query_service.py` | 5 | 查询服务集成测试 |
| `tests/test_server.py` | 15 | MCP 服务器测试 |

---

## 15. 修订历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-01-24 | 初始版本 |
| 1.1 | 2026-01-24 | 添加实际测试状态和快速验证指南 |
