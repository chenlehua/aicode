# PostgreSQL MCP Server - 自然语言查询测试用例

本文档包含针对三个测试数据库的自然语言查询问题，用于测试 pg-mcp 的 SQL 生成能力。

---

## 1. Small Database - 博客系统 (blog_db)

### 1.1 简单查询（单表，无条件或简单条件）

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| S1 | 查询所有用户 | SELECT * FROM users |
| S2 | 有多少篇文章？ | COUNT |
| S3 | 查询所有标签 | SELECT * FROM tags |
| S4 | 查询所有分类 | SELECT * FROM categories |
| S5 | 有多少个用户？ | COUNT |
| S6 | 查询所有已发布的文章 | WHERE status = 'published' |
| S7 | 查询所有评论 | SELECT * FROM comments |
| S8 | 显示前10个用户 | LIMIT |

### 1.2 条件查询（单表，复杂条件）

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| S9 | 查询状态为活跃的用户 | WHERE status = 'active' |
| S10 | 查询浏览量超过1000的文章 | WHERE view_count > 1000 |
| S11 | 查询点赞数大于50的文章 | WHERE like_count > 50 |
| S12 | 查询最近30天发布的文章 | WHERE + 日期计算 |
| S13 | 查询用户名包含"dev"的用户 | WHERE + LIKE |
| S14 | 查询精选文章 | WHERE is_featured = TRUE |
| S15 | 查询置顶文章 | WHERE is_pinned = TRUE |
| S16 | 查询草稿状态的文章 | WHERE status = 'draft' |

### 1.3 排序和分页

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| S17 | 查询浏览量最高的10篇文章 | ORDER BY + LIMIT |
| S18 | 查询最新发布的5篇文章 | ORDER BY published_at DESC + LIMIT |
| S19 | 查询点赞最多的文章 | ORDER BY like_count DESC |
| S20 | 查询评论最多的文章 | ORDER BY comment_count DESC |
| S21 | 查询最早注册的用户 | ORDER BY created_at ASC |
| S22 | 查询文章数量最多的前5个标签 | ORDER BY post_count DESC + LIMIT |

### 1.4 聚合查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| S23 | 统计每个分类下有多少篇文章 | GROUP BY + COUNT |
| S24 | 统计每个用户发布了多少篇文章 | GROUP BY + COUNT |
| S25 | 计算所有文章的平均浏览量 | AVG |
| S26 | 查询总点赞数 | SUM |
| S27 | 统计每种文章状态的数量 | GROUP BY status + COUNT |
| S28 | 查询每个用户的总浏览量 | GROUP BY + SUM |
| S29 | 统计每月发布的文章数量 | GROUP BY + 日期截断 |

### 1.5 关联查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| S30 | 查询每篇文章及其作者名称 | JOIN users |
| S31 | 查询每篇文章的分类名称 | JOIN categories |
| S32 | 查询每个标签关联的文章标题 | JOIN post_tags + JOIN posts |
| S33 | 查询每条评论的作者和文章标题 | 多表 JOIN |
| S34 | 查询用户"alice_dev"发布的所有文章 | JOIN + WHERE |
| S35 | 查询"技术"分类下的所有文章 | JOIN + WHERE |
| S36 | 查询某篇文章的所有评论及评论者 | JOIN + WHERE |

### 1.6 子查询和复杂查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| S37 | 查询没有发布任何文章的用户 | NOT EXISTS / NOT IN |
| S38 | 查询收藏数最多的文章 | 子查询或 JOIN + GROUP BY |
| S39 | 查询互相关注的用户对 | 自连接 |
| S40 | 查询被收藏超过5次的文章 | HAVING |
| S41 | 查询每个分类下浏览量最高的文章 | 窗口函数或子查询 |
| S42 | 查询关注者最多的5个用户 | GROUP BY + ORDER BY + LIMIT |
| S43 | 查询评论数超过平均值的文章 | 子查询比较 |

