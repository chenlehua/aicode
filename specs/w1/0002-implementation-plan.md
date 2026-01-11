# Ticket 标签管理工具 - 实现计划

> 基于 [0001-spec.md](./0001-spec.md) 需求与设计文档

## 1. 项目概览

### 1.1 技术栈

- **数据库**: PostgreSQL 16
- **后端**: Python 3.11+ / FastAPI / SQLAlchemy / Alembic
- **前端**: TypeScript / Vite / React 18 / Tailwind CSS / Shadcn/ui / TanStack Query

### 1.2 开发阶段划分

| 阶段 | 内容 | 预计工时 |
|------|------|----------|
| Phase 1 | 项目初始化与环境搭建 | 2h |
| Phase 2 | 数据库设计与迁移 | 1h |
| Phase 3 | 后端 API 开发 | 4h |
| Phase 4 | 前端基础架构 | 2h |
| Phase 5 | 前端核心功能开发 | 6h |
| Phase 6 | 集成测试与优化 | 2h |
| **总计** | | **17h** |

---

## 2. Phase 1: 项目初始化与环境搭建

### 2.1 目录结构创建

```bash
w1/project-alpha/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   └── services/
│   ├── alembic/
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
└── docker-compose.yml
```

### 2.2 任务清单

#### 2.2.1 Docker 环境配置

- [ ] 创建 `docker-compose.yml`
- [ ] 配置 PostgreSQL 服务
- [ ] 验证数据库连接

#### 2.2.2 后端项目初始化

- [ ] 创建 `requirements.txt`
- [ ] 创建 Python 虚拟环境
- [ ] 安装依赖包
- [ ] 创建 `.env` 配置文件
- [ ] 创建 `app/config.py` 配置模块
- [ ] 创建 `app/database.py` 数据库连接模块
- [ ] 创建 `app/main.py` FastAPI 入口
- [ ] 配置 CORS 中间件
- [ ] 验证 FastAPI 启动

#### 2.2.3 前端项目初始化

- [ ] 使用 Vite 创建 React + TypeScript 项目
- [ ] 安装核心依赖（react-router-dom, @tanstack/react-query, axios）
- [ ] 配置 Tailwind CSS
- [ ] 初始化 Shadcn/ui
- [ ] 安装常用 Shadcn 组件（Button, Input, Card, Dialog, Checkbox, Badge 等）
- [ ] 创建基础目录结构
- [ ] 验证前端启动

### 2.3 验收标准

- Docker PostgreSQL 容器正常运行
- 后端 FastAPI 在 `http://localhost:8000` 可访问
- 前端 Vite 开发服务器在 `http://localhost:5173` 可访问

---

## 3. Phase 2: 数据库设计与迁移

### 3.1 任务清单

#### 3.1.1 Alembic 配置

- [ ] 初始化 Alembic
- [ ] 配置 `alembic.ini` 数据库连接
- [ ] 配置 `env.py` 自动检测模型变更

#### 3.1.2 SQLAlchemy Models

- [ ] 创建 `app/models/__init__.py`
- [ ] 创建 `app/models/base.py` 基础模型类
- [ ] 创建 `app/models/ticket.py` Ticket 模型
- [ ] 创建 `app/models/tag.py` Tag 模型
- [ ] 创建 `app/models/ticket_tag.py` 关联表模型

#### 3.1.3 数据库迁移

- [ ] 生成初始迁移文件
- [ ] 添加触发器函数（updated_at, completed_at）
- [ ] 执行迁移
- [ ] 验证表结构

### 3.2 模型定义

```python
# app/models/ticket.py
class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="open")
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    tags = relationship("Tag", secondary="ticket_tags", back_populates="tickets")
```

```python
# app/models/tag.py
class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), nullable=False, default="#6366f1")
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    tickets = relationship("Ticket", secondary="ticket_tags", back_populates="tags")
```

### 3.3 验收标准

- 数据库表 `tickets`, `tags`, `ticket_tags` 创建成功
- 索引创建成功
- 触发器函数正常工作

---

## 4. Phase 3: 后端 API 开发

