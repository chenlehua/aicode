# E-commerce Database Schema Reference

**Database:** ecommerce_db
**Connection:** localhost:5432, user: postgres, password: postgres

## Tables

### users
用户表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO | uuid_generate_v4() | 主键 |
| email | varchar | NO | | 邮箱（唯一） |
| password_hash | varchar | NO | | 密码哈希 |
| phone | varchar | YES | | 手机号 |
| first_name | varchar | YES | | 名 |
| last_name | varchar | YES | | 姓 |
| avatar_url | varchar | YES | | 头像URL |
| role | user_role | NO | 'customer' | 用户角色 |
| status | account_status | NO | 'pending_verification' | 账户状态 |
| email_verified | boolean | YES | false | 邮箱是否验证 |
| phone_verified | boolean | YES | false | 手机是否验证 |
| last_login_at | timestamptz | YES | | 最后登录时间 |
| login_count | integer | YES | 0 | 登录次数 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### user_addresses
用户地址表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| user_id | uuid | NO | | 用户ID |
| address_type | address_type | NO | 'both' | 地址类型 |
| recipient_name | varchar | NO | | 收件人姓名 |
| phone | varchar | NO | | 联系电话 |
| province | varchar | NO | | 省份 |
| city | varchar | NO | | 城市 |
| district | varchar | YES | | 区县 |
| street_address | varchar | NO | | 详细地址 |
| postal_code | varchar | YES | | 邮政编码 |
| is_default | boolean | YES | false | 是否默认地址 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### stores
店铺表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| owner_id | uuid | NO | | 店主用户ID |
| name | varchar | NO | | 店铺名称 |
| slug | varchar | NO | | URL标识（唯一） |
| description | text | YES | | 店铺描述 |
| logo_url | varchar | YES | | Logo URL |
| banner_url | varchar | YES | | 横幅图URL |
| contact_email | varchar | YES | | 联系邮箱 |
| contact_phone | varchar | YES | | 联系电话 |
| business_license | varchar | YES | | 营业执照号 |
| rating | numeric | YES | 0.00 | 店铺评分 |
| review_count | integer | YES | 0 | 评价数量 |
| is_verified | boolean | YES | false | 是否已认证 |
| is_featured | boolean | YES | false | 是否推荐 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### categories
商品分类表（支持多级）

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| parent_id | integer | YES | | 父分类ID |
| name | varchar | NO | | 分类名称 |
| slug | varchar | NO | | URL标识（唯一） |
| description | text | YES | | 分类描述 |
| icon_url | varchar | YES | | 图标URL |
| image_url | varchar | YES | | 图片URL |
| sort_order | integer | YES | 0 | 排序顺序 |
| is_active | boolean | YES | true | 是否启用 |
| product_count | integer | YES | 0 | 商品数量 |
| level | integer | NO | 1 | 分类层级 |
| path | varchar | YES | | 分类路径 |
| created_at | timestamptz | YES | now() | 创建时间 |

### brands
品牌表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| name | varchar | NO | | 品牌名称（唯一） |
| slug | varchar | NO | | URL标识（唯一） |
| logo_url | varchar | YES | | Logo URL |
| description | text | YES | | 品牌描述 |
| website_url | varchar | YES | | 官网URL |
| country | varchar | YES | | 所属国家 |
| is_featured | boolean | YES | false | 是否推荐 |
| product_count | integer | YES | 0 | 商品数量 |
| created_at | timestamptz | YES | now() | 创建时间 |