### 1.7 使用视图

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| S44 | 查询热门文章排行 | 使用 trending_posts 视图 |
| S45 | 查询用户统计信息 | 使用 user_stats 视图 |
| S46 | 查询发布文章最多的用户 | 使用 user_stats 视图 + ORDER BY |
| S47 | 查询总浏览量最高的用户 | 使用 user_stats 视图 + ORDER BY |

---

## 2. Medium Database - 电商平台 (ecommerce_db)

### 2.1 简单查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M1 | 查询所有商品 | SELECT * FROM products |
| M2 | 有多少个店铺？ | COUNT stores |
| M3 | 查询所有品牌 | SELECT * FROM brands |
| M4 | 有多少个客户？ | COUNT users WHERE role = 'customer' |
| M5 | 查询所有优惠券 | SELECT * FROM coupons |
| M6 | 查询所有订单 | SELECT * FROM orders |
| M7 | 有多少种商品分类？ | COUNT categories |

### 2.2 条件查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M8 | 查询价格超过1000元的商品 | WHERE price > 1000 |
| M9 | 查询库存不足10件的商品 | WHERE stock_quantity < 10 |
| M10 | 查询已认证的店铺 | WHERE is_verified = TRUE |
| M11 | 查询精选商品 | WHERE is_featured = TRUE |
| M12 | 查询已完成的订单 | WHERE status = 'delivered' |
| M13 | 查询已取消的订单 | WHERE status = 'cancelled' |
| M14 | 查询有效的优惠券 | WHERE is_active = TRUE AND expires_at > NOW() |
| M15 | 查询评分高于4.5的商品 | WHERE rating > 4.5 |
| M16 | 查询5星好评 | WHERE rating = 5 |

### 2.3 排序和分页

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M17 | 查询销量最高的10个商品 | ORDER BY sold_count DESC + LIMIT |
| M18 | 查询最贵的商品 | ORDER BY price DESC + LIMIT 1 |
| M19 | 查询最便宜的商品 | ORDER BY price ASC + LIMIT 1 |
| M20 | 查询评分最高的商品 | ORDER BY rating DESC |
| M21 | 查询最新上架的20个商品 | ORDER BY created_at DESC + LIMIT |
| M22 | 查询评论数最多的商品 | ORDER BY review_count DESC |
| M23 | 查询金额最大的订单 | ORDER BY total_amount DESC + LIMIT |

### 2.4 聚合查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M24 | 统计每个品牌有多少商品 | GROUP BY brand_id + COUNT |
| M25 | 统计每个分类的商品数量 | GROUP BY category_id + COUNT |
| M26 | 计算所有商品的平均价格 | AVG(price) |
| M27 | 统计每个店铺的订单总额 | GROUP BY store_id + SUM |
| M28 | 统计每种订单状态的数量 | GROUP BY status + COUNT |
| M29 | 计算每个客户的订单总金额 | GROUP BY user_id + SUM |
| M30 | 统计每天的订单数量 | GROUP BY DATE(created_at) + COUNT |
| M31 | 统计每个月的销售总额 | GROUP BY + 月份 + SUM |
| M32 | 计算每个商品的平均评分 | GROUP BY product_id + AVG |

### 2.5 关联查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M33 | 查询每个订单的客户信息 | JOIN users |
| M34 | 查询每个商品的店铺名称 | JOIN stores |
| M35 | 查询每个商品的品牌名称 | JOIN brands |
| M36 | 查询订单中包含的商品详情 | JOIN order_items + JOIN products |
| M37 | 查询每个商品的评论内容 | JOIN reviews |
| M38 | 查询Apple品牌的所有商品 | JOIN brands + WHERE |
| M39 | 查询某个店铺的所有订单 | JOIN + WHERE |
| M40 | 查询使用了优惠券的订单 | WHERE coupon_id IS NOT NULL |