### 4.1 任务清单

#### 4.1.1 Pydantic Schemas

- [ ] 创建 `app/schemas/__init__.py`
- [ ] 创建 `app/schemas/common.py` 通用响应模型
- [ ] 创建 `app/schemas/tag.py` 标签相关 Schema
- [ ] 创建 `app/schemas/ticket.py` Ticket 相关 Schema

#### 4.1.2 Service 层

- [ ] 创建 `app/services/__init__.py`
- [ ] 创建 `app/services/tag_service.py`
  - [ ] `get_tags()` - 获取标签列表（含 ticket_count）
  - [ ] `get_tag_by_id()` - 获取单个标签
  - [ ] `create_tag()` - 创建标签
  - [ ] `update_tag()` - 更新标签
  - [ ] `delete_tag()` - 删除标签
- [ ] 创建 `app/services/ticket_service.py`
  - [ ] `get_tickets()` - 获取 Ticket 列表（支持筛选、搜索、排序、分页）
  - [ ] `get_ticket_by_id()` - 获取单个 Ticket
  - [ ] `create_ticket()` - 创建 Ticket
  - [ ] `update_ticket()` - 更新 Ticket
  - [ ] `delete_ticket()` - 删除 Ticket
  - [ ] `complete_ticket()` - 完成 Ticket
  - [ ] `reopen_ticket()` - 取消完成 Ticket
  - [ ] `add_tags_to_ticket()` - 添加标签
  - [ ] `remove_tags_from_ticket()` - 移除标签

#### 4.1.3 Router 层

- [ ] 创建 `app/routers/__init__.py`
- [ ] 创建 `app/routers/tags.py`
  - [ ] `GET /api/v1/tags` - 获取标签列表
  - [ ] `POST /api/v1/tags` - 创建标签
  - [ ] `PUT /api/v1/tags/{tag_id}` - 更新标签
  - [ ] `DELETE /api/v1/tags/{tag_id}` - 删除标签
- [ ] 创建 `app/routers/tickets.py`
  - [ ] `GET /api/v1/tickets` - 获取 Ticket 列表
  - [ ] `GET /api/v1/tickets/{ticket_id}` - 获取单个 Ticket
  - [ ] `POST /api/v1/tickets` - 创建 Ticket
  - [ ] `PUT /api/v1/tickets/{ticket_id}` - 更新 Ticket
  - [ ] `DELETE /api/v1/tickets/{ticket_id}` - 删除 Ticket
  - [ ] `PATCH /api/v1/tickets/{ticket_id}/complete` - 完成 Ticket
  - [ ] `PATCH /api/v1/tickets/{ticket_id}/reopen` - 取消完成
  - [ ] `POST /api/v1/tickets/{ticket_id}/tags` - 添加标签
  - [ ] `DELETE /api/v1/tickets/{ticket_id}/tags` - 移除标签

#### 4.1.4 错误处理

- [ ] 创建 `app/exceptions.py` 自定义异常类
- [ ] 配置全局异常处理器
- [ ] 实现统一错误响应格式

#### 4.1.5 注册路由

- [ ] 在 `main.py` 中注册所有路由
- [ ] 配置 API 前缀 `/api/v1`

### 4.2 API 测试用例

| 接口 | 测试点 |
|------|--------|
| GET /tickets | 无筛选返回全部、tag_ids 筛选、status 筛选、search 搜索、排序、分页 |
| POST /tickets | 正常创建、标题为空报错、关联不存在的标签报错 |
| PUT /tickets/{id} | 正常更新、Ticket 不存在报 404 |
| DELETE /tickets/{id} | 正常删除、关联标签自动清除 |
| PATCH /tickets/{id}/complete | 状态变更、completed_at 自动设置 |
| PATCH /tickets/{id}/reopen | 状态变更、completed_at 自动清空 |
| POST /tickets/{id}/tags | 批量添加、重复标签忽略 |
| DELETE /tickets/{id}/tags | 批量移除、不存在标签忽略 |
| GET /tags | 返回列表含 ticket_count |
| POST /tags | 正常创建、名称重复报错 |
| PUT /tags/{id} | 正常更新 |
| DELETE /tags/{id} | 正常删除、关联 Ticket 自动解除 |

