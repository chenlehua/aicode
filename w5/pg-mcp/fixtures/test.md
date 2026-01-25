# PostgreSQL MCP Server - 自然语言查询测试用例

本文档包含针对三个测试数据库的自然语言查询问题，用于测试 pg-mcp 的 SQL 生成能力。

---

## 1. Small Database - 博客系统 (blog_db)

### 1.1 简单查询（单表，无条件或简单条件）

#### S1: 查询所有用户

```sql
SELECT * FROM users;
```

#### S2: 有多少篇文章？

```sql
SELECT COUNT(*) FROM posts;
```

#### S3: 查询所有标签

```sql
SELECT * FROM tags;
```

#### S4: 查询所有分类

```sql
SELECT * FROM categories;
```

#### S5: 有多少个用户？

```sql
SELECT COUNT(*) FROM users;
```

#### S6: 查询所有已发布的文章

```sql
SELECT * FROM posts
WHERE status = 'published';
```

#### S7: 查询所有评论

```sql
SELECT * FROM comments;
```

#### S8: 显示前10个用户

```sql
SELECT * FROM users
LIMIT 10;
```

### 1.2 条件查询（单表，复杂条件）

#### S9: 查询状态为活跃的用户

```sql
SELECT * FROM users
WHERE status = 'active';
```

#### S10: 查询浏览量超过1000的文章

```sql
SELECT * FROM posts
WHERE view_count > 1000;
```

#### S11: 查询点赞数大于50的文章

```sql
SELECT * FROM posts
WHERE like_count > 50;
```

#### S12: 查询最近30天发布的文章

```sql
SELECT * FROM posts
WHERE published_at >= NOW() - INTERVAL '30 days';
```

#### S13: 查询用户名包含"dev"的用户

```sql
SELECT * FROM users
WHERE username ILIKE '%dev%';
```

#### S14: 查询精选文章

```sql
SELECT * FROM posts
WHERE is_featured = TRUE;
```

#### S15: 查询置顶文章

```sql
SELECT * FROM posts
WHERE is_pinned = TRUE;
```

#### S16: 查询草稿状态的文章

```sql
SELECT * FROM posts
WHERE status = 'draft';
```

### 1.3 排序和分页

#### S17: 查询浏览量最高的10篇文章

```sql
SELECT * FROM posts
ORDER BY view_count DESC
LIMIT 10;
```

#### S18: 查询最新发布的5篇文章

```sql
SELECT * FROM posts
WHERE status = 'published'
ORDER BY published_at DESC
LIMIT 5;
```

#### S19: 查询点赞最多的文章

```sql
SELECT * FROM posts
ORDER BY like_count DESC
LIMIT 1;
```

#### S20: 查询评论最多的文章

```sql
SELECT * FROM posts
ORDER BY comment_count DESC
LIMIT 1;
```

#### S21: 查询最早注册的用户

```sql
SELECT * FROM users
ORDER BY created_at ASC
LIMIT 1;
```

#### S22: 查询文章数量最多的前5个标签

```sql
SELECT * FROM tags
ORDER BY post_count DESC
LIMIT 5;
```

### 1.4 聚合查询

#### S23: 统计每个分类下有多少篇文章

```sql
SELECT c.name, COUNT(p.id) AS post_count
FROM categories c
LEFT JOIN posts p ON c.id = p.category_id
GROUP BY c.id, c.name;
```

#### S24: 统计每个用户发布了多少篇文章

```sql
SELECT u.username, COUNT(p.id) AS post_count
FROM users u
LEFT JOIN posts p ON u.id = p.author_id
GROUP BY u.id, u.username;
```

#### S25: 计算所有文章的平均浏览量

```sql
SELECT AVG(view_count) AS avg_views
FROM posts;
```

#### S26: 查询总点赞数

```sql
SELECT SUM(like_count) AS total_likes
FROM posts;
```

#### S27: 统计每种文章状态的数量

```sql
SELECT status, COUNT(*) AS count
FROM posts
GROUP BY status;
```

#### S28: 查询每个用户的总浏览量

```sql
SELECT u.username, SUM(p.view_count) AS total_views
FROM users u
JOIN posts p ON u.id = p.author_id
GROUP BY u.id, u.username;
```

#### S29: 统计每月发布的文章数量

```sql
SELECT DATE_TRUNC('month', published_at) AS month, COUNT(*) AS count
FROM posts
WHERE status = 'published'
GROUP BY DATE_TRUNC('month', published_at)
ORDER BY month;
```

### 1.5 关联查询

#### S30: 查询每篇文章及其作者名称

```sql
SELECT p.title, u.username AS author
FROM posts p
JOIN users u ON p.author_id = u.id;
```

#### S31: 查询每篇文章的分类名称

```sql
SELECT p.title, c.name AS category
FROM posts p
LEFT JOIN categories c ON p.category_id = c.id;
```

#### S32: 查询每个标签关联的文章标题

```sql
SELECT t.name AS tag, p.title
FROM tags t
JOIN post_tags pt ON t.id = pt.tag_id
JOIN posts p ON pt.post_id = p.id;
```

