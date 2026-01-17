# Natural Language Query Test Cases

This document contains natural language queries for testing the DB Query Tool's natural language to SQL conversion feature.

Based on the database schema in `test.sql`:

## Database Schema

### Tables

- **users**: id, name, email, password_hash, phone, address, city, country, active, role, created_at, updated_at
- **categories**: id, name, description, parent_id, sort_order, active, created_at
- **products**: id, sku, name, description, category_id, price, cost, stock_quantity, min_stock_level, weight, is_featured, is_active, created_at, updated_at
- **orders**: id, order_no, user_id, status, total, discount, tax, shipping_fee, shipping_address, shipping_city, shipping_country, payment_method, payment_status, notes, ordered_at, paid_at, shipped_at, delivered_at, created_at, updated_at
- **order_items**: id, order_id, product_id, quantity, unit_price, subtotal, created_at

### Views

- **v_active_users**: 活跃用户视图 (id, name, email, city, country, role, created_at)
- **v_user_order_summary**: 用户订单汇总 (user_id, user_name, email, order_count, total_spent, avg_order_value, last_order_date)
- **v_product_stats**: 商品销售统计 (product_id, sku, product_name, category_name, price, stock_quantity, total_sold, total_revenue)

### Enums

- **role**: admin, user, guest
- **status**: pending, confirmed, shipped, delivered, cancelled
- **payment_status**: unpaid, paid, refunded
- **payment_method**: alipay, wechat, credit_card, bank_transfer

---

## 1. Simple Queries (基础查询)

### 1.1 List all users
```
查询所有用户
```

### 1.2 Show all products
```
显示所有商品信息
```

### 1.3 Get all orders
```
列出所有订单
```

### 1.4 Show all categories
```
查询所有商品分类
```

### 1.5 View active users
```
查看活跃用户列表
```

---

## 2. Filtering Queries (过滤查询)

### 2.1 Active users only
```
查询所有活跃用户
```

### 2.2 Admin users
```
查询所有管理员用户
```

### 2.3 Users by city
```
查询北京的用户
```

### 2.4 Users by country
```
查询来自日本的用户
```

### 2.5 Featured products
```
查询所有精选商品
```

### 2.6 Products by category
```
查询手机通讯类别的商品
```

### 2.7 High-priced products
```
查询价格超过1000的商品
```

### 2.8 Products by price range
```
查询价格在500到2000之间的商品
```

### 2.9 Low stock products
```
查询库存少于50的商品
```

### 2.10 Products below minimum stock
```
查询库存低于最低库存水平的商品
```

### 2.11 Completed orders
```
查询所有已完成的订单
```

### 2.12 Pending orders
```
显示待处理的订单
```

### 2.13 Shipped orders
```
查询已发货的订单
```

### 2.14 Cancelled orders
```
查询已取消的订单
```

### 2.15 Orders by payment method
```
查询使用支付宝支付的订单
```

### 2.16 Paid orders
```
查询所有已支付的订单
```

### 2.17 Unpaid orders
```
查询未支付的订单
```

### 2.18 Root categories
```
查询所有一级分类
```

### 2.19 Sub-categories
```
查询电子产品下的子分类
```

---

## 3. Sorting Queries (排序查询)

### 3.1 Products by price descending
```
按价格从高到低显示所有商品
```

### 3.2 Products by price ascending
```
按价格从低到高显示商品
```

### 3.3 Latest orders first
```
按日期从新到旧显示订单
```

### 3.4 Users by registration date
```
按注册时间排序显示用户列表
```

### 3.5 Products by stock
```
按库存数量从少到多显示商品
```

### 3.6 Orders by total amount
```
按订单金额从高到低排序
```

### 3.7 Categories by sort order
```
按排序顺序显示分类
```

---

## 4. Aggregation Queries (聚合查询)

### 4.1 Count users
```
统计用户总数
```

### 4.2 Count active users
```
统计活跃用户数量
```

### 4.3 Count users by role
```
按角色统计用户数量
```

### 4.4 Count users by country
```
按国家统计用户数量
```

### 4.5 Average product price
```
计算商品的平均价格
```

### 4.6 Total order amount
```
计算所有订单的总金额
```

