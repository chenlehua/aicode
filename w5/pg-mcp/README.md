# PostgreSQL MCP Server

一个基于 Python 的 MCP (Model Context Protocol) 服务器，支持通过自然语言查询 PostgreSQL 数据库。

## 功能特性

- **自然语言查询**：用户无需编写 SQL，通过自然语言描述即可查询数据库
- **SQL 安全校验**：只允许 SELECT 查询，自动拦截危险操作（INSERT、UPDATE、DELETE、DROP 等）
- **LLM 结果验证**：可选的 LLM 验证功能，确保查询结果符合用户意图
- **Schema 缓存**：自动缓存数据库结构，为 LLM 提供上下文信息
- **多数据库支持**：支持配置多个 PostgreSQL 数据库连接

## 技术栈

- **MCP 框架**：mcp (官方 Python SDK)
- **数据库驱动**：asyncpg (异步 PostgreSQL 驱动)
- **LLM 调用**：OpenAI SDK (兼容 DashScope/Qwen)
- **SQL 解析**：SQLGlot (AST 级别安全检查)
- **配置管理**：Pydantic Settings

## 安装

### 使用 uv (推荐)

```bash
cd w5/pg-mcp
uv sync
```

### 使用 pip

```bash
cd w5/pg-mcp
pip install -e .
```

## 配置

### 1. 创建配置文件

复制示例配置文件并修改：

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`：

```yaml
databases:
  - name: "my_database"
    host: "localhost"
    port: 5432
    database: "myapp"
    user: "readonly_user"
    password: "${PG_PASSWORD}"  # 从环境变量读取
```

### 2. 设置环境变量

```bash
# 必需
export LLM_API_KEY="your-api-key"
export PG_MCP_CONFIG_PATH="/path/to/config.yaml"

# 可选
export LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export LLM_MODEL="qwen-plus"
export PG_MCP_LOG_LEVEL="INFO"

# 数据库密码（如果在配置文件中使用 ${PG_PASSWORD}）
export PG_PASSWORD="your-db-password"
```

### 环境变量参考

| 变量名 | 必需 | 默认值 | 描述 |
|--------|------|--------|------|
| `LLM_API_KEY` | 是 | - | LLM API 密钥 |
| `LLM_BASE_URL` | 否 | DashScope 端点 | LLM API 地址 |
| `LLM_MODEL` | 否 | `qwen-plus` | 模型名称 |
| `LLM_TEMPERATURE` | 否 | `0.1` | 生成温度 |
| `LLM_TIMEOUT` | 否 | `30.0` | API 超时(秒) |
| `PG_MCP_CONFIG_PATH` | 是 | - | 数据库配置文件路径 |
| `PG_MCP_LOG_LEVEL` | 否 | `INFO` | 日志级别 |
| `QUERY_DEFAULT_LIMIT` | 否 | `100` | 默认返回行数 |
| `QUERY_STATEMENT_TIMEOUT` | 否 | `30000` | SQL 超时(毫秒) |
| `QUERY_ENABLE_VALIDATION` | 否 | `true` | 是否启用 LLM 验证 |

## 使用方式

### 启动服务器

```bash
# 使用 uv
uv run pg-mcp

# 或直接运行
python -m pg_mcp
```

### 在 Claude Desktop 中使用

编辑 Claude Desktop 配置文件：

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pg-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/pg-mcp", "pg-mcp"],
      "env": {
        "LLM_API_KEY": "your-api-key",
        "PG_MCP_CONFIG_PATH": "/path/to/config.yaml",
        "PG_PASSWORD": "your-db-password"
      }
    }
  }
}
```

## MCP 工具

### query

根据自然语言描述查询数据库。

**参数**：
- `query` (string): 自然语言查询描述

**示例**：
```
查询最近一个月注册的用户数量
```

**返回**：
```json
{
  "success": true,
  "sql": "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '1 month'",
  "result": {
    "columns": ["count"],
    "rows": [[42]],
    "row_count": 1,
    "execution_time_ms": 15.5
  },
  "validation": {
    "passed": true,
    "message": "查询结果正确返回了最近一个月的用户数量"
  }
}
```

### refresh_schema

刷新数据库 Schema 缓存。当数据库结构发生变化时使用。

### get_schema

获取当前数据库的 Schema 信息，用于了解可用的表和列。

## 安全性

- **只读查询**：只允许执行 SELECT 语句
- **SQL 注入防护**：使用 SQLGlot AST 解析进行安全检查
- **危险函数拦截**：禁止 `pg_read_file`、`dblink` 等危险函数
- **多语句拦截**：禁止执行多条 SQL 语句
- **查询超时**：可配置的 SQL 执行超时

## 开发

### 运行测试

```bash
# 安装开发依赖
uv sync --all-extras

# 运行测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov=src/pg_mcp --cov-report=html
```

### 项目结构

```
pg-mcp/
├── pyproject.toml          # 项目配置
├── config.example.yaml     # 配置文件示例
├── README.md              # 本文件
├── src/
│   └── pg_mcp/
│       ├── __init__.py
│       ├── __main__.py     # 模块入口
│       ├── server.py       # FastMCP 服务器
│       ├── config/         # 配置管理
│       ├── models/         # 数据模型
│       ├── database/       # 数据库操作
│       ├── llm/           # LLM 服务
│       ├── validator/     # SQL 校验
│       └── query/         # 查询编排
└── tests/                 # 测试文件
```

## 许可证

MIT License
