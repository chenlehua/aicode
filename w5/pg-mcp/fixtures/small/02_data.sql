-- =====================================================
-- Small Test Database: Blog System - Test Data
-- 博客系统测试数据
-- =====================================================

-- =====================================================
-- 用户数据 (50 users)
-- =====================================================

INSERT INTO users (username, email, password_hash, display_name, bio, avatar_url, status) VALUES
('alice_dev', 'alice@example.com', '$2b$12$dummy_hash_1', 'Alice Chen', '全栈开发者，热爱技术分享', 'https://i.pravatar.cc/150?u=alice', 'active'),
('bob_writer', 'bob@example.com', '$2b$12$dummy_hash_2', 'Bob Wang', '技术写手，专注后端开发', 'https://i.pravatar.cc/150?u=bob', 'active'),
('charlie_ml', 'charlie@example.com', '$2b$12$dummy_hash_3', 'Charlie Liu', '机器学习工程师', 'https://i.pravatar.cc/150?u=charlie', 'active'),
('diana_fe', 'diana@example.com', '$2b$12$dummy_hash_4', 'Diana Zhang', '前端工程师，React 爱好者', 'https://i.pravatar.cc/150?u=diana', 'active'),
('edward_db', 'edward@example.com', '$2b$12$dummy_hash_5', 'Edward Li', '数据库专家，PostgreSQL 贡献者', 'https://i.pravatar.cc/150?u=edward', 'active'),
('fiona_sec', 'fiona@example.com', '$2b$12$dummy_hash_6', 'Fiona Huang', '安全研究员', 'https://i.pravatar.cc/150?u=fiona', 'active'),
('george_cloud', 'george@example.com', '$2b$12$dummy_hash_7', 'George Wu', '云架构师，AWS 认证专家', 'https://i.pravatar.cc/150?u=george', 'active'),
('helen_data', 'helen@example.com', '$2b$12$dummy_hash_8', 'Helen Zhao', '数据科学家', 'https://i.pravatar.cc/150?u=helen', 'active'),
('ivan_mobile', 'ivan@example.com', '$2b$12$dummy_hash_9', 'Ivan Sun', '移动开发专家', 'https://i.pravatar.cc/150?u=ivan', 'active'),
('julia_devops', 'julia@example.com', '$2b$12$dummy_hash_10', 'Julia Qian', 'DevOps 工程师', 'https://i.pravatar.cc/150?u=julia', 'active'),
('kevin_ai', 'kevin@example.com', '$2b$12$dummy_hash_11', 'Kevin Ma', 'AI 研究员', 'https://i.pravatar.cc/150?u=kevin', 'active'),
('lisa_ux', 'lisa@example.com', '$2b$12$dummy_hash_12', 'Lisa Xu', 'UX 设计师', 'https://i.pravatar.cc/150?u=lisa', 'active'),
('mike_sys', 'mike@example.com', '$2b$12$dummy_hash_13', 'Mike Yang', '系统工程师', 'https://i.pravatar.cc/150?u=mike', 'active'),
('nancy_pm', 'nancy@example.com', '$2b$12$dummy_hash_14', 'Nancy Zhou', '产品经理', 'https://i.pravatar.cc/150?u=nancy', 'active'),
('oscar_qa', 'oscar@example.com', '$2b$12$dummy_hash_15', 'Oscar Lin', '测试工程师', 'https://i.pravatar.cc/150?u=oscar', 'active'),
('patricia_arch', 'patricia@example.com', '$2b$12$dummy_hash_16', 'Patricia Jiang', '软件架构师', 'https://i.pravatar.cc/150?u=patricia', 'active'),
('quincy_go', 'quincy@example.com', '$2b$12$dummy_hash_17', 'Quincy Feng', 'Go 语言专家', 'https://i.pravatar.cc/150?u=quincy', 'active'),
('rachel_py', 'rachel@example.com', '$2b$12$dummy_hash_18', 'Rachel Deng', 'Python 开发者', 'https://i.pravatar.cc/150?u=rachel', 'active'),
('steve_rust', 'steve@example.com', '$2b$12$dummy_hash_19', 'Steve Cao', 'Rust 爱好者', 'https://i.pravatar.cc/150?u=steve', 'active'),
('tina_java', 'tina@example.com', '$2b$12$dummy_hash_20', 'Tina Luo', 'Java 架构师', 'https://i.pravatar.cc/150?u=tina', 'active'),
('user21', 'user21@example.com', '$2b$12$dummy_hash_21', 'User 21', '技术爱好者', NULL, 'active'),
('user22', 'user22@example.com', '$2b$12$dummy_hash_22', 'User 22', NULL, NULL, 'active'),
('user23', 'user23@example.com', '$2b$12$dummy_hash_23', 'User 23', NULL, NULL, 'active'),
('user24', 'user24@example.com', '$2b$12$dummy_hash_24', 'User 24', NULL, NULL, 'inactive'),
('user25', 'user25@example.com', '$2b$12$dummy_hash_25', 'User 25', NULL, NULL, 'active'),
('user26', 'user26@example.com', '$2b$12$dummy_hash_26', 'User 26', NULL, NULL, 'pending'),
('user27', 'user27@example.com', '$2b$12$dummy_hash_27', 'User 27', NULL, NULL, 'active'),
('user28', 'user28@example.com', '$2b$12$dummy_hash_28', 'User 28', NULL, NULL, 'active'),
('user29', 'user29@example.com', '$2b$12$dummy_hash_29', 'User 29', NULL, NULL, 'banned'),
('user30', 'user30@example.com', '$2b$12$dummy_hash_30', 'User 30', NULL, NULL, 'active'),
('user31', 'user31@example.com', '$2b$12$dummy_hash_31', 'User 31', NULL, NULL, 'active'),
('user32', 'user32@example.com', '$2b$12$dummy_hash_32', 'User 32', NULL, NULL, 'active'),
('user33', 'user33@example.com', '$2b$12$dummy_hash_33', 'User 33', NULL, NULL, 'active'),
('user34', 'user34@example.com', '$2b$12$dummy_hash_34', 'User 34', NULL, NULL, 'inactive'),
('user35', 'user35@example.com', '$2b$12$dummy_hash_35', 'User 35', NULL, NULL, 'active'),
('user36', 'user36@example.com', '$2b$12$dummy_hash_36', 'User 36', NULL, NULL, 'active'),
('user37', 'user37@example.com', '$2b$12$dummy_hash_37', 'User 37', NULL, NULL, 'active'),
('user38', 'user38@example.com', '$2b$12$dummy_hash_38', 'User 38', NULL, NULL, 'active'),
('user39', 'user39@example.com', '$2b$12$dummy_hash_39', 'User 39', NULL, NULL, 'pending'),
('user40', 'user40@example.com', '$2b$12$dummy_hash_40', 'User 40', NULL, NULL, 'active'),
('user41', 'user41@example.com', '$2b$12$dummy_hash_41', 'User 41', NULL, NULL, 'active'),
('user42', 'user42@example.com', '$2b$12$dummy_hash_42', 'User 42', NULL, NULL, 'active'),
('user43', 'user43@example.com', '$2b$12$dummy_hash_43', 'User 43', NULL, NULL, 'active'),
('user44', 'user44@example.com', '$2b$12$dummy_hash_44', 'User 44', NULL, NULL, 'active'),
('user45', 'user45@example.com', '$2b$12$dummy_hash_45', 'User 45', NULL, NULL, 'active'),
('user46', 'user46@example.com', '$2b$12$dummy_hash_46', 'User 46', NULL, NULL, 'active'),
('user47', 'user47@example.com', '$2b$12$dummy_hash_47', 'User 47', NULL, NULL, 'active'),
('user48', 'user48@example.com', '$2b$12$dummy_hash_48', 'User 48', NULL, NULL, 'active'),
('user49', 'user49@example.com', '$2b$12$dummy_hash_49', 'User 49', NULL, NULL, 'active'),
('user50', 'user50@example.com', '$2b$12$dummy_hash_50', 'User 50', NULL, NULL, 'active');