#### S33: 查询每条评论的作者和文章标题

```sql
SELECT c.content, u.username AS author, p.title AS post_title
FROM comments c
LEFT JOIN users u ON c.author_id = u.id
JOIN posts p ON c.post_id = p.id;
```

#### S34: 查询用户"alice_dev"发布的所有文章

```sql
SELECT p.*
FROM posts p
JOIN users u ON p.author_id = u.id
WHERE u.username = 'alice_dev';
```

#### S35: 查询"技术"分类下的所有文章

```sql
SELECT p.*
FROM posts p
JOIN categories c ON p.category_id = c.id
WHERE c.name = '技术';
```

#### S36: 查询某篇文章的所有评论及评论者

```sql
SELECT c.content, u.username AS author
FROM comments c
LEFT JOIN users u ON c.author_id = u.id
WHERE c.post_id = 1;
```

### 1.6 子查询和复杂查询

#### S37: 查询没有发布任何文章的用户

```sql
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM posts p
    WHERE p.author_id = u.id
);
```

#### S38: 查询收藏数最多的文章

```sql
SELECT p.*, COUNT(b.id) AS bookmark_count
FROM posts p
JOIN bookmarks b ON p.id = b.post_id
GROUP BY p.id
ORDER BY bookmark_count DESC
LIMIT 1;
```

#### S39: 查询互相关注的用户对

```sql
SELECT f1.follower_id, f1.following_id
FROM follows f1
JOIN follows f2 ON f1.follower_id = f2.following_id
                AND f1.following_id = f2.follower_id
WHERE f1.follower_id < f1.following_id;
```

#### S40: 查询被收藏超过5次的文章

```sql
SELECT p.*, COUNT(b.id) AS bookmark_count
FROM posts p
JOIN bookmarks b ON p.id = b.post_id
GROUP BY p.id
HAVING COUNT(b.id) > 5;
```

#### S41: 查询每个分类下浏览量最高的文章

```sql
SELECT DISTINCT ON (category_id) *
FROM posts
WHERE category_id IS NOT NULL
ORDER BY category_id, view_count DESC;
```

#### S42: 查询关注者最多的5个用户

```sql
SELECT u.*, COUNT(f.follower_id) AS follower_count
FROM users u
JOIN follows f ON u.id = f.following_id
GROUP BY u.id
ORDER BY follower_count DESC
LIMIT 5;
```

#### S43: 查询评论数超过平均值的文章

```sql
SELECT * FROM posts
WHERE comment_count > (
    SELECT AVG(comment_count) FROM posts
);
```

### 1.7 使用视图

#### S44: 查询热门文章排行

```sql
SELECT * FROM trending_posts;
```

#### S45: 查询用户统计信息

```sql
SELECT * FROM user_stats;
```

#### S46: 查询发布文章最多的用户

```sql
SELECT * FROM user_stats
ORDER BY post_count DESC
LIMIT 1;
```

#### S47: 查询总浏览量最高的用户

```sql
SELECT * FROM user_stats
ORDER BY total_views DESC
LIMIT 1;
```

---

## 2. Medium Database - 电商平台 (ecommerce_db)

### 2.1 简单查询

#### M1: 查询所有商品

```sql
SELECT * FROM products;
```

#### M2: 有多少个店铺？

```sql
SELECT COUNT(*) FROM stores;
```

#### M3: 查询所有品牌

```sql
SELECT * FROM brands;
```

#### M4: 有多少个客户？

```sql
SELECT COUNT(*) FROM users
WHERE role = 'customer';
```

#### M5: 查询所有优惠券

```sql
SELECT * FROM coupons;
```

#### M6: 查询所有订单

```sql
SELECT * FROM orders;
```

#### M7: 有多少种商品分类？

```sql
SELECT COUNT(*) FROM categories;
```

### 2.2 条件查询

#### M8: 查询价格超过1000元的商品

```sql
SELECT * FROM products
WHERE price > 1000;
```

#### M9: 查询库存不足10件的商品

```sql
SELECT * FROM products
WHERE stock_quantity < 10;
```

#### M10: 查询已认证的店铺

```sql
SELECT * FROM stores
WHERE is_verified = TRUE;
```

#### M11: 查询精选商品

```sql
SELECT * FROM products
WHERE is_featured = TRUE;
```

#### M12: 查询已完成的订单

```sql
SELECT * FROM orders
WHERE status = 'delivered';
```

#### M13: 查询已取消的订单

```sql
SELECT * FROM orders
WHERE status = 'cancelled';
```

#### M14: 查询有效的优惠券

```sql
SELECT * FROM coupons
WHERE is_active = TRUE
  AND expires_at > NOW();
```

#### M15: 查询评分高于4.5的商品

```sql
SELECT * FROM products
WHERE rating > 4.5;
```

#### M16: 查询5星好评

```sql
SELECT * FROM reviews
WHERE rating = 5;
```

### 2.3 排序和分页

#### M17: 查询销量最高的10个商品