### products
商品表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| store_id | integer | NO | | 店铺ID |
| category_id | integer | YES | | 分类ID |
| brand_id | integer | YES | | 品牌ID |
| sku | varchar | NO | | SKU编码（唯一） |
| name | varchar | NO | | 商品名称 |
| slug | varchar | NO | | URL标识（唯一） |
| short_description | varchar | YES | | 简短描述 |
| description | text | YES | | 详细描述 |
| price | numeric | NO | | 销售价格 |
| compare_at_price | numeric | YES | | 原价（用于显示折扣） |
| cost_price | numeric | YES | | 成本价 |
| status | product_status | NO | 'draft' | 商品状态 |
| stock_quantity | integer | NO | 0 | 库存数量 |
| low_stock_threshold | integer | YES | 10 | 低库存阈值 |
| weight | numeric | YES | | 重量 |
| length | numeric | YES | | 长度 |
| width | numeric | YES | | 宽度 |
| height | numeric | YES | | 高度 |
| is_featured | boolean | YES | false | 是否推荐 |
| is_taxable | boolean | YES | true | 是否含税 |
| tax_rate | numeric | YES | 0.00 | 税率 |
| view_count | integer | YES | 0 | 浏览次数 |
| sold_count | integer | YES | 0 | 销售数量 |
| rating | numeric | YES | 0.00 | 商品评分 |
| review_count | integer | YES | 0 | 评价数量 |
| meta_title | varchar | YES | | SEO标题 |
| meta_description | varchar | YES | | SEO描述 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### product_variants
商品变体表（如不同颜色、尺寸）

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| product_id | integer | NO | | 商品ID |
| sku | varchar | NO | | 变体SKU（唯一） |
| name | varchar | NO | | 变体名称 |
| price | numeric | YES | | 变体价格（为空则用商品价格） |
| stock_quantity | integer | NO | 0 | 库存数量 |
| weight | numeric | YES | | 重量 |
| option1_name | varchar | YES | | 选项1名称（如"颜色"） |
| option1_value | varchar | YES | | 选项1值（如"红色"） |
| option2_name | varchar | YES | | 选项2名称（如"尺寸"） |
| option2_value | varchar | YES | | 选项2值（如"XL"） |
| option3_name | varchar | YES | | 选项3名称 |
| option3_value | varchar | YES | | 选项3值 |
| image_url | varchar | YES | | 变体图片URL |
| is_active | boolean | YES | true | 是否启用 |
| created_at | timestamptz | YES | now() | 创建时间 |

### product_images
商品图片表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| product_id | integer | NO | | 商品ID |
| url | varchar | NO | | 图片URL |
| alt_text | varchar | YES | | 图片描述 |
| sort_order | integer | YES | 0 | 排序顺序 |
| is_primary | boolean | YES | false | 是否主图 |
| created_at | timestamptz | YES | now() | 创建时间 |

### product_tags / product_tag_relations
商品标签及关联表

**product_tags:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| name | varchar | NO | | 标签名称（唯一） |
| slug | varchar | NO | | URL标识（唯一） |
| product_count | integer | YES | 0 | 商品数量 |
| created_at | timestamptz | YES | now() | 创建时间 |

**product_tag_relations:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| product_id | integer | NO | | 商品ID |
| tag_id | integer | NO | | 标签ID |

### carts / cart_items
购物车及购物车项表

**carts:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| user_id | uuid | YES | | 用户ID（游客可为空） |
| session_id | varchar | YES | | 会话ID（游客使用） |
| total_items | integer | YES | 0 | 商品总数 |
| subtotal | numeric | YES | 0.00 | 小计金额 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |
| expires_at | timestamptz | YES | | 过期时间 |

**cart_items:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| cart_id | integer | NO | | 购物车ID |
| product_id | integer | NO | | 商品ID |
| variant_id | integer | YES | | 变体ID |
| quantity | integer | NO | 1 | 数量 |
| unit_price | numeric | NO | | 单价 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### orders
订单表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| order_number | varchar | NO | | 订单号（唯一） |
| user_id | uuid | NO | | 用户ID |
| store_id | integer | NO | | 店铺ID |
| status | order_status | NO | 'pending' | 订单状态 |
| subtotal | numeric | NO | | 商品小计 |
| discount_amount | numeric | YES | 0.00 | 折扣金额 |
| shipping_fee | numeric | YES | 0.00 | 运费 |
| tax_amount | numeric | YES | 0.00 | 税额 |
| total_amount | numeric | NO | | 订单总额 |
| coupon_id | integer | YES | | 使用的优惠券ID |
| coupon_code | varchar | YES | | 优惠券码 |
| shipping_name | varchar | YES | | 收件人姓名 |
| shipping_phone | varchar | YES | | 收件人电话 |
| shipping_address | text | YES | | 收货地址 |
| shipping_method | varchar | YES | | 配送方式 |
| tracking_number | varchar | YES | | 物流单号 |
| notes | text | YES | | 订单备注 |
| paid_at | timestamptz | YES | | 支付时间 |
| shipped_at | timestamptz | YES | | 发货时间 |
| delivered_at | timestamptz | YES | | 签收时间 |
| cancelled_at | timestamptz | YES | | 取消时间 |
| cancel_reason | text | YES | | 取消原因 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### order_items
订单项表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| order_id | integer | NO | | 订单ID |
| product_id | integer | NO | | 商品ID |
| variant_id | integer | YES | | 变体ID |
| product_name | varchar | NO | | 商品名称（快照） |
| variant_name | varchar | YES | | 变体名称（快照） |
| sku | varchar | NO | | SKU |
| quantity | integer | NO | | 数量 |
| unit_price | numeric | NO | | 单价 |
| total_price | numeric | NO | | 总价 |
| created_at | timestamptz | YES | now() | 创建时间 |

