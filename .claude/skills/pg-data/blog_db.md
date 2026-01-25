# Blog Database Schema Reference

**Database:** blog_db
**Connection:** localhost:5432, user: postgres, password: postgres

## Tables

### users
用户表，存储博客系统的用户信息

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| username | varchar | NO | | 用户名（唯一） |
| email | varchar | NO | | 邮箱（唯一） |
| password_hash | varchar | NO | | 密码哈希 |
| display_name | varchar | YES | | 显示名称 |
| bio | text | YES | | 个人简介 |
| avatar_url | varchar | YES | | 头像URL |
| status | user_status | NO | 'pending' | 用户状态 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### posts
文章表，存储博客文章

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| title | varchar | NO | | 文章标题 |
| slug | varchar | NO | | URL友好的唯一标识 |
| excerpt | text | YES | | 文章摘要 |
| content | text | NO | | 文章内容 |
| author_id | integer | NO | | 作者ID（关联users.id） |
| category_id | integer | YES | | 分类ID（关联categories.id） |
| status | post_status | NO | 'draft' | 文章状态 |
| view_count | integer | YES | 0 | 浏览次数 |
| like_count | integer | YES | 0 | 点赞数 |
| comment_count | integer | YES | 0 | 评论数 |
| is_featured | boolean | YES | false | 是否推荐 |
| is_pinned | boolean | YES | false | 是否置顶 |
| published_at | timestamptz | YES | | 发布时间 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### categories
分类表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| name | varchar | NO | | 分类名称（唯一） |
| slug | varchar | NO | | URL友好的唯一标识 |
| description | text | YES | | 分类描述 |
| parent_id | integer | YES | | 父分类ID（自关联） |
| sort_order | integer | YES | 0 | 排序顺序 |
| created_at | timestamptz | YES | now() | 创建时间 |

### tags
标签表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| name | varchar | NO | | 标签名称（唯一） |
| slug | varchar | NO | | URL友好的唯一标识 |
| color | varchar | YES | '#6B7280' | 标签颜色 |
| post_count | integer | YES | 0 | 使用该标签的文章数 |
| created_at | timestamptz | YES | now() | 创建时间 |

### post_tags
文章-标签关联表（多对多）

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| post_id | integer | NO | | 文章ID（关联posts.id） |
| tag_id | integer | NO | | 标签ID（关联tags.id） |
| created_at | timestamptz | YES | now() | 创建时间 |

**Primary Key:** (post_id, tag_id)

### comments
评论表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| post_id | integer | NO | | 文章ID（关联posts.id） |
| author_id | integer | YES | | 作者ID（关联users.id，可为空表示匿名） |
| parent_id | integer | YES | | 父评论ID（自关联，用于回复） |
| content | text | NO | | 评论内容 |
| author_name | varchar | YES | | 匿名评论者名称 |
| author_email | varchar | YES | | 匿名评论者邮箱 |
| is_approved | boolean | YES | true | 是否已审核 |
| like_count | integer | YES | 0 | 点赞数 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### bookmarks
书签/收藏表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| user_id | integer | NO | | 用户ID（关联users.id） |
| post_id | integer | NO | | 文章ID（关联posts.id） |
| created_at | timestamptz | YES | now() | 创建时间 |

**Unique:** (user_id, post_id)

### follows
关注关系表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| follower_id | integer | NO | | 关注者ID（关联users.id） |
| following_id | integer | NO | | 被关注者ID（关联users.id） |
| created_at | timestamptz | YES | now() | 创建时间 |

**Primary Key:** (follower_id, following_id)

## Enum Types

### post_status
文章状态枚举
- `draft` - 草稿
- `published` - 已发布
- `archived` - 已归档
- `deleted` - 已删除

### user_status
用户状态枚举
- `active` - 活跃
- `inactive` - 不活跃
- `banned` - 已封禁
- `pending` - 待激活

## Views

### published_posts
已发布文章视图，包含作者和分类信息

```sql
SELECT p.id, p.title, p.slug, p.excerpt, p.author_id,
       u.username AS author_username, u.display_name AS author_display_name,
       p.category_id, c.name AS category_name,
       p.view_count, p.like_count, p.comment_count,
       p.is_featured, p.is_pinned, p.published_at, p.created_at
FROM posts p
JOIN users u ON p.author_id = u.id
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.status = 'published';
```

### user_stats
用户统计视图

```sql
SELECT u.id, u.username, u.display_name, u.status,
       count(DISTINCT p.id) AS post_count,
       COALESCE(sum(p.view_count), 0) AS total_views,
       COALESCE(sum(p.like_count), 0) AS total_likes,
       (SELECT count(*) FROM follows WHERE following_id = u.id) AS follower_count,
       (SELECT count(*) FROM follows WHERE follower_id = u.id) AS following_count,
       u.created_at AS member_since
FROM users u
LEFT JOIN posts p ON u.id = p.author_id AND p.status = 'published'
GROUP BY u.id;
```

### trending_posts
热门文章视图（最近30天，按热度分数排序）

```sql
SELECT p.id, p.title, p.slug, p.author_id, u.username AS author_username,
       p.view_count, p.like_count, p.comment_count, p.published_at,
       (p.view_count * 1 + p.like_count * 5 + p.comment_count * 3) AS trending_score
FROM posts p
JOIN users u ON p.author_id = u.id
WHERE p.status = 'published' AND p.published_at > (now() - '30 days'::interval)
ORDER BY trending_score DESC;
```

## Foreign Key Relationships

| Table | Column | References |
|-------|--------|------------|
| categories | parent_id | categories.id |
| posts | author_id | users.id |
| posts | category_id | categories.id |
| post_tags | post_id | posts.id |
| post_tags | tag_id | tags.id |
| comments | post_id | posts.id |
| comments | author_id | users.id |
| comments | parent_id | comments.id |
| bookmarks | user_id | users.id |
| bookmarks | post_id | posts.id |
| follows | follower_id | users.id |
| follows | following_id | users.id |

## Common Query Patterns

### 获取用户的所有文章
```sql
SELECT * FROM posts WHERE author_id = $1 ORDER BY created_at DESC;
```

### 获取分类下的文章
```sql
SELECT * FROM posts WHERE category_id = $1 AND status = 'published' ORDER BY published_at DESC;
```

### 获取文章的所有标签
```sql
SELECT t.* FROM tags t
JOIN post_tags pt ON t.id = pt.tag_id
WHERE pt.post_id = $1;
```

### 获取用户的粉丝列表
```sql
SELECT u.* FROM users u
JOIN follows f ON u.id = f.follower_id
WHERE f.following_id = $1;
```

### 搜索文章
```sql
SELECT * FROM posts
WHERE status = 'published'
AND (title ILIKE '%keyword%' OR content ILIKE '%keyword%')
ORDER BY published_at DESC;
```
