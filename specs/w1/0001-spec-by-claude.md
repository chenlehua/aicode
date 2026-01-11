# Ticket 标签管理系统 - 需求与设计文档

## 1. 项目概述

### 1.1 项目背景
构建一个简单的 Ticket 管理工具，支持通过标签对 Ticket 进行分类和管理。

### 1.2 技术栈
- **数据库**: PostgreSQL
- **后端**: Python FastAPI
- **前端**: TypeScript + Vite + Tailwind CSS + Shadcn/ui

### 1.3 核心特性
- 无用户系统（单用户模式）
- Ticket 的 CRUD 操作
- 标签管理
- 按标签筛选
- 标题搜索

---

## 2. 功能需求

### 2.1 Ticket 管理

#### 2.1.1 创建 Ticket
- 用户可以创建新的 Ticket
- 必填字段：标题（title）
- 可选字段：描述（description）、标签（tags）
- 创建时自动记录创建时间
- 默认状态为「未完成」

#### 2.1.2 编辑 Ticket
- 用户可以修改 Ticket 的标题、描述
- 用户可以添加或移除 Ticket 的标签
- 自动记录更新时间

#### 2.1.3 删除 Ticket
- 用户可以删除 Ticket
- 删除操作需要确认
- 删除后同时清除该 Ticket 与标签的关联关系

#### 2.1.4 完成/取消完成 Ticket
- 用户可以将 Ticket 标记为「已完成」
- 用户可以将已完成的 Ticket 恢复为「未完成」
- 记录完成时间

### 2.2 标签管理

#### 2.2.1 创建标签
- 用户可以创建新标签
- 标签名称必填且唯一
- 可选设置标签颜色

#### 2.2.2 删除标签
- 用户可以删除标签
- 删除标签时自动解除与所有 Ticket 的关联

### 2.3 查询与筛选

#### 2.3.1 按标签筛选
- 用户可以选择一个或多个标签进行筛选
- 显示包含所选标签的 Ticket 列表

#### 2.3.2 按标题搜索
- 用户可以输入关键词搜索 Ticket
- 支持模糊匹配标题

#### 2.3.3 列表展示
- 默认显示所有 Ticket
- 支持按状态（已完成/未完成）筛选
- 按创建时间倒序排列

---

## 3. 数据模型设计

### 3.1 数据库表结构

#### 3.1.1 tickets 表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 主键 |
| title | VARCHAR(255) | NOT NULL | 标题 |
| description | TEXT | NULLABLE | 描述 |
| is_completed | BOOLEAN | DEFAULT FALSE | 是否完成 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |
| completed_at | TIMESTAMP | NULLABLE | 完成时间 |

#### 3.1.2 tags 表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 主键 |
| name | VARCHAR(50) | NOT NULL, UNIQUE | 标签名称 |
| color | VARCHAR(7) | DEFAULT '#6B7280' | 颜色（十六进制） |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

#### 3.1.3 ticket_tags 表（关联表）
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| ticket_id | UUID | FOREIGN KEY | Ticket ID |
| tag_id | UUID | FOREIGN KEY | Tag ID |
| PRIMARY KEY | (ticket_id, tag_id) | | 联合主键 |

### 3.2 实体关系
- Ticket 与 Tag 为多对多关系
- 通过 ticket_tags 关联表实现

---

## 4. API 设计

### 4.1 Ticket 接口

#### GET /api/tickets
获取 Ticket 列表
- 查询参数：
  - `search`: 搜索关键词（可选）
  - `tag_ids`: 标签 ID 列表（可选）
  - `is_completed`: 完成状态（可选）
- 响应：Ticket 列表（包含关联标签）

#### POST /api/tickets
创建 Ticket
- 请求体：
  ```json
  {
    "title": "string",
    "description": "string | null",
    "tag_ids": ["uuid"]
  }
  ```
- 响应：创建的 Ticket

#### GET /api/tickets/{id}
获取单个 Ticket 详情
- 响应：Ticket 详情（包含关联标签）

#### PUT /api/tickets/{id}
更新 Ticket
- 请求体：
  ```json
  {
    "title": "string",
    "description": "string | null",
    "tag_ids": ["uuid"]
  }
  ```
- 响应：更新后的 Ticket