### payments
支付表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| order_id | integer | NO | | 订单ID |
| payment_number | varchar | NO | | 支付单号（唯一） |
| payment_method | payment_method | NO | | 支付方式 |
| amount | numeric | NO | | 支付金额 |
| status | payment_status | NO | 'pending' | 支付状态 |
| transaction_id | varchar | YES | | 第三方交易ID |
| gateway_response | jsonb | YES | | 网关响应 |
| paid_at | timestamptz | YES | | 支付时间 |
| refunded_at | timestamptz | YES | | 退款时间 |
| created_at | timestamptz | YES | now() | 创建时间 |

### refunds
退款表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| order_id | integer | NO | | 订单ID |
| payment_id | integer | YES | | 支付ID |
| refund_number | varchar | NO | | 退款单号（唯一） |
| amount | numeric | NO | | 退款金额 |
| reason | text | NO | | 退款原因 |
| status | varchar | NO | 'pending' | 退款状态 |
| approved_by | uuid | YES | | 审批人ID |
| approved_at | timestamptz | YES | | 审批时间 |
| completed_at | timestamptz | YES | | 完成时间 |
| created_at | timestamptz | YES | now() | 创建时间 |

### coupons
优惠券表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| code | varchar | NO | | 优惠券码（唯一） |
| name | varchar | NO | | 优惠券名称 |
| description | text | YES | | 描述 |
| coupon_type | coupon_type | NO | | 优惠券类型 |
| discount_value | numeric | NO | | 折扣值 |
| minimum_order_amount | numeric | YES | 0.00 | 最低订单金额 |
| maximum_discount | numeric | YES | | 最大折扣金额 |
| usage_limit | integer | YES | | 总使用次数限制 |
| usage_count | integer | YES | 0 | 已使用次数 |
| per_user_limit | integer | YES | 1 | 每用户使用限制 |
| starts_at | timestamptz | NO | | 生效时间 |
| expires_at | timestamptz | NO | | 过期时间 |
| is_active | boolean | YES | true | 是否启用 |
| created_at | timestamptz | YES | now() | 创建时间 |

### user_coupons
用户领取的优惠券

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| user_id | uuid | NO | | 用户ID |
| coupon_id | integer | NO | | 优惠券ID |
| used_count | integer | YES | 0 | 已使用次数 |
| claimed_at | timestamptz | YES | now() | 领取时间 |

### reviews
商品评价表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| product_id | integer | NO | | 商品ID |
| user_id | uuid | NO | | 用户ID |
| order_id | integer | YES | | 订单ID |
| rating | integer | NO | | 评分(1-5) |
| title | varchar | YES | | 评价标题 |
| content | text | YES | | 评价内容 |
| pros | text | YES | | 优点 |
| cons | text | YES | | 缺点 |
| images | jsonb | YES | | 评价图片 |
| is_verified_purchase | boolean | YES | false | 是否已购买验证 |
| is_featured | boolean | YES | false | 是否精选 |
| helpful_count | integer | YES | 0 | 有用数 |
| reply | text | YES | | 商家回复 |
| replied_at | timestamptz | YES | | 回复时间 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### wishlists
收藏表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| user_id | uuid | NO | | 用户ID |
| product_id | integer | NO | | 商品ID |
| created_at | timestamptz | YES | now() | 创建时间 |

### browse_history
浏览历史表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| user_id | uuid | YES | | 用户ID |
| session_id | varchar | YES | | 会话ID |
| product_id | integer | NO | | 商品ID |
| viewed_at | timestamptz | YES | now() | 浏览时间 |

### promotions / promotion_products
促销活动及关联表

**promotions:**
| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| name | varchar | NO | | 活动名称 |
| description | text | YES | | 活动描述 |
| promotion_type | varchar | NO | | 促销类型 |
| discount_type | varchar | NO | | 折扣类型 |
| discount_value | numeric | NO | | 折扣值 |
| minimum_purchase | numeric | YES | 0.00 | 最低消费 |
| maximum_discount | numeric | YES | | 最大折扣 |
| starts_at | timestamptz | NO | | 开始时间 |
| ends_at | timestamptz | NO | | 结束时间 |
| is_active | boolean | YES | true | 是否启用 |
| priority | integer | YES | 0 | 优先级 |
| created_at | timestamptz | YES | now() | 创建时间 |