```sql
SELECT * FROM products
ORDER BY sold_count DESC
LIMIT 10;
```

#### M18: 查询最贵的商品

```sql
SELECT * FROM products
ORDER BY price DESC
LIMIT 1;
```

#### M19: 查询最便宜的商品

```sql
SELECT * FROM products
ORDER BY price ASC
LIMIT 1;
```

#### M20: 查询评分最高的商品

```sql
SELECT * FROM products
ORDER BY rating DESC
LIMIT 1;
```

#### M21: 查询最新上架的20个商品

```sql
SELECT * FROM products
ORDER BY created_at DESC
LIMIT 20;
```

#### M22: 查询评论数最多的商品

```sql
SELECT * FROM products
ORDER BY review_count DESC
LIMIT 1;
```

#### M23: 查询金额最大的订单

```sql
SELECT * FROM orders
ORDER BY total_amount DESC
LIMIT 1;
```

### 2.4 聚合查询

#### M24: 统计每个品牌有多少商品

```sql
SELECT b.name, COUNT(p.id) AS product_count
FROM brands b
LEFT JOIN products p ON b.id = p.brand_id
GROUP BY b.id, b.name;
```

#### M25: 统计每个分类的商品数量

```sql
SELECT c.name, COUNT(p.id) AS product_count
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
GROUP BY c.id, c.name;
```

#### M26: 计算所有商品的平均价格

```sql
SELECT AVG(price) AS avg_price
FROM products;
```

#### M27: 统计每个店铺的订单总额

```sql
SELECT s.name, SUM(o.total_amount) AS total_sales
FROM stores s
JOIN orders o ON s.id = o.store_id
GROUP BY s.id, s.name;
```

#### M28: 统计每种订单状态的数量

```sql
SELECT status, COUNT(*) AS count
FROM orders
GROUP BY status;
```

#### M29: 计算每个客户的订单总金额

```sql
SELECT u.username, SUM(o.total_amount) AS total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username;
```

#### M30: 统计每天的订单数量

```sql
SELECT DATE(created_at) AS order_date, COUNT(*) AS order_count
FROM orders
GROUP BY DATE(created_at)
ORDER BY order_date;
```

#### M31: 统计每个月的销售总额

```sql
SELECT DATE_TRUNC('month', created_at) AS month,
       SUM(total_amount) AS total_sales
FROM orders
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;
```

#### M32: 计算每个商品的平均评分

```sql
SELECT p.name, AVG(r.rating) AS avg_rating
FROM products p
JOIN reviews r ON p.id = r.product_id
GROUP BY p.id, p.name;
```

### 2.5 关联查询

#### M33: 查询每个订单的客户信息

```sql
SELECT o.order_number, u.username, u.email
FROM orders o
JOIN users u ON o.user_id = u.id;
```

#### M34: 查询每个商品的店铺名称

```sql
SELECT p.name AS product, s.name AS store
FROM products p
JOIN stores s ON p.store_id = s.id;
```

#### M35: 查询每个商品的品牌名称

```sql
SELECT p.name AS product, b.name AS brand
FROM products p
LEFT JOIN brands b ON p.brand_id = b.id;
```

#### M36: 查询订单中包含的商品详情

```sql
SELECT o.order_number, p.name AS product, oi.quantity, oi.unit_price
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

#### M37: 查询每个商品的评论内容

```sql
SELECT p.name AS product, r.content, r.rating
FROM products p
JOIN reviews r ON p.id = r.product_id;
```

#### M38: 查询Apple品牌的所有商品

```sql
SELECT p.*
FROM products p
JOIN brands b ON p.brand_id = b.id
WHERE b.name = 'Apple';
```

#### M39: 查询某个店铺的所有订单

```sql
SELECT o.*
FROM orders o
JOIN stores s ON o.store_id = s.id
WHERE s.id = 1;
```

#### M40: 查询使用了优惠券的订单

```sql
SELECT * FROM orders
WHERE coupon_id IS NOT NULL;
```

### 2.6 复杂业务查询

#### M41: 查询库存预警商品（库存低于阈值）

```sql
SELECT * FROM products
WHERE stock_quantity <= low_stock_threshold;
```

#### M42: 查询每个客户的消费总额和订单数

```sql
SELECT u.username,
       COUNT(o.id) AS order_count,
       SUM(o.total_amount) AS total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username;
```

#### M43: 查询复购率最高的商品

```sql
SELECT p.name,
       COUNT(DISTINCT o.user_id) AS buyer_count,
       COUNT(oi.id) AS purchase_count
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
GROUP BY p.id, p.name
ORDER BY (COUNT(oi.id)::float / NULLIF(COUNT(DISTINCT o.user_id), 0)) DESC
LIMIT 10;
```

#### M44: 查询每个分类的销售额排名

```sql
SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_sales
FROM categories c
JOIN products p ON c.id = p.category_id
JOIN order_items oi ON p.id = oi.product_id
GROUP BY c.id, c.name
ORDER BY total_sales DESC;
```

#### M45: 查询过去7天的销售趋势

```sql
SELECT DATE(created_at) AS sale_date,
       COUNT(*) AS order_count,
       SUM(total_amount) AS total_sales