### 4.3 验收标准

- 所有 API 接口可通过 Swagger UI 测试
- 错误响应格式统一
- 数据库触发器正常工作

---

## 5. Phase 4: 前端基础架构

### 5.1 任务清单

#### 5.1.1 类型定义

- [ ] 创建 `src/types/index.ts`
  - [ ] `Tag` 接口
  - [ ] `Ticket` 接口
  - [ ] `CreateTicketInput` 接口
  - [ ] `UpdateTicketInput` 接口
  - [ ] `TicketFilters` 接口
  - [ ] `PaginatedResponse<T>` 接口

#### 5.1.2 API 客户端

- [ ] 创建 `src/lib/api.ts`
  - [ ] 配置 axios 实例（baseURL, interceptors）
  - [ ] 实现响应数据转换（snake_case → camelCase）
- [ ] 创建 `src/lib/ticketApi.ts`
  - [ ] `getTickets(filters)` - 获取列表
  - [ ] `getTicket(id)` - 获取单个
  - [ ] `createTicket(input)` - 创建
  - [ ] `updateTicket(id, input)` - 更新
  - [ ] `deleteTicket(id)` - 删除
  - [ ] `completeTicket(id)` - 完成
  - [ ] `reopenTicket(id)` - 取消完成
  - [ ] `addTagsToTicket(id, tagIds)` - 添加标签
  - [ ] `removeTagsFromTicket(id, tagIds)` - 移除标签
- [ ] 创建 `src/lib/tagApi.ts`
  - [ ] `getTags()` - 获取列表
  - [ ] `createTag(input)` - 创建
  - [ ] `updateTag(id, input)` - 更新
  - [ ] `deleteTag(id)` - 删除

#### 5.1.3 React Query Hooks

- [ ] 创建 `src/hooks/useTickets.ts`
  - [ ] `useTickets(filters)` - 查询列表
  - [ ] `useTicket(id)` - 查询单个
  - [ ] `useCreateTicket()` - 创建 mutation
  - [ ] `useUpdateTicket()` - 更新 mutation
  - [ ] `useDeleteTicket()` - 删除 mutation
  - [ ] `useCompleteTicket()` - 完成 mutation
  - [ ] `useReopenTicket()` - 取消完成 mutation
  - [ ] `useAddTagsToTicket()` - 添加标签 mutation
  - [ ] `useRemoveTagsFromTicket()` - 移除标签 mutation
- [ ] 创建 `src/hooks/useTags.ts`
  - [ ] `useTags()` - 查询列表
  - [ ] `useCreateTag()` - 创建 mutation
  - [ ] `useUpdateTag()` - 更新 mutation
  - [ ] `useDeleteTag()` - 删除 mutation
- [ ] 创建 `src/hooks/useFilters.ts`
  - [ ] 管理筛选状态（status, tagIds, search, sortBy, sortOrder）

#### 5.1.4 路由配置

- [ ] 创建 `src/App.tsx` 配置路由
- [ ] 配置 React Query Provider

#### 5.1.5 工具函数

- [ ] 创建 `src/lib/utils.ts`
  - [ ] `cn()` - className 合并函数
  - [ ] `formatDate()` - 日期格式化
  - [ ] `debounce()` - 防抖函数

### 5.2 验收标准

- API 客户端可正常请求后端接口
- React Query hooks 正常工作
- 路由配置完成

---

## 6. Phase 5: 前端核心功能开发

### 6.1 任务清单

#### 6.1.1 布局组件

- [ ] 创建 `src/components/layout/Header.tsx`
  - [ ] Logo
  - [ ] 「新建 Ticket」按钮
- [ ] 创建 `src/components/layout/Sidebar.tsx`
  - [ ] 搜索框
  - [ ] 状态筛选
  - [ ] 标签筛选
  - [ ] 新建标签按钮
- [ ] 创建 `src/components/layout/MainLayout.tsx`
  - [ ] 整合 Header + Sidebar + Main Content