### 2.6 复杂业务查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M41 | 查询库存预警商品（库存低于阈值） | WHERE stock_quantity <= low_stock_threshold |
| M42 | 查询每个客户的消费总额和订单数 | GROUP BY + 多聚合 |
| M43 | 查询复购率最高的商品 | 复杂聚合 |
| M44 | 查询每个分类的销售额排名 | GROUP BY + JOIN + ORDER BY |
| M45 | 查询过去7天的销售趋势 | 日期范围 + GROUP BY |
| M46 | 查询未支付的订单 | WHERE status = 'pending' |
| M47 | 查询已发货但未送达的订单 | WHERE status = 'shipped' |
| M48 | 查询退款订单及原因 | JOIN refunds |
| M49 | 查询每个店铺的平均评分 | GROUP BY store_id + AVG |
| M50 | 查询每个城市的订单分布 | GROUP BY + 地址解析 |

### 2.7 使用视图

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M51 | 查询热销商品排行榜 | 使用 bestseller_products 视图 |
| M52 | 查询库存预警商品列表 | 使用 low_stock_products 视图 |
| M53 | 查询每日销售统计 | 使用 daily_sales 视图 |
| M54 | 查询客户消费统计 | 使用 user_order_stats 视图 |
| M55 | 查询店铺销售统计 | 使用 store_sales_stats 视图 |
| M56 | 查询优惠券使用情况 | 使用 coupon_usage_stats 视图 |
| M57 | 查询在售商品列表 | 使用 active_products 视图 |

### 2.8 高级查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| M58 | 查询购买过某商品的用户还购买了什么 | 协同过滤逻辑 |
| M59 | 查询从未下单的用户 | NOT EXISTS |
| M60 | 查询订单金额高于平均值的订单 | 子查询比较 |
| M61 | 查询每个分类下销量最高的商品 | 窗口函数 |
| M62 | 查询连续7天都有订单的店铺 | 复杂日期逻辑 |
| M63 | 查询商品价格变化历史 | 如果有历史表 |

---

## 3. Large Database - 企业 ERP 系统 (erp_db)

### 3.1 人力资源模块 (HR)

#### 简单查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L1 | 查询所有员工 | SELECT * FROM hr.employees |
| L2 | 有多少个员工？ | COUNT |
| L3 | 查询所有部门 | SELECT * FROM public.departments |
| L4 | 查询所有职位 | SELECT * FROM public.positions |
| L5 | 查询在职员工数量 | WHERE status = 'active' |
| L6 | 查询所有培训课程 | SELECT * FROM hr.training_courses |

#### 条件和关联查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L7 | 查询研发部的所有员工 | JOIN departments + WHERE |
| L8 | 查询工资超过10万的员工 | WHERE base_salary > 100000 |
| L9 | 查询2020年之后入职的员工 | WHERE hire_date >= '2020-01-01' |
| L10 | 查询正在休假的员工 | WHERE status = 'on_leave' |
| L11 | 查询每个部门的员工数量 | GROUP BY department_id + COUNT |
| L12 | 查询每个部门的平均工资 | GROUP BY + AVG |
| L13 | 查询工资最高的10个员工 | ORDER BY base_salary DESC + LIMIT |
| L14 | 查询每个员工的部门和职位信息 | 多表 JOIN |
| L15 | 查询没有直属下级的员工 | NOT EXISTS 或 LEFT JOIN |

#### 考勤和薪资

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L16 | 查询今天的考勤记录 | WHERE attendance_date = CURRENT_DATE |
| L17 | 查询本月迟到的员工 | WHERE attendance_type = 'late' + 日期范围 |
| L18 | 统计每个员工本月的工作小时数 | GROUP BY + SUM |
| L19 | 查询上个月的薪资发放记录 | WHERE pay_period = 上月 |
| L20 | 查询待审批的请假申请 | WHERE status = 'pending' |
| L21 | 统计每种请假类型的申请数量 | GROUP BY leave_type + COUNT |
| L22 | 查询每个员工的剩余年假天数 | 查询 leave_balances |
| L23 | 查询加班时间最多的员工 | GROUP BY + SUM + ORDER BY |

#### 招聘和培训

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L24 | 查询正在招聘的职位 | WHERE status = 'open' |
| L25 | 查询每个职位的申请人数 | GROUP BY posting_id + COUNT |
| L26 | 查询待面试的候选人 | WHERE status = 'interview_scheduled' |
| L27 | 查询参加过某培训课程的员工 | JOIN training_records |
| L28 | 查询培训通过率 | 聚合计算 |