FROM orders
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY sale_date;
```

#### M46: 查询未支付的订单

```sql
SELECT * FROM orders
WHERE status = 'pending';
```

#### M47: 查询已发货但未送达的订单

```sql
SELECT * FROM orders
WHERE status = 'shipped';
```

#### M48: 查询退款订单及原因

```sql
SELECT o.order_number, r.amount, r.reason, r.status
FROM orders o
JOIN refunds r ON o.id = r.order_id;
```

#### M49: 查询每个店铺的平均评分

```sql
SELECT s.name, AVG(r.rating) AS avg_rating
FROM stores s
JOIN products p ON s.id = p.store_id
JOIN reviews r ON p.id = r.product_id
GROUP BY s.id, s.name;
```

#### M50: 查询每个城市的订单分布

```sql
SELECT SPLIT_PART(shipping_address, ' ', 1) AS city,
       COUNT(*) AS order_count
FROM orders
WHERE shipping_address IS NOT NULL
GROUP BY city
ORDER BY order_count DESC;
```

### 2.7 使用视图

#### M51: 查询热销商品排行榜

```sql
SELECT * FROM bestseller_products;
```

#### M52: 查询库存预警商品列表

```sql
SELECT * FROM low_stock_products;
```

#### M53: 查询每日销售统计

```sql
SELECT * FROM daily_sales
ORDER BY sale_date DESC;
```

#### M54: 查询客户消费统计

```sql
SELECT * FROM user_order_stats
ORDER BY total_spent DESC;
```

#### M55: 查询店铺销售统计

```sql
SELECT * FROM store_sales_stats
ORDER BY total_sales DESC;
```

#### M56: 查询优惠券使用情况

```sql
SELECT * FROM coupon_usage_stats;
```

#### M57: 查询在售商品列表

```sql
SELECT * FROM active_products;
```

### 2.8 高级查询

#### M58: 查询购买过某商品的用户还购买了什么

```sql
SELECT DISTINCT p2.name
FROM order_items oi1
JOIN orders o1 ON oi1.order_id = o1.id
JOIN orders o2 ON o1.user_id = o2.user_id
JOIN order_items oi2 ON o2.id = oi2.order_id
JOIN products p2 ON oi2.product_id = p2.id
WHERE oi1.product_id = 1
  AND oi2.product_id != 1;
```

#### M59: 查询从未下单的用户

```sql
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id
);
```

#### M60: 查询订单金额高于平均值的订单

```sql
SELECT * FROM orders
WHERE total_amount > (
    SELECT AVG(total_amount) FROM orders
);
```

#### M61: 查询每个分类下销量最高的商品

```sql
SELECT DISTINCT ON (category_id) *
FROM products
WHERE category_id IS NOT NULL
ORDER BY category_id, sold_count DESC;
```

#### M62: 查询连续7天都有订单的店铺

```sql
WITH daily_orders AS (
    SELECT store_id, DATE(created_at) AS order_date
    FROM orders
    WHERE created_at >= NOW() - INTERVAL '7 days'
    GROUP BY store_id, DATE(created_at)
)
SELECT store_id
FROM daily_orders
GROUP BY store_id
HAVING COUNT(DISTINCT order_date) = 7;
```

#### M63: 查询商品价格变化历史

```sql
SELECT * FROM inventory_logs
WHERE change_type = 'price_change'
ORDER BY created_at DESC;
```

---

## 3. Large Database - 企业 ERP 系统 (erp_db)

### 3.1 人力资源模块 (HR)

#### L1: 查询所有员工

```sql
SELECT * FROM hr.employees;
```

#### L2: 有多少个员工？

```sql
SELECT COUNT(*) FROM hr.employees;
```

#### L3: 查询所有部门

```sql
SELECT * FROM departments;
```

#### L4: 查询所有职位

```sql
SELECT * FROM positions;
```

#### L5: 查询在职员工数量

```sql
SELECT COUNT(*) FROM hr.employees
WHERE status = 'active';
```

#### L6: 查询所有培训课程

```sql
SELECT * FROM hr.training_courses;
```

#### L7: 查询研发部的所有员工

```sql
SELECT e.*
FROM hr.employees e
JOIN departments d ON e.department_id = d.id
WHERE d.name = '研发部';
```

#### L8: 查询工资超过10万的员工

```sql
SELECT * FROM hr.employees
WHERE base_salary > 100000;
```

#### L9: 查询2020年之后入职的员工

```sql
SELECT * FROM hr.employees
WHERE hire_date >= '2020-01-01';
```

#### L10: 查询正在休假的员工

```sql
SELECT * FROM hr.employees
WHERE status = 'on_leave';
```

#### L11: 查询每个部门的员工数量

```sql
SELECT d.name, COUNT(e.id) AS employee_count
FROM departments d
LEFT JOIN hr.employees e ON d.id = e.department_id
GROUP BY d.id, d.name;
```

#### L12: 查询每个部门的平均工资

```sql
SELECT d.name, AVG(e.base_salary) AS avg_salary
FROM departments d
JOIN hr.employees e ON d.id = e.department_id
GROUP BY d.id, d.name;
```

#### L13: 查询工资最高的10个员工

```sql
SELECT * FROM hr.employees
ORDER BY base_salary DESC
LIMIT 10;
```

#### L14: 查询每个员工的部门和职位信息

```sql
SELECT e.full_name, d.name AS department, p.title AS position
FROM hr.employees e
LEFT JOIN departments d ON e.department_id = d.id
LEFT JOIN positions p ON e.position_id = p.id;
```

#### L15: 查询没有直属下级的员工

```sql
SELECT e.*
FROM hr.employees e
WHERE NOT EXISTS (
    SELECT 1 FROM hr.employees sub
    WHERE sub.manager_id = e.id
);
```

#### L16: 查询今天的考勤记录

```sql
SELECT * FROM hr.attendance
WHERE attendance_date = CURRENT_DATE;
```

#### L17: 查询本月迟到的员工

```sql
SELECT DISTINCT e.*
FROM hr.employees e
JOIN hr.attendance a ON e.id = a.employee_id
WHERE a.status = 'late'
  AND a.attendance_date >= DATE_TRUNC('month', CURRENT_DATE);