-- =====================================================
-- 分类数据 (10 categories)
-- =====================================================

INSERT INTO categories (name, slug, description, parent_id, sort_order) VALUES
('技术', 'tech', '技术相关文章', NULL, 1),
('前端开发', 'frontend', 'HTML, CSS, JavaScript, React, Vue 等', 1, 2),
('后端开发', 'backend', 'Node.js, Python, Java, Go 等', 1, 3),
('数据库', 'database', 'SQL, NoSQL, 数据库设计', 1, 4),
('DevOps', 'devops', '运维、CI/CD、容器化', 1, 5),
('生活', 'life', '生活感悟与分享', NULL, 6),
('旅行', 'travel', '旅行游记', 6, 7),
('读书', 'reading', '读书笔记与推荐', 6, 8),
('职业', 'career', '职业发展与规划', NULL, 9),
('开源', 'opensource', '开源项目与贡献', NULL, 10);

-- =====================================================
-- 标签数据 (20 tags)
-- =====================================================

INSERT INTO tags (name, slug, color) VALUES
('Python', 'python', '#3776AB'),
('JavaScript', 'javascript', '#F7DF1E'),
('PostgreSQL', 'postgresql', '#336791'),
('Docker', 'docker', '#2496ED'),
('Kubernetes', 'kubernetes', '#326CE5'),
('React', 'react', '#61DAFB'),
('Vue', 'vue', '#4FC08D'),
('TypeScript', 'typescript', '#3178C6'),
('Go', 'go', '#00ADD8'),
('Rust', 'rust', '#000000'),
('机器学习', 'ml', '#FF6F00'),
('深度学习', 'dl', '#EE4C2C'),
('微服务', 'microservice', '#1E88E5'),
('API设计', 'api-design', '#6DB33F'),
('性能优化', 'performance', '#FF5722'),
('安全', 'security', '#F44336'),
('测试', 'testing', '#8BC34A'),
('架构', 'architecture', '#9C27B0'),
('教程', 'tutorial', '#00BCD4'),
('最佳实践', 'best-practice', '#FFC107');