#### 6.1.2 筛选组件

- [ ] 创建 `src/components/filters/StatusFilter.tsx`
  - [ ] 单选：所有 / 进行中 / 已完成
  - [ ] 选中状态高亮
- [ ] 创建 `src/components/filters/TagFilter.tsx`
  - [ ] 多选标签
  - [ ] 显示 ticket_count
  - [ ] 标签颜色显示

#### 6.1.3 标签组件

- [ ] 创建 `src/components/tags/TagBadge.tsx`
  - [ ] 显示标签名称和颜色
- [ ] 创建 `src/components/tags/TagSelector.tsx`
  - [ ] 多选标签（用于 Ticket 表单）
  - [ ] 支持快速创建新标签
- [ ] 创建 `src/components/tags/TagForm.tsx`
  - [ ] 名称输入
  - [ ] 颜色选择器
  - [ ] 表单验证
- [ ] 创建 `src/components/tags/TagList.tsx`
  - [ ] 标签管理列表
  - [ ] 编辑/删除操作

#### 6.1.4 Ticket 组件

- [ ] 创建 `src/components/tickets/TicketSearch.tsx`
  - [ ] 搜索输入框
  - [ ] 防抖处理（300ms）
- [ ] 创建 `src/components/tickets/TicketCard.tsx`
  - [ ] 显示标题、描述预览
  - [ ] 显示状态（完成/未完成）
  - [ ] 显示关联标签
  - [ ] 完成/取消完成复选框
  - [ ] 编辑/删除操作菜单
  - [ ] 已完成样式（删除线/灰色）
- [ ] 创建 `src/components/tickets/TicketList.tsx`
  - [ ] 渲染 Ticket 列表
  - [ ] Loading 状态
  - [ ] 空状态提示
  - [ ] 分页加载
- [ ] 创建 `src/components/tickets/TicketForm.tsx`
  - [ ] 标题输入（必填）
  - [ ] 描述输入
  - [ ] 标签选择
  - [ ] 表单验证
  - [ ] 新建/编辑模式

#### 6.1.5 对话框组件

- [ ] 创建 `src/components/dialogs/TicketFormDialog.tsx`
  - [ ] 新建 Ticket 对话框
  - [ ] 编辑 Ticket 对话框
- [ ] 创建 `src/components/dialogs/TagFormDialog.tsx`
  - [ ] 新建标签对话框
  - [ ] 编辑标签对话框
- [ ] 创建 `src/components/dialogs/ConfirmDialog.tsx`
  - [ ] 删除确认对话框

#### 6.1.6 Toast 通知

- [ ] 配置 Shadcn Toast
- [ ] 操作成功提示
- [ ] 操作失败提示

#### 6.1.7 页面组装

- [ ] 创建首页 `/`
  - [ ] 整合所有组件
  - [ ] 筛选状态管理
  - [ ] 响应式布局

### 6.2 组件开发顺序

```
1. 布局组件（MainLayout, Header, Sidebar）
   ↓
2. 基础组件（TagBadge, StatusFilter）
   ↓
3. 列表组件（TicketList, TicketCard）
   ↓
4. 筛选组件（TagFilter, TicketSearch）
   ↓
5. 表单组件（TicketForm, TagForm, TagSelector）
   ↓
6. 对话框组件（TicketFormDialog, TagFormDialog, ConfirmDialog）
   ↓
7. 页面整合
```

### 6.3 验收标准

- 所有功能需求实现
- 交互反馈完善（Loading, Toast）
- 响应式设计正常

---

## 7. Phase 6: 集成测试与优化

### 7.1 任务清单

#### 7.1.1 功能测试

- [ ] Ticket 创建/编辑/删除
- [ ] Ticket 完成/取消完成
- [ ] Ticket 添加/移除标签
- [ ] 标签创建/编辑/删除
- [ ] 按状态筛选
- [ ] 按标签筛选（多选）
- [ ] 按标题搜索
- [ ] 排序功能
- [ ] 分页功能

#### 7.1.2 边界情况测试