```

#### L18: 统计每个员工本月的工作小时数

```sql
SELECT e.full_name, SUM(a.work_hours) AS total_hours
FROM hr.employees e
JOIN hr.attendance a ON e.id = a.employee_id
WHERE a.attendance_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY e.id, e.full_name;
```

#### L19: 查询上个月的薪资发放记录

```sql
SELECT * FROM hr.payroll
WHERE pay_period = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month');
```

#### L20: 查询待审批的请假申请

```sql
SELECT * FROM hr.leave_requests
WHERE status = 'pending';
```

#### L21: 统计每种请假类型的申请数量

```sql
SELECT leave_type, COUNT(*) AS count
FROM hr.leave_requests
GROUP BY leave_type;
```

#### L22: 查询每个员工的剩余年假天数

```sql
SELECT e.full_name, lb.balance
FROM hr.employees e
JOIN hr.leave_balances lb ON e.id = lb.employee_id
WHERE lb.leave_type = 'annual';
```

#### L23: 查询加班时间最多的员工

```sql
SELECT e.full_name, SUM(a.overtime_hours) AS total_overtime
FROM hr.employees e
JOIN hr.attendance a ON e.id = a.employee_id
GROUP BY e.id, e.full_name
ORDER BY total_overtime DESC
LIMIT 1;
```

#### L24: 查询正在招聘的职位

```sql
SELECT * FROM hr.job_postings
WHERE status = 'open';
```

#### L25: 查询每个职位的申请人数

```sql
SELECT jp.title, COUNT(ja.id) AS applicant_count
FROM hr.job_postings jp
LEFT JOIN hr.job_applications ja ON jp.id = ja.posting_id
GROUP BY jp.id, jp.title;
```

#### L26: 查询待面试的候选人

```sql
SELECT * FROM hr.job_applications
WHERE status = 'interview_scheduled';
```

#### L27: 查询参加过某培训课程的员工

```sql
SELECT DISTINCT e.*
FROM hr.employees e
JOIN hr.training_records tr ON e.id = tr.employee_id
WHERE tr.course_id = 1;
```

#### L28: 查询培训通过率

```sql
SELECT tc.name,
       COUNT(CASE WHEN tr.status = 'passed' THEN 1 END)::float / COUNT(*) * 100 AS pass_rate
FROM hr.training_courses tc
JOIN hr.training_records tr ON tc.id = tr.course_id
GROUP BY tc.id, tc.name;
```

### 3.2 财务模块 (Finance)

#### L29: 查询所有银行账户

```sql
SELECT * FROM finance.bank_accounts;
```

#### L30: 查询每个银行账户的余额

```sql
SELECT account_name, current_balance
FROM finance.bank_accounts;
```

#### L31: 查询本月的所有凭证

```sql
SELECT * FROM finance.vouchers
WHERE voucher_date >= DATE_TRUNC('month', CURRENT_DATE);
```

#### L32: 查询待审核的凭证

```sql
SELECT * FROM finance.vouchers
WHERE status = 'pending';
```

#### L33: 查询每个会计科目的余额

```sql
SELECT a.name, ab.balance
FROM finance.accounts a
JOIN finance.account_balances ab ON a.id = ab.account_id;
```

#### L34: 查询本月的收入总额

```sql
SELECT SUM(vl.credit) AS total_income
FROM finance.voucher_lines vl
JOIN finance.vouchers v ON vl.voucher_id = v.id
JOIN finance.accounts a ON vl.account_id = a.id
WHERE a.account_type = 'income'
  AND v.voucher_date >= DATE_TRUNC('month', CURRENT_DATE);