### 4.7 Products per category
```
统计每个类别有多少商品
```

### 4.8 Orders per status
```
按状态统计订单数量
```

### 4.9 Orders per payment method
```
按支付方式统计订单数量
```

### 4.10 Total revenue
```
计算总销售收入
```

### 4.11 Average order value
```
计算平均订单金额
```

### 4.12 Min and max product price
```
查询商品最高价和最低价
```

### 4.13 Total stock quantity
```
计算总库存数量
```

---

## 5. JOIN Queries (关联查询)

### 5.1 Orders with user names
```
显示订单信息以及对应的用户名
```

### 5.2 Order items with product details
```
查询订单项及其对应的商品名称和价格
```

### 5.3 Products with category names
```
显示商品及其分类名称
```

### 5.4 User purchase history
```
查询每个用户的购买记录
```

### 5.5 Orders with shipping info
```
显示订单及其收货地址信息
```

### 5.6 Category hierarchy
```
显示分类层级结构
```

---

## 6. Complex Aggregation (复杂聚合)

### 6.1 Total spent per user
```
计算每个用户的总消费金额
```

### 6.2 Best selling products
```
查询销量最高的前10个商品
```

### 6.3 Revenue by category
```
计算每个商品类别的总销售额
```

### 6.4 Average order value per user
```
计算每个用户的平均订单金额
```

### 6.5 Most ordered products
```
查询被订购次数最多的商品
```

### 6.6 Order count per user
```
统计每个用户的订单数量
```

### 6.7 Revenue per city
```
按城市统计销售额
```

### 6.8 Top customers by spending
```
查询消费金额最高的前5名客户
```

### 6.9 Product profit margin
```
计算每个商品的利润率
```

### 6.10 Average items per order
```
计算每个订单平均包含多少商品
```

---

## 7. Date-based Queries (日期查询)

### 7.1 Orders in specific month
```
查询2025年1月的所有订单
```

### 7.2 Recent orders
```
查询最近7天的订单
```

### 7.3 Recent orders 30 days
```
查询最近30天的订单
```

### 7.4 Users registered this month
```
查询本月注册的用户
```

### 7.5 Orders between dates
```
查询2025年1月1日到1月15日之间的订单
```

### 7.6 Today's orders
```
查询今天的订单
```

### 7.7 Orders in last year
```
查询去年的订单
```

### 7.8 Delivered orders last week
```
查询上周已送达的订单
```

---

## 8. Complex Business Queries (复杂业务查询)

### 8.1 Top spending customers
```
谁的订单总金额最高？显示前三名
```

### 8.2 Inactive users with orders
```
查询不活跃但有订单记录的用户
```

### 8.3 Products never ordered
```
查询从未被购买过的商品
```

### 8.4 Users without orders
```
查询没有任何订单的用户
```

### 8.5 Most popular categories
```
哪个商品类别的销售额最高
```

### 8.6 High value orders
```
查询金额超过5000的订单及其用户信息
```

### 8.7 Customer lifetime value
```
计算每个活跃用户的消费总额，按金额排序
```

### 8.8 Products with low stock alert
```
查询库存低于最低库存水平且仍在销售的商品
```

### 8.9 Users with multiple orders
```
查询下单次数超过3次的用户
```

### 8.10 Repeat customers
```
查询有多次购买记录的回头客
```

### 8.11 Orders with discounts
```
查询有折扣的订单
```

### 8.12 High shipping fee orders
```
查询运费超过15元的订单
```

### 8.13 Products by weight
```
查询重量超过1公斤的商品
```

### 8.14 Featured products by category
```
查询每个分类的精选商品
```

### 8.15 Guest users
```
查询所有游客用户
```

---

## 9. View Queries (视图查询)

### 9.1 User order summary
```
查询用户订单汇总信息
```

### 9.2 Product statistics
```
查询商品销售统计
```

### 9.3 Top revenue products
```
查询收入最高的前10个商品
```

### 9.4 Active users view
```
从活跃用户视图查询北京的用户
```

### 9.5 Users with high spending
```
查询总消费超过10000的用户
```

### 9.6 Best selling products from view
```
查询销量最高的商品
```

---

## 10. Subquery and Window Functions (子查询和窗口函数)

