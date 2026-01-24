-- =====================================================
-- Small Test Database: Blog System
-- 博客系统测试数据库（小型）
-- Tables: 8 | Views: 3 | Types: 2 | Indexes: 10+
-- =====================================================

-- 清理现有对象
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;

-- =====================================================
-- 自定义类型 (Custom Types)
-- =====================================================

-- 用户状态枚举
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'banned', 'pending');

-- 文章状态枚举
CREATE TYPE post_status AS ENUM ('draft', 'published', 'archived', 'deleted');

-- =====================================================
-- 表结构 (Tables)
-- =====================================================

-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url VARCHAR(255),
    status user_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE users IS '用户表 - 存储博客系统的所有用户信息';
COMMENT ON COLUMN users.username IS '用户名，唯一标识';
COMMENT ON COLUMN users.email IS '用户邮箱地址';
COMMENT ON COLUMN users.status IS '用户状态：active/inactive/banned/pending';

-- 分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE categories IS '文章分类表 - 支持层级分类';
COMMENT ON COLUMN categories.slug IS 'URL友好的分类标识符';
COMMENT ON COLUMN categories.parent_id IS '父分类ID，用于构建分类树';

-- 标签表
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE,
    slug VARCHAR(30) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#6B7280',
    post_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tags IS '标签表 - 用于文章标签';
COMMENT ON COLUMN tags.color IS '标签显示颜色（十六进制）';

-- 文章表
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    excerpt TEXT,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    status post_status NOT NULL DEFAULT 'draft',
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE posts IS '文章表 - 博客文章的主表';
COMMENT ON COLUMN posts.slug IS 'URL友好的文章标识符';
COMMENT ON COLUMN posts.excerpt IS '文章摘要';
COMMENT ON COLUMN posts.is_featured IS '是否为精选文章';

-- 文章标签关联表
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (post_id, tag_id)
);

COMMENT ON TABLE post_tags IS '文章与标签的多对多关联表';

-- 评论表
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    author_name VARCHAR(50),
    author_email VARCHAR(100),
    is_approved BOOLEAN DEFAULT TRUE,
    like_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE comments IS '评论表 - 支持嵌套评论';
COMMENT ON COLUMN comments.parent_id IS '父评论ID，用于实现评论回复';
COMMENT ON COLUMN comments.author_name IS '匿名用户的显示名称';

-- 用户收藏表
CREATE TABLE bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, post_id)
);

COMMENT ON TABLE bookmarks IS '用户收藏的文章';

-- 用户关注表
CREATE TABLE follows (
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id != following_id)
);

COMMENT ON TABLE follows IS '用户关注关系表';
COMMENT ON COLUMN follows.follower_id IS '关注者用户ID';
COMMENT ON COLUMN follows.following_id IS '被关注者用户ID';

-- =====================================================
-- 索引 (Indexes)
-- =====================================================

-- 用户表索引
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- 文章表索引
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_category_id ON posts(category_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_published_at ON posts(published_at DESC);
CREATE INDEX idx_posts_view_count ON posts(view_count DESC);
CREATE INDEX idx_posts_is_featured ON posts(is_featured) WHERE is_featured = TRUE;

-- 评论表索引
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_author_id ON comments(author_id);
CREATE INDEX idx_comments_parent_id ON comments(parent_id);
CREATE INDEX idx_comments_created_at ON comments(created_at DESC);

-- 收藏表索引
CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id);

-- =====================================================
-- 视图 (Views)
-- =====================================================

-- 已发布文章视图
CREATE VIEW published_posts AS
SELECT 
    p.id,
    p.title,
    p.slug,
    p.excerpt,
    p.author_id,
    u.username AS author_username,
    u.display_name AS author_display_name,
    p.category_id,
    c.name AS category_name,
    p.view_count,
    p.like_count,
    p.comment_count,
    p.is_featured,
    p.is_pinned,
    p.published_at,
    p.created_at
FROM posts p
JOIN users u ON p.author_id = u.id
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.status = 'published';

COMMENT ON VIEW published_posts IS '已发布文章的简化视图，包含作者和分类信息';

-- 用户统计视图
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.display_name,
    u.status,
    COUNT(DISTINCT p.id) AS post_count,
    COALESCE(SUM(p.view_count), 0) AS total_views,
    COALESCE(SUM(p.like_count), 0) AS total_likes,
    (SELECT COUNT(*) FROM follows WHERE following_id = u.id) AS follower_count,
    (SELECT COUNT(*) FROM follows WHERE follower_id = u.id) AS following_count,
    u.created_at AS member_since
FROM users u
LEFT JOIN posts p ON u.id = p.author_id AND p.status = 'published'
GROUP BY u.id;

COMMENT ON VIEW user_stats IS '用户统计信息视图';

-- 热门文章视图
CREATE VIEW trending_posts AS
SELECT 
    p.id,
    p.title,
    p.slug,
    p.author_id,
    u.username AS author_username,
    p.view_count,
    p.like_count,
    p.comment_count,
    p.published_at,
    (p.view_count * 1 + p.like_count * 5 + p.comment_count * 3) AS trending_score
FROM posts p
JOIN users u ON p.author_id = u.id
WHERE p.status = 'published'
  AND p.published_at > NOW() - INTERVAL '30 days'
ORDER BY trending_score DESC;

COMMENT ON VIEW trending_posts IS '过去30天热门文章，基于浏览、点赞、评论综合评分';

-- =====================================================
-- 函数 (Functions)
-- =====================================================

-- 更新文章评论计数的函数
CREATE OR REPLACE FUNCTION update_post_comment_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE posts SET comment_count = comment_count + 1 WHERE id = NEW.post_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE posts SET comment_count = comment_count - 1 WHERE id = OLD.post_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 评论计数触发器
CREATE TRIGGER trigger_update_comment_count
AFTER INSERT OR DELETE ON comments
FOR EACH ROW EXECUTE FUNCTION update_post_comment_count();

-- 更新标签文章计数的函数
CREATE OR REPLACE FUNCTION update_tag_post_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE tags SET post_count = post_count + 1 WHERE id = NEW.tag_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE tags SET post_count = post_count - 1 WHERE id = OLD.tag_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 标签计数触发器
CREATE TRIGGER trigger_update_tag_count
AFTER INSERT OR DELETE ON post_tags
FOR EACH ROW EXECUTE FUNCTION update_tag_post_count();
