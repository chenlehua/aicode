# Ticket 标签管理系统 - 实现计划

基于 [0001-spec-by-claude.md](0001-spec-by-claude.md) 需求文档

---

## 阶段一：项目初始化与环境搭建

### 1.1 后端项目初始化
- [ ] 创建 `backend/` 目录结构
- [ ] 初始化 Python 项目（pyproject.toml 或 requirements.txt）
- [ ] 安装依赖：
  - fastapi
  - uvicorn
  - sqlalchemy
  - asyncpg（PostgreSQL 异步驱动）
  - alembic（数据库迁移）
  - pydantic
  - python-dotenv
- [ ] 配置 `.env` 文件模板（数据库连接等）

### 1.2 前端项目初始化
- [ ] 使用 Vite 创建 TypeScript + React 项目
- [ ] 安装并配置 Tailwind CSS
- [ ] 安装并配置 Shadcn/ui
- [ ] 安装额外依赖：
  - axios（HTTP 客户端）
  - @tanstack/react-query（数据请求管理）
- [ ] 配置代理（vite.config.ts）解决跨域问题

### 1.3 数据库准备
- [ ] 创建 PostgreSQL 数据库
- [ ] 配置 Alembic 迁移环境
- [ ] 创建初始迁移脚本

---

## 阶段二：后端核心实现

### 2.1 数据库模型层
- [ ] 创建 `app/database.py`：数据库连接配置
- [ ] 创建 `app/models/tag.py`：Tag 模型
  - id (UUID, 主键)
  - name (VARCHAR(50), 非空, 唯一)
  - color (VARCHAR(7), 默认 '#6B7280')
  - created_at (TIMESTAMP)
- [ ] 创建 `app/models/ticket.py`：Ticket 模型
  - id (UUID, 主键)
  - title (VARCHAR(255), 非空)
  - description (TEXT, 可空)
  - is_completed (BOOLEAN, 默认 False)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)
  - completed_at (TIMESTAMP, 可空)
- [ ] 创建 `ticket_tags` 关联表
- [ ] 生成并执行数据库迁移

### 2.2 Pydantic Schema 定义
- [ ] 创建 `app/schemas/tag.py`：
  - TagCreate：创建标签请求
  - TagResponse：标签响应
- [ ] 创建 `app/schemas/ticket.py`：
  - TicketCreate：创建 Ticket 请求
  - TicketUpdate：更新 Ticket 请求
  - TicketResponse：Ticket 响应（包含关联标签）
  - TicketListParams：列表查询参数

### 2.3 业务服务层
- [ ] 创建 `app/services/tag_service.py`：
  - get_all_tags()：获取所有标签
  - create_tag()：创建标签
  - delete_tag()：删除标签（级联解除关联）
- [ ] 创建 `app/services/ticket_service.py`：
  - get_tickets()：获取 Ticket 列表（支持搜索、筛选）
  - get_ticket_by_id()：获取单个 Ticket
  - create_ticket()：创建 Ticket
  - update_ticket()：更新 Ticket
  - toggle_complete()：切换完成状态
  - delete_ticket()：删除 Ticket

### 2.4 API 路由层
- [ ] 创建 `app/routers/tags.py`：
  - GET /api/tags
  - POST /api/tags
  - DELETE /api/tags/{id}
- [ ] 创建 `app/routers/tickets.py`：
  - GET /api/tickets
  - POST /api/tickets
  - GET /api/tickets/{id}
  - PUT /api/tickets/{id}
  - PATCH /api/tickets/{id}/complete
  - DELETE /api/tickets/{id}

### 2.5 应用入口
- [ ] 创建 `app/main.py`：
  - FastAPI 应用实例
  - 注册路由
  - 配置 CORS
  - 启动/关闭事件（数据库连接）

---

## 阶段三：前端核心实现

### 3.1 类型定义与 API 客户端
- [ ] 创建 `src/types/index.ts`：
  - Tag 类型
  - Ticket 类型
  - API 请求/响应类型
- [ ] 创建 `src/lib/api.ts`：
  - axios 实例配置
  - Ticket API 方法
  - Tag API 方法

### 3.2 自定义 Hooks
- [ ] 创建 `src/hooks/useTags.ts`：
  - useQuery 获取标签列表
  - useMutation 创建/删除标签
- [ ] 创建 `src/hooks/useTickets.ts`：
  - useQuery 获取 Ticket 列表（支持参数）
  - useMutation 创建/更新/删除/切换完成状态

### 3.3 UI 基础组件（Shadcn/ui）
- [ ] 安装所需 Shadcn 组件：
  - Button
  - Input
  - Textarea
  - Dialog
  - Badge
  - Card
  - Checkbox
  - DropdownMenu
  - Popover
  - Toast

### 3.4 布局组件
- [ ] 创建 `src/components/layout/Header.tsx`：
  - 应用标题
  - 新建 Ticket 按钮
- [ ] 创建 `src/components/layout/Sidebar.tsx`：
  - 标签列表展示
  - 标签筛选（多选 Checkbox）
  - 新建标签按钮
  - 标签删除操作