### 3.2 财务模块 (Finance)

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L29 | 查询所有银行账户 | SELECT * FROM finance.bank_accounts |
| L30 | 查询每个银行账户的余额 | SELECT current_balance |
| L31 | 查询本月的所有凭证 | WHERE + 日期范围 |
| L32 | 查询待审核的凭证 | WHERE status = 'pending' |
| L33 | 查询每个会计科目的余额 | 查询 account_balances |
| L34 | 查询本月的收入总额 | SUM + WHERE 收入科目 |
| L35 | 查询本月的支出总额 | SUM + WHERE 费用科目 |
| L36 | 查询待支付的发票 | WHERE payment_status = 'pending' |
| L37 | 查询逾期未付的发票 | WHERE payment_status = 'overdue' |
| L38 | 查询每个部门的预算执行情况 | JOIN budgets |

### 3.3 库存模块 (Inventory)

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L39 | 查询所有仓库 | SELECT * FROM inventory.warehouses |
| L40 | 查询所有产品/物料 | SELECT * FROM inventory.products |
| L41 | 查询每个仓库的库存总量 | GROUP BY warehouse_id + SUM |
| L42 | 查询库存不足的物料 | WHERE quantity < reorder_point |
| L43 | 查询需要补货的物料 | WHERE quantity_available <= reorder_point |
| L44 | 查询每个产品的库存分布 | GROUP BY product_id, warehouse_id |
| L45 | 查询最近的库存移动记录 | ORDER BY movement_date DESC |
| L46 | 查询盘点差异大于0的记录 | WHERE variance != 0 |
| L47 | 查询某仓库的所有库位 | WHERE warehouse_id = X |

### 3.4 销售模块 (Sales)

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L48 | 查询所有客户 | SELECT * FROM sales.customers |
| L49 | 查询VIP客户 | WHERE customer_type = 'vip' |
| L50 | 查询本月的销售订单 | WHERE + 日期范围 |
| L51 | 查询每个客户的订单总额 | GROUP BY customer_id + SUM |
| L52 | 查询每个销售员的业绩 | GROUP BY sales_rep_id + SUM |
| L53 | 查询待发货的订单 | WHERE status = 'confirmed' |
| L54 | 查询已发货未签收的订单 | WHERE status = 'shipped' |
| L55 | 查询销售额最高的客户 | ORDER BY + LIMIT |
| L56 | 查询本月的销售退货 | WHERE + 日期范围 |
| L57 | 查询有效的报价单 | WHERE valid_until >= CURRENT_DATE |

### 3.5 采购模块 (Procurement)

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L58 | 查询所有供应商 | SELECT * FROM procurement.suppliers |
| L59 | 查询评级最高的供应商 | ORDER BY rating DESC |
| L60 | 查询待审批的采购订单 | WHERE status = 'pending_approval' |
| L61 | 查询每个供应商的采购总额 | GROUP BY supplier_id + SUM |
| L62 | 查询待收货的采购订单 | WHERE status = 'ordered' |
| L63 | 查询部分收货的采购订单 | WHERE status = 'partial_received' |
| L64 | 查询某个物料的供应商列表 | 查询 supplier_products |
| L65 | 查询哪个供应商的某物料价格最低 | ORDER BY unit_price ASC |

### 3.6 生产模块 (Production)

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L66 | 查询所有生产工单 | SELECT * FROM production.work_orders |
| L67 | 查询进行中的生产工单 | WHERE status = 'in_progress' |
| L68 | 查询已完成的生产工单 | WHERE status = 'completed' |
| L69 | 查询某产品的BOM（物料清单） | 查询 bom + bom_lines |
| L70 | 查询每个产品的BOM成本 | 聚合计算组件成本 |
| L71 | 查询质检不合格的记录 | WHERE result = 'fail' |
| L72 | 查询质检合格率 | 聚合计算 |
| L73 | 查询逾期未完成的工单 | WHERE planned_end < CURRENT_DATE AND status != 'completed' |

