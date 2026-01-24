# PostgreSQL MCP Server 产品需求文档 (PRD)

## 1. 概述

### 1.1 项目背景

构建一个基于 Python 的 MCP (Model Context Protocol) 服务器，允许用户通过自然语言描述查询需求，系统自动生成 SQL 并执行查询。该服务器将作为 AI 助手与 PostgreSQL 数据库之间的桥梁，实现智能化的数据库查询功能。

### 1.2 目标用户

- 使用 Claude Desktop 或其他支持 MCP 协议的 AI 客户端的用户
- 需要通过自然语言查询 PostgreSQL 数据库的开发者和数据分析师
- 不熟悉 SQL 语法但需要获取数据库信息的业务人员

### 1.3 核心价值

- **降低使用门槛**：用户无需掌握 SQL 语法即可查询数据库
- **提高安全性**：只允许执行查询语句，防止数据修改或删除
- **智能验证**：通过 LLM 验证查询结果的有意义性
- **灵活输出**：支持返回 SQL 语句或查询结果两种模式

---

## 2. 功能需求

### 2.1 MCP 服务器初始化

#### 2.1.1 数据库发现与连接

**需求描述**：
- 服务器启动时，读取配置文件或环境变量获取可访问的数据库连接信息
- 支持配置多个 PostgreSQL 数据库连接
- 每个数据库连接应包含：主机、端口、数据库名、用户名、密码等信息

**配置示例**：
```yaml
databases:
  - name: "production_db"
    host: "localhost"
    port: 5432
    database: "myapp"
    user: "readonly_user"
    password: "${PG_PASSWORD}"  # 支持环境变量引用

  - name: "analytics_db"
    host: "analytics.example.com"
    port: 5432
    database: "analytics"
    user: "analyst"
    password: "${ANALYTICS_PASSWORD}"
```

#### 2.1.2 Schema 缓存

**需求描述**：
- 服务器启动时自动获取并缓存所有已配置数据库的 schema 信息
- 需要缓存的元数据包括：
  - **Tables（表）**：表名、列名、列类型、约束（主键、外键、唯一约束等）、列注释
  - **Views（视图）**：视图名、视图定义、列信息
  - **Types（自定义类型）**：枚举类型、复合类型等
  - **Indexes（索引）**：索引名、索引类型、索引列
  - **Functions（函数）**：函数名、参数、返回类型（可选）
  - **表关系**：外键关系图，用于理解表之间的关联

**缓存策略**：
- 启动时进行完整缓存
- 提供手动刷新缓存的 MCP Tool
- 可选：支持定时自动刷新（配置项）

**Schema 信息用途**：
- 作为 LLM 生成 SQL 的上下文信息
- 帮助 LLM 理解表结构和表关系
- 用于验证生成的 SQL 是否引用了正确的表和列

---

### 2.2 自然语言查询处理

#### 2.2.1 用户输入接收

**需求描述**：
- 通过 MCP Tool 接收用户的自然语言查询请求
- 用户只需提供查询需求描述（自然语言）
- 系统自动处理 SQL 生成、执行和结果验证

**MCP Tool 定义示例**：
```
Tool: query
Description: 根据自然语言描述查询数据库

Parameters:
  - query: string (required) - 自然语言查询描述
```

#### 2.2.2 LLM SQL 生成

**需求描述**：
- 使用阿里通义千问模型（Qwen）生成 SQL（通过 OpenAI 兼容 API）
- API 密钥通过环境变量 `LLM_API_KEY` 获取
- 构建包含以下信息的 Prompt：
  - 目标数据库的完整 Schema 信息
  - 用户的自然语言查询需求
  - SQL 生成规则和约束

**Prompt 构建要点**：
- 明确指示只生成 SELECT 查询语句
- 提供表结构和表关系信息
- 包含常见的查询模式示例
- 要求输出可直接执行的 SQL

**LLM 调用配置**：
- 模型选择：`qwen-plus` 或 `qwen-turbo`（可配置）
- Temperature：较低值（如 0.1-0.3）以确保输出稳定性
- 超时设置：合理的请求超时时间

---

### 2.3 SQL 安全校验

#### 2.3.1 查询语句限制