-- =====================================================
-- 文章数据 (100 posts)
-- =====================================================

INSERT INTO posts (title, slug, excerpt, content, author_id, category_id, status, view_count, like_count, is_featured, is_pinned, published_at) VALUES
('Python 异步编程入门指南', 'python-async-guide', '本文介绍 Python asyncio 的基础知识', '# Python 异步编程入门指南\n\n## 什么是异步编程？\n\n异步编程是一种并发编程模式...\n\n## asyncio 基础\n\n```python\nimport asyncio\n\nasync def main():\n    print("Hello")\n    await asyncio.sleep(1)\n    print("World")\n\nasyncio.run(main())\n```\n\n## 总结\n\n异步编程可以有效提高 I/O 密集型应用的性能。', 1, 3, 'published', 1520, 89, TRUE, TRUE, NOW() - INTERVAL '30 days'),
('PostgreSQL 性能调优实战', 'postgresql-performance-tuning', '深入了解 PostgreSQL 的性能优化技巧', '# PostgreSQL 性能调优实战\n\n## 索引优化\n\n正确使用索引是提高查询性能的关键...\n\n## 查询计划分析\n\n使用 EXPLAIN ANALYZE 分析查询计划...', 5, 4, 'published', 2340, 156, TRUE, FALSE, NOW() - INTERVAL '25 days'),
('React 18 新特性详解', 'react-18-new-features', 'React 18 带来了许多激动人心的新特性', '# React 18 新特性详解\n\n## Concurrent Mode\n\n并发模式是 React 18 的核心更新...\n\n## Automatic Batching\n\n自动批处理可以减少重渲染次数...', 4, 2, 'published', 3120, 245, TRUE, FALSE, NOW() - INTERVAL '20 days'),
('Docker 容器化最佳实践', 'docker-best-practices', '如何编写高效的 Dockerfile', '# Docker 容器化最佳实践\n\n## 多阶段构建\n\n多阶段构建可以减小镜像体积...\n\n## 安全考虑\n\n永远不要在镜像中保存敏感信息...', 10, 5, 'published', 1890, 112, FALSE, FALSE, NOW() - INTERVAL '18 days'),
('Kubernetes 入门到实践', 'kubernetes-getting-started', 'K8s 的核心概念和实践指南', '# Kubernetes 入门到实践\n\n## Pod 概念\n\nPod 是 K8s 中最小的部署单元...\n\n## Deployment 管理\n\n使用 Deployment 进行应用部署和更新...', 7, 5, 'published', 2780, 189, FALSE, FALSE, NOW() - INTERVAL '15 days'),
('TypeScript 类型系统深入', 'typescript-type-system', '掌握 TypeScript 的高级类型技巧', '# TypeScript 类型系统深入\n\n## 泛型约束\n\n泛型让代码更加灵活且类型安全...\n\n## 条件类型\n\n条件类型可以实现复杂的类型推导...', 4, 2, 'published', 1650, 98, FALSE, FALSE, NOW() - INTERVAL '12 days'),
('Go 语言并发编程', 'go-concurrency', 'Goroutine 和 Channel 的使用方法', '# Go 语言并发编程\n\n## Goroutine\n\nGoroutine 是轻量级的线程...\n\n## Channel\n\nChannel 用于 Goroutine 之间的通信...', 17, 3, 'published', 2100, 134, FALSE, FALSE, NOW() - INTERVAL '10 days'),
('微服务架构设计原则', 'microservice-design-principles', '如何设计一个好的微服务架构', '# 微服务架构设计原则\n\n## 单一职责\n\n每个服务只负责一个业务领域...\n\n## 服务间通信\n\n选择合适的通信方式：REST、gRPC、消息队列...', 16, 3, 'published', 3450, 278, TRUE, FALSE, NOW() - INTERVAL '8 days'),
('Vue 3 组合式 API 实战', 'vue3-composition-api', 'Vue 3 组合式 API 的使用场景和技巧', '# Vue 3 组合式 API 实战\n\n## setup 函数\n\nsetup 是组合式 API 的入口...\n\n## 响应式系统\n\n使用 ref 和 reactive 创建响应式数据...', 4, 2, 'published', 1980, 145, FALSE, FALSE, NOW() - INTERVAL '7 days'),
('Rust 入门：所有权系统', 'rust-ownership', '理解 Rust 独特的所有权机制', '# Rust 入门：所有权系统\n\n## 什么是所有权？\n\n所有权是 Rust 的核心特性...\n\n## 借用规则\n\n了解可变借用和不可变借用的区别...', 19, 3, 'published', 1420, 87, FALSE, FALSE, NOW() - INTERVAL '5 days');

