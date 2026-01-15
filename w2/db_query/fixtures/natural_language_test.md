# Natural Language Query Test Cases

This document contains natural language queries for testing the DB Query Tool's natural language to SQL conversion feature.

Based on the database schema in `test.sql`:
- **users**: id, name, email, active, created_at, updated_at
- **products**: id, name, description, price, stock_quantity, category, created_at
- **orders**: id, user_id, total, status, order_date
- **order_items**: id, order_id, product_id, quantity, unit_price

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

---

## 2. Filtering Queries (过滤查询)

### 2.1 Active users only
```
查询所有活跃用户
```

### 2.2 Products by category
```
查询所有电子产品类别的商品
```

### 2.3 High-priced products
```
查询价格超过100的商品
```

### 2.4 Completed orders
```
查询所有已完成的订单
```

### 2.5 Pending orders
```
显示待处理的订单
```

### 2.6 Low stock products
```
查询库存少于50的商品
```

---

## 3. Sorting Queries (排序查询)

### 3.1 Products by price descending
```
按价格从高到低显示所有商品
```

### 3.2 Latest orders first
```
按日期从新到旧显示订单
```

### 3.3 Users by registration date
```
按注册时间排序显示用户列表
```

---

## 4. Aggregation Queries (聚合查询)

### 4.1 Count users
```
统计用户总数
```

### 4.2 Average product price
```
计算商品的平均价格
```

### 4.3 Total order amount
```
计算所有订单的总金额
```

### 4.4 Products per category
```
统计每个类别有多少商品
```

### 4.5 Orders per status
```
按状态统计订单数量
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

### 5.3 User purchase history
```
查询每个用户的购买记录
```

---

## 6. Complex Aggregation (复杂聚合)

### 6.1 Total spent per user
```
计算每个用户的总消费金额
```

### 6.2 Best selling products
```
查询销量最高的前5个商品
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

---

## 7. Date-based Queries (日期查询)

### 7.1 Orders in February 2024
```
查询2024年2月的所有订单
```

### 7.2 Recent orders
```
查询最近7天的订单
```

### 7.3 Users registered this month
```
查询本月注册的用户
```

### 7.4 Orders between dates
```
查询2024年2月1日到2月10日之间的订单
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

### 8.6 Average items per order
```
计算每个订单平均包含多少商品
```

### 8.7 High value orders
```
查询金额超过500的订单及其用户信息
```

### 8.8 Customer lifetime value
```
计算每个活跃用户的消费总额，按金额排序
```

---

## 9. Subquery and Window Functions (子查询和窗口函数)

### 9.1 Users with above average spending
```
查询消费金额高于平均值的用户
```

### 9.2 Product price ranking
```
显示商品价格排名
```

### 9.3 Orders higher than user average
```
查询金额高于该用户平均订单金额的订单
```

---

## 10. Multi-condition Queries (多条件查询)

### 10.1 Active users with completed orders
```
查询有已完成订单的活跃用户
```

### 10.2 Electronics under 100
```
查询价格低于100的电子产品
```

### 10.3 High stock expensive items
```
查询库存充足且价格超过200的商品
```

### 10.4 Recent large orders
```
查询2024年2月金额超过100的订单
```

---

## 11. English Queries (英文查询)

### 11.1 Simple select
```
Show all users
```

### 11.2 With filter
```
Find products with price greater than 500
```

### 11.3 Aggregation
```
What is the total revenue from all orders?
```

### 11.4 Join query
```
List all orders with customer names and order totals
```

### 11.5 Complex analysis
```
Which customer has placed the most orders?
```

### 11.6 Category analysis
```
Show the total sales amount for each product category
```

### 11.7 Stock analysis
```
Find products that are running low on stock (less than 50 items)
```

### 11.8 Order analysis
```
What is the average order value for completed orders?
```

---

## 12. Edge Cases (边界情况)

### 12.1 Ambiguous query
```
显示用户
```

### 12.2 Vague requirement
```
最贵的东西
```

### 12.3 Incomplete query
```
订单
```

### 12.4 Mixed language
```
Show all 用户
```

---

## Expected SQL Examples

For reference, here are some expected SQL outputs:

| Natural Language | Expected SQL |
|------------------|--------------|
| 查询所有用户 | `SELECT * FROM users;` |
| 查询所有活跃用户 | `SELECT * FROM users WHERE active = true;` |
| 按价格从高到低显示商品 | `SELECT * FROM products ORDER BY price DESC;` |
| 计算每个用户的总消费金额 | `SELECT u.id, u.name, SUM(o.total) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name;` |
| 谁的订单最多 | `SELECT u.name, COUNT(o.id) as order_count FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name ORDER BY order_count DESC LIMIT 1;` |