### 3.7 跨模块复杂查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L74 | 查询每个公司的员工总数和平均工资 | GROUP BY company_id + 多聚合 |
| L75 | 查询销售额最高的部门 | 关联销售订单和员工部门 |
| L76 | 查询本月销售额与上月对比 | 复杂日期计算 |
| L77 | 查询库存周转率 | 复杂业务计算 |
| L78 | 查询从采购到入库的平均时间 | 日期差计算 |
| L79 | 查询每个客户的应收账款账龄 | 使用 v_ar_aging 视图 |
| L80 | 查询每个供应商的应付账款账龄 | 使用 v_ap_aging 视图 |

### 3.8 使用视图

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| L81 | 查看公司仪表板数据 | 使用 v_company_dashboard 视图 |
| L82 | 查看员工详细信息 | 使用 hr.v_employee_details 视图 |
| L83 | 查看部门统计 | 使用 v_department_stats 视图 |
| L84 | 查看月度考勤统计 | 使用 hr.v_monthly_attendance 视图 |
| L85 | 查看销售订单概览 | 使用 sales.v_order_overview 视图 |
| L86 | 查看库存汇总 | 使用 inventory.v_stock_summary 视图 |
| L87 | 查看低库存预警 | 使用 inventory.v_low_stock_alert 视图 |
| L88 | 查看采购订单概览 | 使用 procurement.v_po_overview 视图 |
| L89 | 查看供应商统计 | 使用 procurement.v_supplier_stats 视图 |
| L90 | 查看质检统计 | 使用 production.v_qc_stats 视图 |

---

## 4. 边界情况和特殊查询

### 4.1 空结果处理

| # | 自然语言问题 | 说明 |
|---|-------------|------|
| E1 | 查询2030年的订单 | 应返回空结果 |
| E2 | 查询价格超过一百万的商品 | 可能返回空结果 |
| E3 | 查询用户名为"不存在的用户"的信息 | 应返回空结果 |

### 4.2 模糊查询

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| E4 | 查询名字中包含"科技"的公司 | LIKE '%科技%' |
| E5 | 查询邮箱以"gmail.com"结尾的用户 | LIKE '%gmail.com' |
| E6 | 查询标题包含"Python"的文章 | ILIKE '%python%' |

### 4.3 日期范围

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| E7 | 查询过去一周的订单 | WHERE created_at >= NOW() - INTERVAL '7 days' |
| E8 | 查询上个季度的销售数据 | 日期范围计算 |
| E9 | 查询今年的所有入职员工 | WHERE EXTRACT(YEAR FROM hire_date) = 当年 |
| E10 | 查询工作日的考勤记录 | 排除周末 |

### 4.4 NULL 值处理

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| E11 | 查询没有分配部门的员工 | WHERE department_id IS NULL |
| E12 | 查询没有经理的员工 | WHERE manager_id IS NULL |
| E13 | 查询没有设置价格的商品 | WHERE price IS NULL |

### 4.5 多条件组合

| # | 自然语言问题 | 预期查询类型 |
|---|-------------|-------------|
| E14 | 查询价格在100到500之间且评分高于4的商品 | WHERE + AND + BETWEEN |
| E15 | 查询北京或上海的客户 | WHERE + OR |
| E16 | 查询已发布且浏览量超过1000的精选文章 | WHERE + AND + AND |
| E17 | 查询本月下单且已完成的VIP客户订单 | 多条件组合 |

---

## 5. 测试注意事项

### 5.1 SQL 安全验证

以下查询应该被 pg-mcp 拒绝执行：

| # | 危险查询 | 应拒绝原因 |
|---|---------|-----------|
| X1 | 删除所有用户 | DELETE 操作 |
| X2 | 更新商品价格为0 | UPDATE 操作 |
| X3 | 创建新表 | CREATE 操作 |
| X4 | 删除数据库 | DROP 操作 |
| X5 | 查询用户密码 | 敏感信息 |

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
