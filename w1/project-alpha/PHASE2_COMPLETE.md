# Phase 2: 数据库设计与迁移 - 完成报告

## ✅ 完成的任务

### 3.1.1 Alembic 配置

- [x] 初始化 Alembic
- [x] 配置 `alembic.ini` 数据库连接（从 app.config 动态读取）
- [x] 配置 `env.py` 自动检测模型变更

### 3.1.2 SQLAlchemy Models

- [x] 创建 `app/models/base.py` 基础模型类
- [x] 创建 `app/models/ticket.py` Ticket 模型
- [x] 创建 `app/models/tag.py` Tag 模型
- [x] 创建 `app/models/ticket_tag.py` 关联表模型
- [x] 更新 `app/models/__init__.py` 导出所有模型

### 3.1.3 数据库迁移

- [x] 生成初始迁移文件
- [x] 添加触发器函数（updated_at, completed_at）
- [x] 添加索引（status, title, created_at, tag_id）
- [x] 执行迁移
- [x] 验证表结构

## 📁 创建的文件清单

### 模型文件

```
backend/app/models/
├── __init__.py          # 导出所有模型
├── base.py              # 基础模型类
├── ticket.py            # Ticket 模型
├── tag.py               # Tag 模型
└── ticket_tag.py        # Ticket-Tag 关联表模型
```

### Alembic 文件

```
backend/
├── alembic.ini          # Alembic 配置文件
└── alembic/
    ├── env.py           # Alembic 环境配置（已配置自动检测模型）
    ├── script.py.mako   # 迁移文件模板
    └── versions/
        └── 55edc2c3852c_initial_migration_create_tickets_tags_.py  # 初始迁移文件
```

## 🗄️ 数据库结构

### 表结构

#### tickets 表

- `id` (UUID, PRIMARY KEY)
- `title` (VARCHAR(255), NOT NULL)
- `description` (TEXT, NULLABLE)
- `status` (VARCHAR(20), NOT NULL, DEFAULT 'open', CHECK: 'open'|'completed')
- `completed_at` (TIMESTAMP WITH TIME ZONE, NULLABLE)
- `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())
- `updated_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())

#### tags 表

- `id` (UUID, PRIMARY KEY)
- `name` (VARCHAR(50), NOT NULL, UNIQUE)
- `color` (VARCHAR(7), NOT NULL, DEFAULT '#6366f1')
- `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())
- `updated_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())

#### ticket_tags 表（关联表）

- `ticket_id` (UUID, FOREIGN KEY → tickets.id, ON DELETE CASCADE)
- `tag_id` (UUID, FOREIGN KEY → tags.id, ON DELETE CASCADE)
- `created_at` (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())
- PRIMARY KEY (ticket_id, tag_id)

### 索引

1. `idx_tickets_status` - tickets(status)
2. `idx_tickets_title` - tickets(title)
3. `idx_tickets_created_at` - tickets(created_at DESC)
4. `idx_ticket_tags_tag_id` - ticket_tags(tag_id)

### 触发器函数

1. **update_updated_at_column()**
   - 自动更新 `updated_at` 字段为当前时间
   - 应用于：tickets, tags

2. **update_completed_at_column()**
   - 当 status 变为 'completed' 时，自动设置 `completed_at`
   - 当 status 从 'completed' 变为其他状态时，自动清空 `completed_at`
   - 应用于：tickets

### 触发器

1. `trigger_tickets_updated_at` - tickets 表更新时触发
2. `trigger_tickets_completed_at` - tickets 表更新时触发
3. `trigger_tags_updated_at` - tags 表更新时触发

## 🎯 验收标准检查

### ✅ 数据库表创建成功

- [x] `tickets` 表已创建
- [x] `tags` 表已创建
- [x] `ticket_tags` 关联表已创建

### ✅ 索引创建成功

- [x] `idx_tickets_status` 已创建
- [x] `idx_tickets_title` 已创建
- [x] `idx_tickets_created_at` 已创建（DESC 排序）
- [x] `idx_ticket_tags_tag_id` 已创建

### ✅ 触发器函数正常工作

- [x] `update_updated_at_column()` 函数已创建
- [x] `update_completed_at_column()` 函数已创建
- [x] 所有触发器已正确关联到表

## 🚀 使用说明

### 运行迁移

```bash
cd backend

# 升级到最新版本
uv run alembic upgrade head

# 查看当前版本
uv run alembic current

# 查看迁移历史
uv run alembic history

# 回滚到上一个版本
uv run alembic downgrade -1

# 创建新的迁移（自动检测模型变更）
uv run alembic revision --autogenerate -m "描述信息"
```

### 验证数据库结构

```bash
# 查看所有表
docker-compose exec db psql -U ticketapp -d ticketapp -c "\dt"

# 查看表结构
docker-compose exec db psql -U ticketapp -d ticketapp -c "\d tickets"
docker-compose exec db psql -U ticketapp -d ticketapp -c "\d tags"

# 查看索引
docker-compose exec db psql -U ticketapp -d ticketapp -c "SELECT indexname FROM pg_indexes WHERE tablename IN ('tickets', 'tags', 'ticket_tags');"

# 查看触发器
docker-compose exec db psql -U ticketapp -d ticketapp -c "SELECT trigger_name, event_object_table FROM information_schema.triggers WHERE trigger_schema = 'public';"
```

## 📝 注意事项

1. **模型导入顺序**：在 `env.py` 中需要导入所有模型，以便 Alembic 能够检测到它们
2. **触发器函数**：使用 `op.execute()` 在迁移文件中执行 SQL 语句创建触发器
3. **索引顺序**：`created_at` 索引使用 DESC 排序以优化按创建时间倒序查询
4. **外键级联**：`ticket_tags` 表的外键设置了 `ON DELETE CASCADE`，确保删除 ticket 或 tag 时自动清理关联关系

## ✨ Phase 2 完成

所有 Phase 2 的任务已完成，数据库表结构、索引和触发器都已正确创建，可以进入 Phase 3（后端 API 开发）。
