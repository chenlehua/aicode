# Seed Data 使用说明

## 文件说明

`seed.sql` 文件包含了用于填充数据库的示例数据：

- **35个标签**：包括平台标签、项目标签、功能标签和优先级/类型标签
- **50个Ticket**：包含20个已完成和30个进行中的tickets
- **关联关系**：每个ticket都关联了相关的标签

## 标签分类

### Platform Tags (7个)

- iOS, Android, Web, macOS, Windows, Linux, API

### Project Tags (5个)

- Viking, Phoenix, Atlas, Nexus, Aurora

### Functional Tags (15个)

- autocomplete, search, authentication, authorization, payment
- notification, analytics, caching, database, performance
- security, ui, ux, mobile, responsive

### Priority/Type Tags (8个)

- bug, feature, enhancement, urgent, blocker
- documentation, refactor, testing

## 使用方法

### 方法1: 使用 psql 直接执行

```bash
# 从项目根目录执行
cd backend/docs
psql -U ticketapp -d ticketapp -f seed.sql

# 或者使用 docker-compose
docker-compose exec db psql -U ticketapp -d ticketapp -f /path/to/seed.sql
```

### 方法2: 使用 Docker 执行

```bash
# 从项目根目录
docker-compose exec -T db psql -U ticketapp -d ticketapp < backend/docs/seed.sql
```

### 方法3: 复制到容器内执行

```bash
# 复制文件到容器
docker cp backend/docs/seed.sql ticketapp_db:/tmp/seed.sql

# 在容器内执行
docker-compose exec db psql -U ticketapp -d ticketapp -f /tmp/seed.sql
```

## 注意事项

1. **清空现有数据**：文件默认会清空现有数据（TRUNCATE 已启用）。如果需要保留现有数据，请注释掉文件开头的 TRUNCATE 语句
2. **UUID格式**：所有ID都使用固定的UUID格式，便于测试和调试
3. **时间戳**：使用相对时间（NOW() - INTERVAL），确保数据的时间顺序合理
4. **已完成tickets**：completed_at 字段会自动设置（通过触发器）
5. **执行顺序**：文件按顺序执行（tags → tickets → ticket_tags），确保外键约束正确

## 验证数据

执行seed后，可以运行以下查询验证：

```sql
-- 检查标签数量
SELECT COUNT(*) FROM tags;

-- 检查ticket数量
SELECT COUNT(*) FROM tickets;

-- 检查关联关系数量
SELECT COUNT(*) FROM ticket_tags;

-- 查看标签及其关联的ticket数量
SELECT t.name, COUNT(tt.ticket_id) as ticket_count
FROM tags t
LEFT JOIN ticket_tags tt ON t.id = tt.tag_id
GROUP BY t.id, t.name
ORDER BY ticket_count DESC;

-- 查看各状态的ticket数量
SELECT status, COUNT(*) as count
FROM tickets
GROUP BY status;
```

## 数据特点

- **有意义的标题和描述**：所有tickets都有中文标题和详细描述
- **合理的标签关联**：每个ticket都关联了相关的标签（1-4个）
- **时间分布**：tickets的创建时间分布在过去30天内
- **状态分布**：40%已完成，60%进行中