#### PATCH /api/tickets/{id}/complete
切换 Ticket 完成状态
- 响应：更新后的 Ticket

#### DELETE /api/tickets/{id}
删除 Ticket
- 响应：204 No Content

### 4.2 标签接口

#### GET /api/tags
获取所有标签
- 响应：标签列表

#### POST /api/tags
创建标签
- 请求体：
  ```json
  {
    "name": "string",
    "color": "string | null"
  }
  ```
- 响应：创建的标签

#### DELETE /api/tags/{id}
删除标签
- 响应：204 No Content

---

## 5. 前端设计

### 5.1 页面结构

#### 5.1.1 主页面布局
```
+----------------------------------+
|            Header                |
+--------+-------------------------+
|        |                         |
| 侧边栏  |      Ticket 列表        |
| (标签)  |                         |
|        |                         |
+--------+-------------------------+
```

#### 5.1.2 侧边栏
- 标签列表
- 标签筛选（多选）
- 新建标签按钮
- 标签删除操作

#### 5.1.3 主内容区
- 搜索框
- 状态筛选（全部/未完成/已完成）
- 新建 Ticket 按钮
- Ticket 卡片列表

### 5.2 组件设计

#### 5.2.1 TicketCard 组件
- 显示标题、描述预览
- 显示关联标签（Badge 形式）
- 完成状态切换按钮
- 编辑/删除操作菜单

#### 5.2.2 TicketForm 组件
- 标题输入框
- 描述文本域
- 标签选择器（多选）
- 提交/取消按钮

#### 5.2.3 TagBadge 组件
- 显示标签名称
- 根据设置显示颜色

#### 5.2.4 TagSelector 组件
- 标签多选下拉框
- 支持搜索标签

### 5.3 交互设计

#### 5.3.1 创建/编辑 Ticket
- 点击按钮弹出 Dialog
- 表单验证（标题必填）
- 提交后关闭并刷新列表

#### 5.3.2 删除确认
- 弹出确认 Dialog
- 显示警告信息
- 确认后执行删除

#### 5.3.3 实时筛选
- 搜索框输入时防抖（300ms）
- 标签/状态筛选立即生效

---

## 6. 项目结构

### 6.1 后端结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   │   ├── ticket.py
│   │   └── tag.py
│   ├── schemas/             # Pydantic 模式
│   │   ├── ticket.py
│   │   └── tag.py
│   ├── routers/             # API 路由
│   │   ├── tickets.py
│   │   └── tags.py
│   └── services/            # 业务逻辑
│       ├── ticket_service.py
│       └── tag_service.py
├── alembic/                 # 数据库迁移
├── requirements.txt
└── pyproject.toml
```

### 6.2 前端结构
```
frontend/
├── src/
│   ├── main.tsx             # 应用入口
│   ├── App.tsx              # 根组件
│   ├── components/
│   │   ├── ui/              # Shadcn 组件
│   │   ├── layout/          # 布局组件
│   │   │   ├── Header.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── tickets/         # Ticket 相关组件
│   │   │   ├── TicketCard.tsx
│   │   │   ├── TicketForm.tsx
│   │   │   └── TicketList.tsx
│   │   └── tags/            # Tag 相关组件
│   │       ├── TagBadge.tsx
│   │       └── TagSelector.tsx
│   ├── hooks/               # 自定义 Hooks
│   │   ├── useTickets.ts
│   │   └── useTags.ts
│   ├── types/               # TypeScript 类型定义
│   │   └── index.ts
│   └── lib/                 # 工具函数
│       └── api.ts           # API 客户端
├── index.html
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

---

## 7. 非功能需求

### 7.1 性能
- 列表加载时间 < 500ms
- 前端防抖搜索减少请求

### 7.2 可用性
- 响应式设计，支持移动端
- 操作反馈（loading 状态、toast 提示）

### 7.3 数据安全
- 输入验证防止 SQL 注入
- API 参数校验

---

## 8. 部署方案

### 8.1 开发环境
- PostgreSQL 本地实例或 Docker
- 后端：uvicorn 热重载
- 前端：vite dev server

### 8.2 生产环境
- Docker Compose 编排
- 后端：gunicorn + uvicorn workers
- 前端：nginx 静态文件服务
- PostgreSQL 容器或云数据库