-- 继续插入更多文章 (90 more posts)
INSERT INTO posts (title, slug, excerpt, content, author_id, category_id, status, view_count, like_count, is_featured, published_at)
SELECT 
    '技术文章 ' || generate_series || ': ' || 
    CASE (generate_series % 10)
        WHEN 0 THEN 'Python 进阶技巧'
        WHEN 1 THEN 'JavaScript 最佳实践'
        WHEN 2 THEN 'SQL 查询优化'
        WHEN 3 THEN 'API 设计模式'
        WHEN 4 THEN '容器化部署'
        WHEN 5 THEN '代码重构经验'
        WHEN 6 THEN '测试驱动开发'
        WHEN 7 THEN '性能监控方案'
        WHEN 8 THEN '安全编码实践'
        ELSE '架构设计思考'
    END,
    'article-' || generate_series,
    '这是第 ' || generate_series || ' 篇技术文章的摘要',
    '# 文章内容\n\n这是第 ' || generate_series || ' 篇技术文章的正文内容。\n\n## 章节一\n\n详细内容...\n\n## 章节二\n\n更多内容...',
    1 + (generate_series % 20),
    1 + (generate_series % 5),
    (CASE WHEN generate_series % 8 = 0 THEN 'draft' ELSE 'published' END)::post_status,
    (random() * 5000)::int,
    (random() * 300)::int,
    generate_series % 15 = 0,
    NOW() - (generate_series || ' days')::interval
FROM generate_series(11, 100);

-- =====================================================
-- 文章标签关联 (200+ associations)
-- =====================================================

-- 为前10篇文章手动设置标签
INSERT INTO post_tags (post_id, tag_id) VALUES
(1, 1), (1, 19), -- Python 异步编程
(2, 3), (2, 15), -- PostgreSQL 性能
(3, 6), (3, 8), (3, 19), -- React 18
(4, 4), (4, 20), -- Docker
(5, 5), (5, 4), (5, 13), -- Kubernetes
(6, 8), (6, 2), -- TypeScript
(7, 9), (7, 13), -- Go 并发
(8, 13), (8, 18), (8, 14), -- 微服务
(9, 7), (9, 2), (9, 19), -- Vue 3
(10, 10), (10, 18); -- Rust

