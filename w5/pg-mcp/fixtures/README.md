# PostgreSQL MCP Server - Test Fixtures

用于测试 PostgreSQL MCP Server 的三个测试数据库。

## 数据库概览

| 数据库 | 端口 | 数据库名 | 场景 | Tables | Views | Types | 数据量 |
|--------|------|----------|------|--------|-------|-------|--------|
| Small | 5432 | blog_db | 博客系统 | 8 | 3 | 2 | ~1,000 行 |
| Medium | 5433 | ecommerce_db | 电商平台 | 25 | 10 | 8 | ~50,000 行 |
| Large | 5434 | erp_db | 企业ERP | 60 | 20 | 15 | ~100,000 行 |

## 快速开始

### 启动所有数据库

```bash
cd fixtures
make up
```

### 查看数据库状态

```bash
make status
```

### 连接到数据库

```bash
# 使用 psql 连接
make psql-small    # 博客系统
make psql-medium   # 电商平台
make psql-large    # ERP系统

# 或者使用命令行
psql -h localhost -p 5432 -U postgres -d blog_db
psql -h localhost -p 5433 -U postgres -d ecommerce_db
psql -h localhost -p 5434 -U postgres -d erp_db
```

### 查看数据库统计

```bash
make stats
```

## 数据库详情

### Small - 博客系统 (blog_db)

一个简单的博客系统，适合快速测试基本功能。

**表结构：**
- `users` - 用户表（50个用户）
- `categories` - 文章分类（10个分类，支持层级）
- `tags` - 文章标签（20个标签）
- `posts` - 文章表（100篇文章）
- `post_tags` - 文章标签关联
- `comments` - 评论表（300+评论，支持嵌套）
- `bookmarks` - 用户收藏
- `follows` - 用户关注关系

**视图：**
- `published_posts` - 已发布文章视图
- `user_stats` - 用户统计视图
- `trending_posts` - 热门文章视图

### Medium - 电商平台 (ecommerce_db)

完整的电商平台数据库，包含用户、商品、订单、支付等核心业务。

**主要模块：**
- 用户管理（用户、地址）
- 商品管理（商品、分类、品牌、变体、图片）
- 购物车
- 订单管理（订单、订单项、发货）
- 支付和退款
- 优惠券和促销
- 商品评论
- 收藏和浏览历史

**表数量：** 25张表
**数据规模：**
- 500 用户
- 300 商品
- 2000 订单
- 3000+ 评论

### Large - 企业ERP系统 (erp_db)

完整的企业资源计划系统，覆盖多个业务模块。

**模块划分（使用 Schema）：**
- `public` - 公共模块（公司、部门、职位、用户、权限）
- `hr` - 人力资源（员工、合同、考勤、请假、薪资、培训、招聘）
- `finance` - 财务（会计科目、凭证、银行账户、发票、收付款）
- `inventory` - 库存（仓库、库位、产品、库存、盘点）
- `sales` - 销售（客户、销售订单、发货、报价）
- `procurement` - 采购（供应商、采购订单、收货）
- `production` - 生产（BOM、生产工单、质量检验）

**表数量：** 60张表
**数据规模：**
- 3 家公司，50 个部门
- 1000 员工
- 300 产品，200 客户，100 供应商
- 500 销售订单，300 采购订单
- 200 生产工单

## 常用命令

```bash
# 启动/停止
make up                    # 启动所有数据库
make down                  # 停止所有数据库
make restart               # 重启所有数据库

# 单个数据库操作
make up-small              # 启动 Small
make up-medium             # 启动 Medium
make up-large              # 启动 Large

# 重建数据库（清除数据并重新初始化）
make rebuild               # 重建所有
make rebuild-small         # 重建 Small
make rebuild-medium        # 重建 Medium
make rebuild-large         # 重建 Large

# 清理
make clean                 # 清理所有容器和数据卷

# 日志
make logs                  # 查看所有日志
make logs-small            # 查看 Small 日志

# 数据库 Shell
make psql-small            # 连接到 Small
make psql-medium           # 连接到 Medium
make psql-large            # 连接到 Large

# 统计信息
make stats                 # 显示所有数据库统计

# 连接信息
make connection-info       # 显示连接字符串

# pgAdmin
make up-admin              # 启动 pgAdmin (http://localhost:5050)
make down-admin            # 停止 pgAdmin
```

## 连接信息

| 数据库 | 连接字符串 |
|--------|-----------|
| Small | `postgresql://postgres:postgres@localhost:5432/blog_db` |
| Medium | `postgresql://postgres:postgres@localhost:5433/ecommerce_db` |
| Large | `postgresql://postgres:postgres@localhost:5434/erp_db` |

## 配置示例

在 `config.yaml` 中配置测试数据库：

```yaml
databases:
  - name: "blog"
    host: "localhost"
    port: 5432
    database: "blog_db"
    user: "postgres"
    password: "postgres"

  - name: "ecommerce"
    host: "localhost"
    port: 5433
    database: "ecommerce_db"
    user: "postgres"
    password: "postgres"

  - name: "erp"
    host: "localhost"
    port: 5434
    database: "erp_db"
    user: "postgres"
    password: "postgres"
```

## 示例查询

### Small (博客系统)

```sql
-- 查询最近发布的文章
SELECT title, author_username, view_count, like_count 
FROM published_posts 
ORDER BY published_at DESC LIMIT 10;

-- 查询热门标签
SELECT name, post_count FROM tags ORDER BY post_count DESC LIMIT 10;

-- 查询用户统计
SELECT * FROM user_stats WHERE post_count > 0;
```

### Medium (电商平台)

```sql
-- 查询热销商品
SELECT * FROM bestseller_products LIMIT 20;

-- 查询库存预警
SELECT * FROM low_stock_products;

-- 查询每日销售统计
SELECT * FROM daily_sales ORDER BY sale_date DESC LIMIT 7;

-- 查询客户销售统计
SELECT * FROM user_order_stats ORDER BY total_spent DESC LIMIT 10;
```

### Large (ERP系统)

```sql
-- 查询员工详情
SELECT * FROM hr.v_employee_details WHERE status = 'active' LIMIT 20;

-- 查询部门统计
SELECT * FROM public.v_department_stats;

-- 查询销售订单概览
SELECT * FROM sales.v_order_overview ORDER BY order_date DESC LIMIT 20;

-- 查询库存汇总
SELECT * FROM inventory.v_stock_summary WHERE is_low_stock = TRUE;

-- 查询公司仪表板
SELECT * FROM public.v_company_dashboard;
```

## 文件结构

```
fixtures/
├── docker-compose.yml     # Docker Compose 配置
├── Makefile               # 管理命令
├── README.md              # 本文档
├── small/
│   ├── 01_schema.sql      # 博客系统 schema
│   └── 02_data.sql        # 博客系统测试数据
├── medium/
│   ├── 01_schema.sql      # 电商平台 schema
│   └── 02_data.sql        # 电商平台测试数据
└── large/
    ├── 01_schema.sql      # ERP系统 schema
    └── 02_data.sql        # ERP系统测试数据
```