- [ ] 空列表状态
- [ ] 网络错误处理
- [ ] 表单验证错误
- [ ] 并发操作

#### 7.1.3 性能优化

- [ ] 列表虚拟滚动（如需要）
- [ ] 图片/资源懒加载
- [ ] API 请求缓存策略

#### 7.1.4 UI/UX 优化

- [ ] 移动端适配测试
- [ ] 键盘导航支持
- [ ] Loading 骨架屏

### 7.2 验收标准

- 所有功能正常工作
- 无明显 UI 问题
- 性能满足要求（首屏 < 2s）

---

## 8. 文件创建清单

### 8.1 后端文件

```
w1/project-alpha/backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── ticket.py
│   │   ├── tag.py
│   │   └── ticket_tag.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── ticket.py
│   │   └── tag.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tickets.py
│   │   └── tags.py
│   └── services/
│       ├── __init__.py
│       ├── ticket_service.py
│       └── tag_service.py
├── alembic/
│   ├── versions/
│   │   └── 001_initial.py
│   └── env.py
├── alembic.ini
├── requirements.txt
└── .env
```

### 8.2 前端文件

```
w1/project-alpha/frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   ├── tickets/
│   │   │   ├── TicketList.tsx
│   │   │   ├── TicketCard.tsx
│   │   │   ├── TicketForm.tsx
│   │   │   └── TicketSearch.tsx
│   │   ├── filters/
│   │   │   ├── StatusFilter.tsx
│   │   │   └── TagFilter.tsx
│   │   ├── tags/
│   │   │   ├── TagList.tsx
│   │   │   ├── TagBadge.tsx
│   │   │   ├── TagForm.tsx
│   │   │   └── TagSelector.tsx
│   │   ├── dialogs/
│   │   │   ├── TicketFormDialog.tsx
│   │   │   ├── TagFormDialog.tsx
│   │   │   └── ConfirmDialog.tsx
│   │   └── ui/
│   │       └── (shadcn components)
│   ├── hooks/
│   │   ├── useTickets.ts
│   │   ├── useTags.ts
│   │   └── useFilters.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── ticketApi.ts
│   │   ├── tagApi.ts
│   │   └── utils.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

## 9. 开发命令参考

### 9.1 环境启动

```bash
# 启动数据库
docker-compose up -d

# 后端开发服务器
cd w1/project-alpha/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 前端开发服务器
cd w1/project-alpha/frontend
npm run dev
```

### 9.2 数据库迁移

```bash
# 生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 9.3 Shadcn 组件安装

```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add checkbox
npx shadcn@latest add badge
npx shadcn@latest add dropdown-menu
npx shadcn@latest add toast
npx shadcn@latest add form
npx shadcn@latest add label
npx shadcn@latest add textarea
npx shadcn@latest add popover
npx shadcn@latest add command
```

---

## 10. 风险与注意事项

### 10.1 技术风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| PostgreSQL 触发器复杂性 | 调试困难 | 充分测试触发器逻辑 |
| 多标签筛选 SQL 性能 | 列表加载慢 | 添加合适索引、考虑缓存 |
| React Query 缓存失效 | 数据不一致 | 合理配置 invalidateQueries |

### 10.2 注意事项

1. **UUID 格式一致性**: 前后端 UUID 格式需保持一致
2. **时间格式**: 统一使用 ISO 8601 格式（带时区）
3. **字段命名**: 后端 snake_case，前端 camelCase，需做转换
4. **错误处理**: 所有 API 错误需统一格式返回
5. **并发安全**: 完成/取消完成操作需考虑并发情况

---

## 11. 里程碑检查点

| 检查点 | 完成标志 |
|--------|----------|
| M1: 环境就绪 | 前后端服务均可启动，数据库连接正常 |
| M2: 数据库就绪 | 所有表创建成功，触发器工作正常 |
| M3: API 就绪 | 所有接口通过 Swagger 测试 |
| M4: 前端框架就绪 | API 调用正常，路由配置完成 |
| M5: 核心功能就绪 | Ticket CRUD 功能完整可用 |
| M6: 项目完成 | 所有功能测试通过，可交付使用 |
