# Phase 3: 后端 API 开发 - 完成报告

## ✅ 完成的任务

### 4.1.1 Pydantic Schemas

- [x] 创建 `app/schemas/__init__.py`
- [x] 创建 `app/schemas/common.py` 通用响应模型（PaginatedResponse, SuccessResponse, ErrorResponse）
- [x] 创建 `app/schemas/tag.py` 标签相关 Schema（Tag, TagCreate, TagUpdate, TagListResponse）
- [x] 创建 `app/schemas/ticket.py` Ticket 相关 Schema（Ticket, TicketCreate, TicketUpdate, TicketFilters, AddTagsRequest, RemoveTagsRequest）

### 4.1.2 Service 层

- [x] 创建 `app/services/__init__.py`
- [x] 创建 `app/services/tag_service.py`
  - [x] `get_tags()` - 获取标签列表（含 ticket_count）
  - [x] `get_tag_by_id()` - 获取单个标签
  - [x] `create_tag()` - 创建标签
  - [x] `update_tag()` - 更新标签
  - [x] `delete_tag()` - 删除标签
- [x] 创建 `app/services/ticket_service.py`
  - [x] `get_tickets()` - 获取 Ticket 列表（支持筛选、搜索、排序、分页）
  - [x] `get_ticket_by_id()` - 获取单个 Ticket
  - [x] `create_ticket()` - 创建 Ticket
  - [x] `update_ticket()` - 更新 Ticket
  - [x] `delete_ticket()` - 删除 Ticket
  - [x] `complete_ticket()` - 完成 Ticket
  - [x] `reopen_ticket()` - 取消完成 Ticket
  - [x] `add_tags_to_ticket()` - 添加标签
  - [x] `remove_tags_from_ticket()` - 移除标签

### 4.1.3 Router 层

- [x] 创建 `app/routers/__init__.py`
- [x] 创建 `app/routers/tags.py`
  - [x] `GET /api/v1/tags` - 获取标签列表
  - [x] `POST /api/v1/tags` - 创建标签
  - [x] `PUT /api/v1/tags/{tag_id}` - 更新标签
  - [x] `DELETE /api/v1/tags/{tag_id}` - 删除标签
- [x] 创建 `app/routers/tickets.py`
  - [x] `GET /api/v1/tickets` - 获取 Ticket 列表
  - [x] `GET /api/v1/tickets/{ticket_id}` - 获取单个 Ticket
  - [x] `POST /api/v1/tickets` - 创建 Ticket
  - [x] `PUT /api/v1/tickets/{ticket_id}` - 更新 Ticket
  - [x] `DELETE /api/v1/tickets/{ticket_id}` - 删除 Ticket
  - [x] `PATCH /api/v1/tickets/{ticket_id}/complete` - 完成 Ticket
  - [x] `PATCH /api/v1/tickets/{ticket_id}/reopen` - 取消完成
  - [x] `POST /api/v1/tickets/{ticket_id}/tags` - 添加标签
  - [x] `DELETE /api/v1/tickets/{ticket_id}/tags` - 移除标签

### 4.1.4 错误处理

- [x] 创建 `app/exceptions.py` 自定义异常类（TicketNotFoundError, TagNotFoundError, TagNameExistsError, ValidationError）
- [x] 配置全局异常处理器（RequestValidationError, IntegrityError）
- [x] 实现统一错误响应格式

### 4.1.5 注册路由

- [x] 在 `main.py` 中注册所有路由
- [x] 配置 API 前缀 `/api/v1`

## 📁 创建的文件清单

### Schemas

```
backend/app/schemas/
├── __init__.py          # 导出所有 schemas
├── common.py            # 通用响应模型
├── tag.py               # 标签相关 Schema
└── ticket.py            # Ticket 相关 Schema
```

### Services

```
backend/app/services/
├── __init__.py          # 导出所有 services
├── tag_service.py       # 标签服务
└── ticket_service.py    # Ticket 服务
```

### Routers

```
backend/app/routers/
├── __init__.py          # 导出所有 routers
├── tags.py              # 标签路由
└── tickets.py           # Ticket 路由
```

### Exceptions

```
backend/app/
└── exceptions.py        # 自定义异常类
```