```

#### L35: 查询本月的支出总额

```sql
SELECT SUM(vl.debit) AS total_expense
FROM finance.voucher_lines vl
JOIN finance.vouchers v ON vl.voucher_id = v.id
JOIN finance.accounts a ON vl.account_id = a.id
WHERE a.account_type = 'expense'
  AND v.voucher_date >= DATE_TRUNC('month', CURRENT_DATE);
```

#### L36: 查询待支付的发票

```sql
SELECT * FROM finance.invoices
WHERE payment_status = 'pending';
```

#### L37: 查询逾期未付的发票

```sql
SELECT * FROM finance.invoices
WHERE payment_status = 'pending'
  AND due_date < CURRENT_DATE;
```

#### L38: 查询每个部门的预算执行情况

```sql
SELECT d.name,
       b.budget_amount,
       b.spent_amount,
       b.budget_amount - b.spent_amount AS remaining
FROM departments d
JOIN finance.budgets b ON d.id = b.department_id;
```

### 3.3 库存模块 (Inventory)

#### L39: 查询所有仓库

```sql
SELECT * FROM inventory.warehouses;
```

#### L40: 查询所有产品/物料

```sql
SELECT * FROM inventory.products;
```

#### L41: 查询每个仓库的库存总量

```sql
SELECT w.name, SUM(s.quantity) AS total_quantity
FROM inventory.warehouses w
JOIN inventory.stock s ON w.id = s.warehouse_id
GROUP BY w.id, w.name;
```

#### L42: 查询库存不足的物料

```sql
SELECT p.*
FROM inventory.products p
JOIN inventory.stock s ON p.id = s.product_id
WHERE s.quantity < p.reorder_point;
```

#### L43: 查询需要补货的物料

```sql
SELECT p.*, s.quantity
FROM inventory.products p
JOIN inventory.stock s ON p.id = s.product_id
WHERE s.quantity <= p.reorder_point;
```

#### L44: 查询每个产品的库存分布

```sql
SELECT p.name, w.name AS warehouse, s.quantity
FROM inventory.products p
JOIN inventory.stock s ON p.id = s.product_id
JOIN inventory.warehouses w ON s.warehouse_id = w.id;
```

#### L45: 查询最近的库存移动记录

```sql
SELECT * FROM inventory.stock_movements
ORDER BY created_at DESC
LIMIT 20;
```

#### L46: 查询盘点差异大于0的记录

```sql
SELECT * FROM inventory.stock_counts
WHERE variance != 0;
```

#### L47: 查询某仓库的所有库位

```sql
SELECT * FROM inventory.locations
WHERE warehouse_id = 1;
```

### 3.4 销售模块 (Sales)

#### L48: 查询所有客户

```sql
SELECT * FROM sales.customers;
```

#### L49: 查询VIP客户

```sql
SELECT * FROM sales.customers
WHERE customer_type = 'vip';
```

#### L50: 查询本月的销售订单

```sql
SELECT * FROM sales.sales_orders
WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE);
```

#### L51: 查询每个客户的订单总额

```sql
SELECT c.name, SUM(so.total_amount) AS total
FROM sales.customers c
JOIN sales.sales_orders so ON c.id = so.customer_id
GROUP BY c.id, c.name;
```

#### L52: 查询每个销售员的业绩

```sql
SELECT e.full_name, SUM(so.total_amount) AS total_sales
FROM hr.employees e
JOIN sales.sales_orders so ON e.id = so.sales_rep_id
GROUP BY e.id, e.full_name
ORDER BY total_sales DESC;
```

#### L53: 查询待发货的订单

```sql
SELECT * FROM sales.sales_orders
WHERE status = 'confirmed';
```

#### L54: 查询已发货未签收的订单

```sql
SELECT * FROM sales.sales_orders
WHERE status = 'shipped';
```

#### L55: 查询销售额最高的客户

```sql
SELECT c.name, SUM(so.total_amount) AS total
FROM sales.customers c
JOIN sales.sales_orders so ON c.id = so.customer_id
GROUP BY c.id, c.name
ORDER BY total DESC
LIMIT 1;
```

#### L56: 查询本月的销售退货

```sql
SELECT * FROM sales.sales_returns
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

#### L57: 查询有效的报价单

```sql
SELECT * FROM sales.quotations
WHERE valid_until >= CURRENT_DATE;
```

### 3.5 采购模块 (Procurement)

#### L58: 查询所有供应商

```sql
SELECT * FROM procurement.suppliers;
```

#### L59: 查询评级最高的供应商

```sql
SELECT * FROM procurement.suppliers
ORDER BY rating DESC
LIMIT 1;
```

#### L60: 查询待审批的采购订单

```sql
SELECT * FROM procurement.purchase_orders
WHERE status = 'pending_approval';
```

#### L61: 查询每个供应商的采购总额

```sql
SELECT s.name, SUM(po.total_amount) AS total
FROM procurement.suppliers s
JOIN procurement.purchase_orders po ON s.id = po.supplier_id
GROUP BY s.id, s.name;
```