### 10.1 Users with above average spending
```
查询消费金额高于平均值的用户
```

### 10.2 Product price ranking
```
显示商品价格排名
```

### 10.3 Orders higher than user average
```
查询金额高于该用户平均订单金额的订单
```

### 10.4 Top product per category
```
查询每个分类中价格最高的商品
```

### 10.5 User order ranking
```
显示用户订单金额排名
```

---

## 11. Multi-condition Queries (多条件查询)

### 11.1 Active users with completed orders
```
查询有已完成订单的活跃用户
```

### 11.2 Electronics under 1000
```
查询价格低于1000的电子产品
```

### 11.3 High stock expensive items
```
查询库存充足且价格超过2000的商品
```

### 11.4 Recent large orders
```
查询最近30天金额超过1000的订单
```

### 11.5 Featured active products
```
查询精选且在售的商品
```

### 11.6 Paid orders with discount
```
查询已支付且有折扣的订单
```

### 11.7 Chinese users with orders
```
查询来自中国且有订单的用户
```

### 11.8 Delivered orders in Beijing
```
查询收货地址在北京的已送达订单
```

---

## 12. English Queries (英文查询)

### 12.1 Simple select
```
Show all users
```

### 12.2 With filter
```
Find products with price greater than 5000
```

### 12.3 Aggregation
```
What is the total revenue from all orders?
```

### 12.4 Join query
```
List all orders with customer names and order totals
```

### 12.5 Complex analysis
```
Which customer has placed the most orders?
```

### 12.6 Category analysis
```
Show the total sales amount for each product category
```

### 12.7 Stock analysis
```
Find products that are running low on stock
```

### 12.8 Order analysis
```
What is the average order value for delivered orders?
```

### 12.9 User location
```
Show all users from USA
```

### 12.10 Payment analysis
```
How many orders were paid with WeChat?
```

### 12.11 Featured products
```
List all featured products with their prices
```

### 12.12 Admin users
```
Show all admin users
```

---

## 13. Edge Cases (边界情况)

### 13.1 Ambiguous query
```
显示用户
```

### 13.2 Vague requirement
```
最贵的东西
```

### 13.3 Incomplete query
```
订单
```

### 13.4 Mixed language
```
Show all 用户
```

### 13.5 Typo query
```
查询所以用户
```

### 13.6 Minimal query
```
商品
```

---

## Expected SQL Examples

For reference, here are some expected SQL outputs:

| Natural Language | Expected SQL |
|------------------|--------------|
| 查询所有用户 | `SELECT * FROM users;` |
| 查询所有活跃用户 | `SELECT * FROM users WHERE active = true;` |
| 查询管理员用户 | `SELECT * FROM users WHERE role = 'admin';` |
| 按价格从高到低显示商品 | `SELECT * FROM products ORDER BY price DESC;` |
| 查询价格超过1000的商品 | `SELECT * FROM products WHERE price > 1000;` |
| 查询手机类商品 | `SELECT p.* FROM products p JOIN categories c ON p.category_id = c.id WHERE c.name = '手机通讯';` |
| 计算每个用户的总消费金额 | `SELECT u.id, u.name, SUM(o.total) as total_spent FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name;` |
| 谁的订单最多 | `SELECT u.name, COUNT(o.id) as order_count FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name ORDER BY order_count DESC LIMIT 1;` |
| 查询已支付的订单 | `SELECT * FROM orders WHERE payment_status = 'paid';` |
| 查询最近7天的订单 | `SELECT * FROM orders WHERE ordered_at >= NOW() - INTERVAL '7 days';` |
| 查询销量最高的商品 | `SELECT * FROM v_product_stats ORDER BY total_sold DESC LIMIT 10;` |
| 查询用户订单汇总 | `SELECT * FROM v_user_order_summary ORDER BY total_spent DESC;` |
| 查询库存不足的商品 | `SELECT * FROM products WHERE stock_quantity < min_stock_level;` |
| 查询精选商品 | `SELECT * FROM products WHERE is_featured = true AND is_active = true;` |
| 按城市统计用户数 | `SELECT city, COUNT(*) as user_count FROM users GROUP BY city ORDER BY user_count DESC;` |