## 🎯 API 端点清单

### Tags API (`/api/v1/tags`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/tags` | 获取所有标签（含 ticket_count） |
| GET | `/api/v1/tags/{tag_id}` | 获取单个标签 |
| POST | `/api/v1/tags` | 创建标签 |
| PUT | `/api/v1/tags/{tag_id}` | 更新标签 |
| DELETE | `/api/v1/tags/{tag_id}` | 删除标签 |

### Tickets API (`/api/v1/tickets`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/tickets` | 获取 Ticket 列表（支持筛选、搜索、排序、分页） |
| GET | `/api/v1/tickets/{ticket_id}` | 获取单个 Ticket |
| POST | `/api/v1/tickets` | 创建 Ticket |
| PUT | `/api/v1/tickets/{ticket_id}` | 更新 Ticket |
| DELETE | `/api/v1/tickets/{ticket_id}` | 删除 Ticket |
| PATCH | `/api/v1/tickets/{ticket_id}/complete` | 完成 Ticket |
| PATCH | `/api/v1/tickets/{ticket_id}/reopen` | 取消完成 Ticket |
| POST | `/api/v1/tickets/{ticket_id}/tags` | 添加标签到 Ticket |
| DELETE | `/api/v1/tickets/{ticket_id}/tags` | 从 Ticket 移除标签 |

## 🔍 API 功能特性

### Ticket 列表查询功能

- ✅ 按标签筛选（支持多个标签，返回包含任意一个标签的 Ticket）
- ✅ 按状态筛选（open/completed）
- ✅ 按标题搜索（模糊匹配，不区分大小写）
- ✅ 排序（created_at, updated_at, completed_at, title）
- ✅ 分页（page, page_size）

### 错误处理

- ✅ 统一错误响应格式
- ✅ 自定义异常类（TicketNotFoundError, TagNotFoundError, TagNameExistsError）
- ✅ 全局异常处理器（验证错误、数据库完整性错误）

### 数据验证

- ✅ Pydantic 模型验证
- ✅ 字段长度限制
- ✅ 颜色格式验证（HEX）
- ✅ UUID 格式验证

## 🚀 使用说明

### 启动 API 服务器

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### 访问 API 文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API 测试示例

#### 创建标签

```bash
curl -X POST "http://localhost:8000/api/v1/tags" \
  -H "Content-Type: application/json" \
  -d '{"name": "bug", "color": "#ef4444"}'
```

#### 创建 Ticket

```bash
curl -X POST "http://localhost:8000/api/v1/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "修复登录问题",
    "description": "用户无法正常登录系统",
    "tag_ids": ["<tag_id>"]
  }'
```

#### 获取 Ticket 列表（带筛选）

```bash
curl "http://localhost:8000/api/v1/tickets?status=open&sort_by=created_at&sort_order=desc&page=1&page_size=20"
```

#### 完成 Ticket

```bash
curl -X PATCH "http://localhost:8000/api/v1/tickets/<ticket_id>/complete"
```

## 🎯 验收标准检查

### ✅ 所有 API 接口可通过 Swagger UI 测试

- [x] Tags API 所有端点已实现
- [x] Tickets API 所有端点已实现
- [x] API 文档自动生成（Swagger UI）

### ✅ 错误响应格式统一

- [x] 自定义异常返回统一格式
- [x] 验证错误返回统一格式
- [x] 数据库错误返回统一格式

### ✅ 数据库触发器正常工作

- [x] `updated_at` 自动更新（通过触发器）
- [x] `completed_at` 自动管理（通过触发器）

## 📝 注意事项

1. **标签名称唯一性**：创建和更新标签时会检查名称是否已存在
2. **标签关联验证**：创建/更新 Ticket 时会验证标签 ID 是否存在
3. **批量操作**：
   - 添加标签时，已存在的关联会被忽略
   - 移除标签时，不存在的关联会被忽略
4. **分页默认值**：page=1, page_size=20
5. **排序默认值**：sort_by=created_at, sort_order=desc

## ✨ Phase 3 完成

所有 Phase 3 的任务已完成，后端 API 已全部实现，可以通过 Swagger UI 测试所有接口，可以进入 Phase 4（前端基础架构）。