-- 为其他文章随机分配标签
INSERT INTO post_tags (post_id, tag_id)
SELECT DISTINCT post_id, tag_id FROM (
    SELECT 
        generate_series AS post_id,
        1 + (floor(random() * 20))::int AS tag_id
    FROM generate_series(11, 100)
    UNION ALL
    SELECT 
        generate_series AS post_id,
        1 + (floor(random() * 20))::int AS tag_id
    FROM generate_series(11, 100)
) t
ON CONFLICT DO NOTHING;

-- =====================================================
-- 评论数据 (300+ comments)
-- =====================================================

-- 为热门文章添加评论
INSERT INTO comments (post_id, author_id, content, like_count, created_at) VALUES
(1, 2, '非常详细的教程！对 asyncio 有了更深入的理解', 15, NOW() - INTERVAL '29 days'),
(1, 3, '请问 async/await 和 threading 的区别是什么？', 8, NOW() - INTERVAL '28 days'),
(1, 1, '@charlie_ml async/await 是协程，不会创建新线程，适合 I/O 密集型任务', 12, NOW() - INTERVAL '28 days'),
(2, 1, 'PostgreSQL 的 EXPLAIN 分析非常有用', 10, NOW() - INTERVAL '24 days'),
(2, 7, '学到了很多索引优化技巧', 6, NOW() - INTERVAL '23 days'),
(3, 2, 'React 18 的并发模式太棒了！', 20, NOW() - INTERVAL '19 days'),
(3, 12, 'Suspense 在数据获取方面的应用很有意思', 15, NOW() - INTERVAL '18 days'),
(4, 7, '多阶段构建确实能显著减小镜像体积', 8, NOW() - INTERVAL '17 days'),
(5, 10, 'K8s 的学习曲线确实有点陡峭', 5, NOW() - INTERVAL '14 days'),
(5, 16, '推荐先学好 Docker 再学 K8s', 12, NOW() - INTERVAL '13 days');

-- 添加回复评论
INSERT INTO comments (post_id, author_id, parent_id, content, like_count, created_at) VALUES
(1, 4, 2, '同问，我也想了解更多细节', 3, NOW() - INTERVAL '28 days'),
(3, 4, 6, '完全同意！升级到 React 18 后性能提升明显', 8, NOW() - INTERVAL '18 days'),
(5, 7, 10, '是的，循序渐进比较好', 4, NOW() - INTERVAL '12 days');

-- 批量生成更多评论
INSERT INTO comments (post_id, author_id, content, like_count, created_at)
SELECT 
    1 + (row_number() OVER () % 100)::int AS post_id,
    1 + (row_number() OVER () % 50)::int AS author_id,
    CASE (row_number() OVER () % 10)
        WHEN 0 THEN '写得很好，学到了很多！'
        WHEN 1 THEN '请问有源码链接吗？'
        WHEN 2 THEN '期待更多类似的文章'
        WHEN 3 THEN '这个解释很清晰'
        WHEN 4 THEN '正好在学这个，太及时了'
        WHEN 5 THEN '有个小疑问...'
        WHEN 6 THEN '收藏了！'
        WHEN 7 THEN '感谢分享'
        WHEN 8 THEN '干货满满'
        ELSE '赞！'
    END,
    (random() * 20)::int,
    NOW() - (random() * 60 || ' days')::interval
FROM generate_series(1, 300);

-- =====================================================
-- 收藏数据 (200+ bookmarks)
-- =====================================================

INSERT INTO bookmarks (user_id, post_id)
SELECT DISTINCT user_id, post_id FROM (
    SELECT 
        1 + (floor(random() * 50))::int AS user_id,
        1 + (floor(random() * 100))::int AS post_id
    FROM generate_series(1, 250)
) t
ON CONFLICT DO NOTHING;

-- =====================================================
-- 关注关系 (150+ follows)
-- =====================================================

INSERT INTO follows (follower_id, following_id)
SELECT DISTINCT follower_id, following_id FROM (
    SELECT 
        1 + (floor(random() * 50))::int AS follower_id,
        1 + (floor(random() * 20))::int AS following_id
    FROM generate_series(1, 200)
) t
WHERE follower_id != following_id
ON CONFLICT DO NOTHING;

-- =====================================================
-- 更新统计计数
-- =====================================================

-- 更新评论计数
UPDATE posts SET comment_count = (
    SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id
);

-- 更新标签的文章计数
UPDATE tags SET post_count = (
    SELECT COUNT(*) FROM post_tags WHERE post_tags.tag_id = tags.id
);