#### L62: 查询待收货的采购订单

```sql
SELECT * FROM procurement.purchase_orders
WHERE status = 'ordered';
```

#### L63: 查询部分收货的采购订单

```sql
SELECT * FROM procurement.purchase_orders
WHERE status = 'partial_received';
```

#### L64: 查询某个物料的供应商列表

```sql
SELECT s.*
FROM procurement.suppliers s
JOIN procurement.supplier_products sp ON s.id = sp.supplier_id
WHERE sp.product_id = 1;
```

#### L65: 查询哪个供应商的某物料价格最低

```sql
SELECT s.name, sp.unit_price
FROM procurement.suppliers s
JOIN procurement.supplier_products sp ON s.id = sp.supplier_id
WHERE sp.product_id = 1
ORDER BY sp.unit_price ASC
LIMIT 1;
```

### 3.6 生产模块 (Production)

#### L66: 查询所有生产工单

```sql
SELECT * FROM production.work_orders;
```

#### L67: 查询进行中的生产工单

```sql
SELECT * FROM production.work_orders
WHERE status = 'in_progress';
```

#### L68: 查询已完成的生产工单

```sql
SELECT * FROM production.work_orders
WHERE status = 'completed';
```

#### L69: 查询某产品的BOM（物料清单）

```sql
SELECT b.*, bl.*
FROM production.bom b
JOIN production.bom_lines bl ON b.id = bl.bom_id
WHERE b.product_id = 1;
```

#### L70: 查询每个产品的BOM成本

```sql
SELECT b.product_id, p.name, SUM(bl.quantity * ip.unit_cost) AS total_cost
FROM production.bom b
JOIN production.bom_lines bl ON b.id = bl.bom_id
JOIN inventory.products ip ON bl.component_id = ip.id
JOIN inventory.products p ON b.product_id = p.id
GROUP BY b.product_id, p.name;
```

#### L71: 查询质检不合格的记录

```sql
SELECT * FROM production.quality_inspections
WHERE result = 'fail';
```

#### L72: 查询质检合格率

```sql
SELECT COUNT(CASE WHEN result = 'pass' THEN 1 END)::float / COUNT(*) * 100 AS pass_rate
FROM production.quality_inspections;
```

#### L73: 查询逾期未完成的工单

```sql
SELECT * FROM production.work_orders
WHERE planned_end_date < CURRENT_DATE
  AND status != 'completed';
```

### 3.7 跨模块复杂查询

#### L74: 查询每个公司的员工总数和平均工资

```sql
SELECT c.name, COUNT(e.id) AS employee_count, AVG(e.base_salary) AS avg_salary
FROM companies c
JOIN hr.employees e ON c.id = e.company_id
GROUP BY c.id, c.name;
```

#### L75: 查询销售额最高的部门

```sql
SELECT d.name, SUM(so.total_amount) AS total_sales
FROM departments d
JOIN hr.employees e ON d.id = e.department_id
JOIN sales.sales_orders so ON e.id = so.sales_rep_id
GROUP BY d.id, d.name
ORDER BY total_sales DESC
LIMIT 1;
```

#### L76: 查询本月销售额与上月对比

```sql
SELECT 'this_month' AS period, SUM(total_amount) AS amount
FROM sales.sales_orders
WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE)
UNION ALL
SELECT 'last_month' AS period, SUM(total_amount) AS amount
FROM sales.sales_orders
WHERE order_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
  AND order_date < DATE_TRUNC('month', CURRENT_DATE);
```

#### L77: 查询库存周转率

```sql
SELECT p.name,
       COALESCE(SUM(sm.quantity), 0) / NULLIF(AVG(s.quantity), 0) AS turnover_rate
FROM inventory.products p
LEFT JOIN inventory.stock s ON p.id = s.product_id
LEFT JOIN inventory.stock_movements sm ON p.id = sm.product_id
                                       AND sm.movement_type = 'out'
GROUP BY p.id, p.name;
```

#### L78: 查询从采购到入库的平均时间

```sql
SELECT AVG(gr.received_date - po.order_date) AS avg_days
FROM procurement.purchase_orders po
JOIN procurement.goods_receipts gr ON po.id = gr.po_id;
```

#### L79: 查询每个客户的应收账款账龄

```sql
SELECT * FROM finance.v_ar_aging;
```

#### L80: 查询每个供应商的应付账款账龄

```sql
SELECT * FROM finance.v_ap_aging;
```

### 3.8 使用视图

#### L81: 查看公司仪表板数据

```sql
SELECT * FROM v_company_dashboard;
```

#### L82: 查看员工详细信息

```sql
SELECT * FROM hr.v_employee_details;
```

#### L83: 查看部门统计

```sql
SELECT * FROM v_department_stats;
```

#### L84: 查看月度考勤统计

```sql
SELECT * FROM hr.v_monthly_attendance;
```

#### L85: 查看销售订单概览

```sql
SELECT * FROM sales.v_order_overview;
```

#### L86: 查看库存汇总

```sql
SELECT * FROM inventory.v_stock_summary;
```