**需求描述**：
- 只允许执行 SELECT 查询语句
- 禁止以下类型的 SQL 操作：
  - `INSERT`, `UPDATE`, `DELETE` - 数据修改
  - `DROP`, `CREATE`, `ALTER`, `TRUNCATE` - DDL 操作
  - `GRANT`, `REVOKE` - 权限操作
  - `COPY` - 文件操作
  - `EXECUTE`, `CALL` - 存储过程调用
  - 事务控制语句：`BEGIN`, `COMMIT`, `ROLLBACK`

**校验方式**：
- SQL 语法解析（使用 SQLGlot 库，支持完整 AST 解析）
- 通过 AST 节点类型判断语句类型（如 `sqlglot.exp.Select`）
- 确保只有单条 SELECT 语句（禁止多语句执行）

#### 2.3.2 注入防护

**需求描述**：
- 防止 SQL 注入攻击
- 即使 LLM 生成了恶意 SQL，也应被安全层拦截
- 验证表名和列名是否存在于已缓存的 Schema 中（可选的额外安全层）

---

### 2.4 SQL 执行与验证

#### 2.4.1 SQL 执行

**需求描述**：
- 使用只读连接执行 SQL 查询
- 设置合理的查询超时时间（可配置，默认 30 秒）
- 限制返回结果行数（基于用户请求或默认值）
- 捕获并处理执行错误

**执行策略**：
- 使用 PostgreSQL 的 `statement_timeout` 参数限制查询时间
- 自动为无 LIMIT 的查询添加结果限制
- 使用连接池管理数据库连接

#### 2.4.2 结果验证（LLM 验证）

**需求描述**：
- 执行成功后，使用 LLM 验证结果是否有意义
- 验证内容包括：
  - 查询结果是否与用户意图匹配
  - 结果是否看起来合理（非空、非异常值等）
  - 如果结果为空，判断是数据问题还是 SQL 问题

**验证 Prompt 构建**：
- 包含用户原始查询需求
- 包含生成的 SQL 语句
- 包含查询结果的样本数据（前 N 行）
- 请求 LLM 评估结果的有效性

**验证输出**：
- 验证通过：正常返回结果
- 验证失败：返回问题说明，建议用户修改查询或提供更多上下文

---

### 2.5 结果返回

#### 2.5.1 返回格式

**返回内容**：
- 生成的 SQL 语句
- 执行查询结果（结构化 JSON 格式）
- 结果验证信息
- 包含元信息：列名、行数、执行时间等

**返回结构示例**：
```json
{
  "success": true,
  "sql": "SELECT name, email FROM users WHERE created_at > '2024-01-01' LIMIT 100",
  "result": {
    "columns": ["name", "email"],
    "rows": [
      ["Alice", "alice@example.com"],
      ["Bob", "bob@example.com"]
    ],
    "row_count": 2,
    "execution_time_ms": 45
  },
  "validation": {
    "passed": true,
    "message": "查询结果与用户意图匹配，返回了2024年1月后注册的用户信息"
  }
}
```

#### 2.5.2 错误处理

**错误类型与返回**：
- SQL 生成失败：返回错误原因，建议用户提供更清晰的查询描述
- SQL 安全校验失败：返回被拒绝的原因
- SQL 执行失败：返回数据库错误信息
- 超时错误：返回超时提示，建议优化查询
- LLM 验证失败：返回验证问题说明

---

## 3. MCP 接口设计

### 3.1 Tools（工具）

#### Tool: `query`

**描述**：根据自然语言描述查询数据库

**参数**：
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| query | string | 是 | 自然语言查询描述 |

**返回**：
- 生成的 SQL 语句
- 查询结果（结构化 JSON 格式）
- 结果验证信息

---

## 4. 非功能需求

### 4.1 性能要求

- Schema 缓存加载时间：单个数据库 < 5 秒
- SQL 生成响应时间：< 10 秒
- SQL 执行超时：可配置，默认 30 秒
- 并发支持：支持多个并发查询请求

### 4.2 安全要求

- 只读访问：MCP 服务器应使用只读数据库账户
- SQL 注入防护：严格的 SQL 校验
- 凭证保护：敏感信息不应出现在日志或返回信息中
- 连接加密：支持 SSL/TLS 数据库连接

### 4.3 可靠性要求

- 错误恢复：单个查询失败不影响服务器运行
- 连接管理：自动重连断开的数据库连接
- 日志记录：完整的操作日志用于调试和审计

### 4.4 可配置性