- [ ] 创建 `src/components/layout/MainLayout.tsx`：
  - 整体页面布局结构

### 3.5 标签相关组件
- [ ] 创建 `src/components/tags/TagBadge.tsx`：
  - 显示标签名称和颜色
- [ ] 创建 `src/components/tags/TagSelector.tsx`：
  - 标签多选下拉组件
  - 支持搜索过滤
- [ ] 创建 `src/components/tags/TagForm.tsx`：
  - 创建标签表单（名称、颜色选择）

### 3.6 Ticket 相关组件
- [ ] 创建 `src/components/tickets/TicketCard.tsx`：
  - 显示标题、描述预览
  - 显示关联标签（TagBadge）
  - 完成状态切换（Checkbox）
  - 更多操作菜单（编辑、删除）
- [ ] 创建 `src/components/tickets/TicketForm.tsx`：
  - 标题输入（必填验证）
  - 描述输入
  - 标签选择器
  - 提交/取消按钮
- [ ] 创建 `src/components/tickets/TicketList.tsx`：
  - 遍历渲染 TicketCard
  - 空状态提示
  - 加载状态

### 3.7 筛选与搜索组件
- [ ] 创建 `src/components/filters/SearchInput.tsx`：
  - 搜索输入框
  - 防抖处理（300ms）
- [ ] 创建 `src/components/filters/StatusFilter.tsx`：
  - 状态筛选（全部/未完成/已完成）

### 3.8 对话框组件
- [ ] 创建 `src/components/dialogs/TicketDialog.tsx`：
  - 创建/编辑 Ticket 对话框
- [ ] 创建 `src/components/dialogs/TagDialog.tsx`：
  - 创建标签对话框
- [ ] 创建 `src/components/dialogs/ConfirmDialog.tsx`：
  - 删除确认对话框

---

## 阶段四：页面整合

### 4.1 主页面
- [ ] 创建 `src/pages/HomePage.tsx`：
  - 整合 MainLayout
  - 状态管理（搜索词、标签筛选、状态筛选）
  - 连接 useTickets 获取数据
  - 处理创建/编辑/删除操作

### 4.2 应用根组件
- [ ] 更新 `src/App.tsx`：
  - 配置 QueryClientProvider
  - 配置 Toaster（toast 提示）
  - 渲染 HomePage

---

## 阶段五：功能完善与优化

### 5.1 用户体验优化
- [ ] 添加 Loading 状态展示
- [ ] 添加操作成功/失败 Toast 提示
- [ ] 添加表单验证错误提示
- [ ] 添加空状态占位图/提示

### 5.2 响应式设计
- [ ] 移动端侧边栏适配（可折叠/抽屉式）
- [ ] Ticket 卡片响应式布局
- [ ] 对话框移动端适配

### 5.3 错误处理
- [ ] API 请求错误统一处理
- [ ] 网络错误提示
- [ ] 404/500 错误页面

---

## 阶段六：测试与部署

### 6.1 后端测试
- [ ] 编写 API 集成测试
- [ ] 测试数据库操作
- [ ] 测试边界情况

### 6.2 前端测试
- [ ] 组件单元测试
- [ ] Hook 测试
- [ ] E2E 测试（可选）

### 6.3 部署配置
- [ ] 创建 Docker 配置：
  - backend/Dockerfile
  - frontend/Dockerfile
  - docker-compose.yml
- [ ] 配置 nginx（前端静态文件服务）
- [ ] 编写部署文档

---

## 实现优先级建议

| 优先级 | 内容 | 说明 |
|--------|------|------|
| P0 | 阶段一、阶段二 | 基础设施，后端 API |
| P1 | 阶段三（3.1-3.6） | 前端核心功能 |
| P2 | 阶段三（3.7-3.8）、阶段四 | 筛选功能、页面整合 |
| P3 | 阶段五 | 体验优化 |
| P4 | 阶段六 | 测试与部署 |

---

## 关键技术决策

### 状态管理
- 使用 `@tanstack/react-query` 管理服务端状态
- 使用 React `useState` 管理本地 UI 状态（筛选条件等）

### API 通信
- 使用 axios 作为 HTTP 客户端
- 开发环境通过 Vite 代理解决跨域

### 数据库访问
- 使用 SQLAlchemy 2.0 异步模式
- 使用 Alembic 管理数据库迁移

### 组件库
- 使用 Shadcn/ui 作为基础组件库
- 按需安装，保持打包体积最小

---

## 目录结构总览

```
project-root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── tag.py
│   │   │   └── ticket.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── tag.py
│   │   │   └── ticket.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── tags.py
│   │   │   └── tickets.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── tag_service.py
│   │       └── ticket_service.py
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   ├── tickets/
│   │   │   ├── tags/
│   │   │   ├── filters/
│   │   │   └── dialogs/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── lib/
│   │   └── pages/
│   ├── index.html
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
├── docker-compose.yml
└── README.md
```