### inventory_logs
库存变动日志表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| product_id | integer | NO | | 商品ID |
| variant_id | integer | YES | | 变体ID |
| change_quantity | integer | NO | | 变动数量（正为入库，负为出库） |
| previous_quantity | integer | NO | | 变动前数量 |
| new_quantity | integer | NO | | 变动后数量 |
| change_type | varchar | NO | | 变动类型（sale, return, adjustment等） |
| reference_type | varchar | YES | | 关联类型（order, refund等） |
| reference_id | integer | YES | | 关联ID |
| notes | text | YES | | 备注 |
| created_by | uuid | YES | | 操作人ID |
| created_at | timestamptz | YES | now() | 创建时间 |

### settings
系统设置表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| key | varchar | NO | | 设置键（唯一） |
| value | text | YES | | 设置值 |
| value_type | varchar | NO | 'string' | 值类型 |
| description | text | YES | | 描述 |
| is_public | boolean | YES | false | 是否公开 |
| updated_at | timestamptz | YES | now() | 更新时间 |

## Enum Types

### user_role
用户角色
- `customer` - 顾客
- `seller` - 卖家
- `admin` - 管理员
- `support` - 客服

### account_status
账户状态
- `active` - 活跃
- `inactive` - 不活跃
- `suspended` - 已暂停
- `pending_verification` - 待验证

### address_type
地址类型
- `shipping` - 收货地址
- `billing` - 账单地址
- `both` - 两者兼用

### product_status
商品状态
- `draft` - 草稿
- `active` - 上架
- `out_of_stock` - 缺货
- `discontinued` - 已下架

### order_status
订单状态
- `pending` - 待付款
- `paid` - 已付款
- `processing` - 处理中
- `shipped` - 已发货
- `delivered` - 已签收
- `cancelled` - 已取消
- `refunded` - 已退款

### payment_method
支付方式
- `credit_card` - 信用卡
- `debit_card` - 借记卡
- `alipay` - 支付宝
- `wechat_pay` - 微信支付
- `bank_transfer` - 银行转账
- `cod` - 货到付款

### payment_status
支付状态
- `pending` - 待支付
- `completed` - 已完成
- `failed` - 失败
- `refunded` - 已退款
- `cancelled` - 已取消

### coupon_type
优惠券类型
- `percentage` - 百分比折扣
- `fixed_amount` - 固定金额
- `free_shipping` - 免运费
- `buy_x_get_y` - 买X送Y

## Views

### active_products
上架商品视图（包含店铺、分类、品牌信息）

### bestseller_products
畅销商品视图（按销量排序，前100名）

### low_stock_products
低库存商品视图

### order_summary
订单汇总视图（包含用户、店铺信息）

### daily_sales
每日销售统计视图

### product_sales_stats
商品销售统计视图

### store_sales_stats
店铺销售统计视图

### user_order_stats
用户订单统计视图

### category_product_stats
分类商品统计视图

### coupon_usage_stats
优惠券使用统计视图

## Common Query Patterns

### 商品搜索（支持模糊匹配）
```sql
SELECT * FROM products
WHERE status = 'active'
AND name ILIKE '%keyword%'
ORDER BY sold_count DESC;
```

### 获取分类下的商品（包含子分类）
```sql
WITH RECURSIVE category_tree AS (
  SELECT id FROM categories WHERE id = $1
  UNION ALL
  SELECT c.id FROM categories c
  JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT p.* FROM products p
WHERE p.category_id IN (SELECT id FROM category_tree)
AND p.status = 'active';
```

### 获取用户的订单列表
```sql
SELECT o.*,
  (SELECT json_agg(oi.*) FROM order_items oi WHERE oi.order_id = o.id) as items
FROM orders o
WHERE o.user_id = $1
ORDER BY o.created_at DESC;
```

### 商品销售排行
```sql
SELECT p.id, p.name, p.sold_count, p.rating
FROM products p
WHERE p.status = 'active'
ORDER BY p.sold_count DESC
LIMIT 10;
```

### 店铺销售统计
```sql
SELECT s.id, s.name,
  COUNT(o.id) as order_count,
  SUM(o.total_amount) as total_sales
FROM stores s
LEFT JOIN orders o ON s.id = o.store_id
  AND o.status NOT IN ('cancelled', 'refunded')
GROUP BY s.id;
```