- 数据库连接信息
- LLM 模型选择和参数
- 超时设置
- 结果限制
- 日志级别

---

## 5. 技术约束

### 5.1 技术栈

- **运行时**：Python 3.10+
- **MCP 框架**：mcp (官方 Python SDK)
- **数据库驱动**：asyncpg 或 psycopg2
- **LLM 调用**：OpenAI SDK（兼容阿里云 DashScope API）
- **SQL 解析**：SQLGlot
- **配置管理**：pydantic-settings

### 5.2 环境变量

| 变量名 | 必填 | 描述 |
|--------|------|------|
| LLM_API_KEY | 是 | LLM API 密钥（支持 DashScope、OpenAI 等） |
| LLM_BASE_URL | 否 | LLM API 地址（默认使用 DashScope 兼容端点） |
| LLM_MODEL | 否 | LLM 模型名称（默认 qwen-plus） |
| PG_MCP_CONFIG_PATH | 否 | 配置文件路径 |
| PG_MCP_LOG_LEVEL | 否 | 日志级别 (DEBUG/INFO/WARNING/ERROR) |

### 5.3 依赖项

```
mcp>=1.0.0
asyncpg>=0.29.0
openai>=1.0.0
sqlglot>=20.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pyyaml>=6.0.0
```

---

## 6. 用户场景示例

### 场景 1：简单查询

**用户输入**：
```
查询最近一个月注册的用户数量
```

**系统处理**：
1. 解析用户意图
2. 根据 Schema 识别 `users` 表和 `created_at` 字段
3. 生成 SQL：`SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '1 month'`
4. 校验 SQL 安全性
5. 执行查询
6. 验证结果有效性
7. 返回结果

### 场景 2：关联查询

**用户输入**：
```
查询每个部门的员工人数，并按人数降序排列
```

**系统处理**：
1. 识别涉及 `departments` 和 `employees` 表
2. 根据 Schema 中的外键关系生成 JOIN 查询
3. 生成 SQL：
   ```sql
   SELECT d.name AS department_name, COUNT(e.id) AS employee_count
   FROM departments d
   LEFT JOIN employees e ON d.id = e.department_id
   GROUP BY d.id, d.name
   ORDER BY employee_count DESC
   ```
4. 执行并返回结果

---

## 7. 后续扩展（Out of Scope）

以下功能不在当前版本范围内，但可作为后续迭代考虑：

- [ ] 支持 MySQL、SQLite 等其他数据库
- [ ] 查询历史记录和收藏
- [ ] 自然语言到图表的可视化
- [ ] 多轮对话优化查询
- [ ] 查询模板保存和复用
- [ ] 权限细粒度控制（表级、列级）

---

## 8. 验收标准

### 8.1 功能验收

- [ ] MCP 服务器可正常启动并注册到 MCP 客户端
- [ ] 可成功获取并缓存数据库 Schema
- [ ] 可通过自然语言生成正确的 SQL
- [ ] SQL 安全校验可拦截非 SELECT 语句
- [ ] 可成功执行查询并返回结果
- [ ] 返回结果包含 SQL 语句和查询结果
- [ ] LLM 验证可正确评估结果有效性

### 8.2 性能验收

- [ ] Schema 缓存加载时间符合要求
- [ ] SQL 生成响应时间符合要求
- [ ] 可处理并发请求

### 8.3 安全验收

- [ ] 无法执行 INSERT/UPDATE/DELETE 等修改操作
- [ ] 无法执行 DDL 语句
- [ ] SQL 注入测试通过

---

## 9. 附录

### 9.1 参考资料

- [MCP (Model Context Protocol) 规范](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [阿里云 DashScope API 文档](https://help.aliyun.com/zh/dashscope/)
- [PostgreSQL Information Schema](https://www.postgresql.org/docs/current/information-schema.html)

### 9.2 术语表

| 术语 | 说明 |
|------|------|
| MCP | Model Context Protocol，模型上下文协议 |
| Schema | 数据库结构元数据，包括表、列、索引等信息 |
| Tool | MCP 中的工具概念，允许 AI 调用执行特定功能 |
| Resource | MCP 中的资源概念，提供数据访问能力 |
| DashScope | 阿里云的大模型服务平台 |

---

## 10. 修订历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| 1.0 | 2026-01-24 | - | 初始版本 |