#### L87: 查看低库存预警

```sql
SELECT * FROM inventory.v_low_stock_alert;
```

#### L88: 查看采购订单概览

```sql
SELECT * FROM procurement.v_po_overview;
```

#### L89: 查看供应商统计

```sql
SELECT * FROM procurement.v_supplier_stats;
```

#### L90: 查看质检统计

```sql
SELECT * FROM production.v_qc_stats;
```

---

## 4. 边界情况和特殊查询

### 4.1 空结果处理

#### E1: 查询2030年的订单

> 应返回空结果

```sql
SELECT * FROM orders
WHERE EXTRACT(YEAR FROM created_at) = 2030;
```

#### E2: 查询价格超过一百万的商品

> 可能返回空结果

```sql
SELECT * FROM products
WHERE price > 1000000;
```

#### E3: 查询用户名为"不存在的用户"的信息

> 应返回空结果

```sql
SELECT * FROM users
WHERE username = '不存在的用户';
```

### 4.2 模糊查询

#### E4: 查询名字中包含"科技"的公司

```sql
SELECT * FROM companies
WHERE name LIKE '%科技%';
```

#### E5: 查询邮箱以"gmail.com"结尾的用户

```sql
SELECT * FROM users
WHERE email LIKE '%gmail.com';
```

#### E6: 查询标题包含"Python"的文章

```sql
SELECT * FROM posts
WHERE title ILIKE '%python%';
```

### 4.3 日期范围

#### E7: 查询过去一周的订单

```sql
SELECT * FROM orders
WHERE created_at >= NOW() - INTERVAL '7 days';
```

#### E8: 查询上个季度的销售数据

```sql
SELECT * FROM sales.sales_orders
WHERE order_date >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months')
  AND order_date < DATE_TRUNC('quarter', CURRENT_DATE);
```

#### E9: 查询今年的所有入职员工

```sql
SELECT * FROM hr.employees
WHERE EXTRACT(YEAR FROM hire_date) = EXTRACT(YEAR FROM CURRENT_DATE);
```

#### E10: 查询工作日的考勤记录

```sql
SELECT * FROM hr.attendance
WHERE EXTRACT(DOW FROM attendance_date) NOT IN (0, 6);
```

### 4.4 NULL 值处理

#### E11: 查询没有分配部门的员工

```sql
SELECT * FROM hr.employees
WHERE department_id IS NULL;
```

#### E12: 查询没有经理的员工

```sql
SELECT * FROM hr.employees
WHERE manager_id IS NULL;
```

#### E13: 查询没有设置价格的商品

```sql
SELECT * FROM products
WHERE price IS NULL;
```

### 4.5 多条件组合

#### E14: 查询价格在100到500之间且评分高于4的商品

```sql
SELECT * FROM products
WHERE price BETWEEN 100 AND 500
  AND rating > 4;
```

#### E15: 查询北京或上海的客户

```sql
SELECT * FROM sales.customers
WHERE city = '北京' OR city = '上海';
```

#### E16: 查询已发布且浏览量超过1000的精选文章

```sql
SELECT * FROM posts
WHERE status = 'published'
  AND view_count > 1000
  AND is_featured = TRUE;
```

#### E17: 查询本月下单且已完成的VIP客户订单

```sql
SELECT o.*
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.role = 'vip'
  AND o.status = 'delivered'
  AND o.created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

---

## 5. 测试注意事项

### 5.1 SQL 安全验证

以下查询应该被 pg-mcp 拒绝执行：

#### X1: 删除所有用户

> ❌ 应拒绝原因：DELETE 操作

```sql
DELETE FROM users;
```

#### X2: 更新商品价格为0

> ❌ 应拒绝原因：UPDATE 操作

```sql
UPDATE products SET price = 0;
```

#### X3: 创建新表

> ❌ 应拒绝原因：CREATE 操作

```sql
CREATE TABLE test (id INT);
```

#### X4: 删除数据库

> ❌ 应拒绝原因：DROP 操作

```sql
DROP DATABASE blog_db;
```

#### X5: 查询用户密码

> ❌ 应拒绝原因：敏感信息

```sql
SELECT password_hash FROM users;
```

### 5.2 结果验证要点

1. **结果完整性**: 返回的数据是否完整
2. **列名正确性**: 返回的列名是否有意义
3. **数据类型正确**: 数值、日期等类型是否正确
4. **排序正确性**: ORDER BY 是否按预期排序
5. **聚合正确性**: COUNT/SUM/AVG 等计算是否正确

### 5.3 性能关注点

- 大表查询是否使用了适当的 LIMIT
- 复杂 JOIN 是否有效率问题
- 是否利用了已有的索引

---

## 6. 连接信息

| 数据库 | 连接字符串 |
|--------|-----------|
| Small | `postgresql://postgres:postgres@localhost:5432/blog_db` |
| Medium | `postgresql://postgres:postgres@localhost:5433/ecommerce_db` |
| Large | `postgresql://postgres:postgres@localhost:5434/erp_db` |
