# ERP Database Schema Reference

**Database:** erp_db
**Connection:** localhost:5432, user: postgres, password: postgres

## Schemas

ERP系统采用多Schema设计，按业务模块划分：

- **public** - 核心表（公司、部门、用户、权限等）
- **hr** - 人力资源模块
- **sales** - 销售模块
- **procurement** - 采购模块
- **inventory** - 库存模块
- **finance** - 财务模块
- **production** - 生产模块

---

## Schema: public (核心模块)

### companies
公司表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| code | varchar | NO | | 公司编码（唯一） |
| name | varchar | NO | | 公司名称 |
| legal_name | varchar | YES | | 法人名称 |
| tax_id | varchar | YES | | 税号 |
| address | text | YES | | 地址 |
| city | varchar | YES | | 城市 |
| country | varchar | YES | 'China' | 国家 |
| phone | varchar | YES | | 电话 |
| email | varchar | YES | | 邮箱 |
| website | varchar | YES | | 网站 |
| founded_date | date | YES | | 成立日期 |
| employee_count | integer | YES | 0 | 员工数量 |
| status | record_status | YES | 'active' | 状态 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### departments
部门表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| parent_id | integer | YES | | 上级部门ID |
| code | varchar | NO | | 部门编码 |
| name | varchar | NO | | 部门名称 |
| description | text | YES | | 描述 |
| manager_id | integer | YES | | 部门经理ID（关联hr.employees） |
| level | integer | YES | 1 | 层级 |
| path | varchar | YES | | 层级路径 |
| sort_order | integer | YES | 0 | 排序 |
| budget | numeric | YES | | 预算 |
| cost_center | varchar | YES | | 成本中心 |
| status | record_status | YES | 'active' | 状态 |
| created_at | timestamptz | YES | now() | 创建时间 |

### positions
职位表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| department_id | integer | YES | | 部门ID |
| code | varchar | NO | | 职位编码 |
| title | varchar | NO | | 职位名称 |
| description | text | YES | | 职位描述 |
| requirements | text | YES | | 任职要求 |
| salary_min | numeric | YES | | 最低薪资 |
| salary_max | numeric | YES | | 最高薪资 |
| headcount | integer | YES | 1 | 编制人数 |
| current_count | integer | YES | 0 | 当前人数 |
| level | integer | YES | 1 | 职级 |
| status | record_status | YES | 'active' | 状态 |
| created_at | timestamptz | YES | now() | 创建时间 |

### locations
办公地点表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| code | varchar | NO | | 地点编码 |
| name | varchar | NO | | 地点名称 |
| address | text | YES | | 地址 |
| city | varchar | YES | | 城市 |
| province | varchar | YES | | 省份 |
| postal_code | varchar | YES | | 邮编 |
| country | varchar | YES | 'China' | 国家 |
| latitude | numeric | YES | | 纬度 |
| longitude | numeric | YES | | 经度 |
| timezone | varchar | YES | 'Asia/Shanghai' | 时区 |
| is_headquarters | boolean | YES | false | 是否总部 |
| status | record_status | YES | 'active' | 状态 |
| created_at | timestamptz | YES | now() | 创建时间 |

### users
系统用户表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | uuid | NO | uuid_generate_v4() | 主键 |
| username | varchar | NO | | 用户名（唯一） |
| email | varchar | NO | | 邮箱（唯一） |
| password_hash | varchar | NO | | 密码哈希 |
| employee_id | integer | YES | | 关联员工ID |
| is_active | boolean | YES | true | 是否启用 |
| is_superuser | boolean | YES | false | 是否超级管理员 |
| last_login | timestamptz | YES | | 最后登录时间 |
| login_count | integer | YES | 0 | 登录次数 |
| failed_login_count | integer | YES | 0 | 失败登录次数 |
| locked_until | timestamptz | YES | | 锁定截止时间 |
| password_changed_at | timestamptz | YES | | 密码修改时间 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### roles / permissions / role_permissions / user_roles
权限相关表

**roles:**
| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| code | varchar | 角色编码（唯一） |
| name | varchar | 角色名称 |
| description | text | 描述 |
| is_system | boolean | 是否系统角色 |

**permissions:**
| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| code | varchar | 权限编码（唯一） |
| name | varchar | 权限名称 |
| module | varchar | 所属模块 |
| description | text | 描述 |

**role_permissions:** (role_id, permission_id)
**user_roles:** (user_id, role_id, granted_at, granted_by)

### audit_logs
审计日志表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO | auto increment | 主键 |
| user_id | uuid | YES | | 操作用户ID |
| action | varchar | NO | | 操作类型 |
| table_name | varchar | NO | | 操作表名 |
| record_id | varchar | YES | | 记录ID |
| old_values | jsonb | YES | | 旧值 |
| new_values | jsonb | YES | | 新值 |
| ip_address | inet | YES | | IP地址 |
| user_agent | text | YES | | User Agent |
| created_at | timestamptz | YES | now() | 创建时间 |

---

## Schema: hr (人力资源)

### hr.employees
员工表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| employee_no | varchar | NO | | 员工工号 |
| first_name | varchar | NO | | 名 |
| last_name | varchar | NO | | 姓 |
| full_name | varchar | YES | | 全名 |
| gender | gender | YES | | 性别 |
| birth_date | date | YES | | 出生日期 |
| id_number | varchar | YES | | 身份证号 |
| phone | varchar | YES | | 手机 |
| email | varchar | YES | | 工作邮箱 |
| personal_email | varchar | YES | | 个人邮箱 |
| address | text | YES | | 地址 |
| emergency_contact | varchar | YES | | 紧急联系人 |
| emergency_phone | varchar | YES | | 紧急联系电话 |
| department_id | integer | YES | | 部门ID |
| position_id | integer | YES | | 职位ID |
| manager_id | integer | YES | | 直属上级ID |
| location_id | integer | YES | | 工作地点ID |
| hire_date | date | NO | | 入职日期 |
| probation_end_date | date | YES | | 试用期结束日期 |
| contract_type | contract_type | YES | | 合同类型 |
| contract_end_date | date | YES | | 合同结束日期 |
| education_level | education_level | YES | | 学历 |
| major | varchar | YES | | 专业 |
| graduation_year | integer | YES | | 毕业年份 |
| base_salary | numeric | YES | | 基本工资 |
| status | employee_status | YES | 'active' | 员工状态 |
| termination_date | date | YES | | 离职日期 |
| termination_reason | text | YES | | 离职原因 |
| photo_url | varchar | YES | | 照片URL |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### hr.attendance
考勤表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | bigint | NO | auto increment | 主键 |
| employee_id | integer | NO | | 员工ID |
| attendance_date | date | NO | | 日期 |
| check_in | timestamptz | YES | | 签到时间 |
| check_out | timestamptz | YES | | 签退时间 |
| work_hours | numeric | YES | | 工作时长 |
| overtime_hours | numeric | YES | | 加班时长 |
| attendance_type | attendance_type | YES | 'normal' | 考勤类型 |
| location_id | integer | YES | | 签到地点ID |
| notes | text | YES | | 备注 |
| created_at | timestamptz | YES | now() | 创建时间 |

### hr.leave_requests / hr.leave_balances
请假申请及假期余额表

**leave_requests:**
| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| employee_id | integer | 员工ID |
| leave_type | leave_type | 请假类型 |
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |
| days | numeric | 请假天数 |
| reason | text | 请假原因 |
| status | varchar | 状态 |
| approved_by | integer | 审批人ID |
| approved_at | timestamptz | 审批时间 |

**leave_balances:**
| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| employee_id | integer | 员工ID |
| year | integer | 年份 |
| leave_type | leave_type | 假期类型 |
| entitled_days | numeric | 应得天数 |
| used_days | numeric | 已用天数 |
| carried_over | numeric | 结转天数 |
| remaining_days | numeric | 剩余天数 |

### hr.payroll
工资表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| employee_id | integer | NO | | 员工ID |
| pay_period | varchar | NO | | 工资期间（如2024-01） |
| base_salary | numeric | NO | | 基本工资 |
| overtime_pay | numeric | YES | | 加班费 |
| bonus | numeric | YES | | 奖金 |
| allowances | numeric | YES | | 津贴 |
| deductions | numeric | YES | | 扣款 |
| tax | numeric | YES | | 个税 |
| social_insurance | numeric | YES | | 社保 |
| housing_fund | numeric | YES | | 公积金 |
| net_salary | numeric | NO | | 实发工资 |
| payment_date | date | YES | | 发放日期 |
| payment_status | varchar | YES | | 发放状态 |
| created_at | timestamptz | YES | now() | 创建时间 |

### hr.performance_reviews
绩效评估表

### hr.employee_contracts
员工合同表

### hr.employee_skills
员工技能表

### hr.training_courses / hr.training_records
培训课程及记录表

### hr.job_postings / hr.job_applications
招聘职位及应聘记录表

---

## Schema: sales (销售)

### sales.customers
客户表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| customer_code | varchar | NO | | 客户编码 |
| name | varchar | NO | | 客户名称 |
| legal_name | varchar | YES | | 法人名称 |
| tax_id | varchar | YES | | 税号 |
| customer_type | varchar | YES | | 客户类型 |
| industry | varchar | YES | | 行业 |
| contact_person | varchar | YES | | 联系人 |
| phone | varchar | YES | | 电话 |
| email | varchar | YES | | 邮箱 |
| billing_address | text | YES | | 账单地址 |
| shipping_address | text | YES | | 收货地址 |
| city | varchar | YES | | 城市 |
| country | varchar | YES | | 国家 |
| credit_limit | numeric | YES | | 信用额度 |
| current_balance | numeric | YES | | 当前余额 |
| payment_terms | integer | YES | | 付款周期（天） |
| currency | varchar | YES | | 币种 |
| sales_rep_id | integer | YES | | 销售代表ID |
| price_list_id | integer | YES | | 价格表ID |
| discount_rate | numeric | YES | | 折扣率 |
| status | record_status | YES | 'active' | 状态 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### sales.sales_orders
销售订单表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| order_no | varchar | NO | | 订单号 |
| customer_id | integer | NO | | 客户ID |
| order_date | date | NO | | 订单日期 |
| requested_date | date | YES | | 要求交货日期 |
| promised_date | date | YES | | 承诺交货日期 |
| warehouse_id | integer | YES | | 发货仓库ID |
| sales_rep_id | integer | YES | | 销售代表ID |
| currency | varchar | YES | | 币种 |
| exchange_rate | numeric | YES | | 汇率 |
| subtotal | numeric | YES | | 小计 |
| discount_amount | numeric | YES | | 折扣金额 |
| tax_amount | numeric | YES | | 税额 |
| shipping_amount | numeric | YES | | 运费 |
| total_amount | numeric | YES | | 总金额 |
| shipping_address | text | YES | | 收货地址 |
| shipping_method | varchar | YES | | 配送方式 |
| payment_terms | integer | YES | | 付款周期 |
| notes | text | YES | | 备注 |
| internal_notes | text | YES | | 内部备注 |
| status | order_status | YES | 'draft' | 订单状态 |
| approved_by | integer | YES | | 审批人ID |
| approved_at | timestamptz | YES | | 审批时间 |
| created_by | integer | YES | | 创建人ID |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### sales.sales_order_lines
销售订单明细表

### sales.quotations
报价单表

### sales.shipments / sales.shipment_lines
发货单及明细表

### sales.sales_returns
销售退货表

### sales.price_lists
价格表

---

## Schema: procurement (采购)

### procurement.suppliers
供应商表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| supplier_code | varchar | NO | | 供应商编码 |
| name | varchar | NO | | 供应商名称 |
| legal_name | varchar | YES | | 法人名称 |
| tax_id | varchar | YES | | 税号 |
| supplier_type | varchar | YES | | 供应商类型 |
| industry | varchar | YES | | 行业 |
| contact_person | varchar | YES | | 联系人 |
| phone | varchar | YES | | 电话 |
| email | varchar | YES | | 邮箱 |
| address | text | YES | | 地址 |
| city | varchar | YES | | 城市 |
| country | varchar | YES | | 国家 |
| payment_terms | integer | YES | | 付款周期 |
| currency | varchar | YES | | 币种 |
| rating | integer | YES | | 评级 |
| current_balance | numeric | YES | | 当前余额 |
| bank_name | varchar | YES | | 开户银行 |
| bank_account | varchar | YES | | 银行账号 |
| status | record_status | YES | 'active' | 状态 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### procurement.purchase_orders
采购订单表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| po_no | varchar | NO | | 采购订单号 |
| supplier_id | integer | NO | | 供应商ID |
| order_date | date | NO | | 订单日期 |
| expected_date | date | YES | | 预计到货日期 |
| warehouse_id | integer | YES | | 收货仓库ID |
| buyer_id | integer | YES | | 采购员ID |
| currency | varchar | YES | | 币种 |
| exchange_rate | numeric | YES | | 汇率 |
| subtotal | numeric | YES | | 小计 |
| tax_amount | numeric | YES | | 税额 |
| shipping_amount | numeric | YES | | 运费 |
| total_amount | numeric | YES | | 总金额 |
| payment_terms | integer | YES | | 付款周期 |
| shipping_address | text | YES | | 收货地址 |
| notes | text | YES | | 备注 |
| internal_notes | text | YES | | 内部备注 |
| status | po_status | YES | 'draft' | 订单状态 |
| approved_by | integer | YES | | 审批人ID |
| approved_at | timestamptz | YES | | 审批时间 |
| created_by | integer | YES | | 创建人ID |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### procurement.purchase_order_lines
采购订单明细表

### procurement.goods_receipts / procurement.goods_receipt_lines
收货单及明细表

### procurement.supplier_products
供应商产品价格表

---

## Schema: inventory (库存)

### inventory.warehouses
仓库表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| code | varchar | NO | | 仓库编码 |
| name | varchar | NO | | 仓库名称 |
| location_id | integer | YES | | 地点ID |
| address | text | YES | | 地址 |
| contact_person | varchar | YES | | 联系人 |
| contact_phone | varchar | YES | | 联系电话 |
| capacity | integer | YES | | 容量 |
| is_active | boolean | YES | true | 是否启用 |
| created_at | timestamptz | YES | now() | 创建时间 |

### inventory.storage_locations
库位表

| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| warehouse_id | integer | 仓库ID |
| code | varchar | 库位编码 |
| zone | varchar | 区域 |
| aisle | varchar | 通道 |
| rack | varchar | 货架 |
| shelf | varchar | 层 |
| bin | varchar | 格 |
| capacity | integer | 容量 |
| is_active | boolean | 是否启用 |

### inventory.products
产品/物料表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| sku | varchar | NO | | SKU编码 |
| name | varchar | NO | | 产品名称 |
| description | text | YES | | 描述 |
| category_id | integer | YES | | 分类ID |
| brand | varchar | YES | | 品牌 |
| uom | varchar | YES | | 计量单位 |
| weight | numeric | YES | | 重量 |
| weight_unit | varchar | YES | | 重量单位 |
| dimensions | varchar | YES | | 尺寸 |
| barcode | varchar | YES | | 条形码 |
| is_serialized | boolean | YES | false | 是否序列号管理 |
| is_batch_tracked | boolean | YES | false | 是否批次管理 |
| minimum_stock | integer | YES | | 最低库存 |
| reorder_point | integer | YES | | 再订货点 |
| reorder_quantity | integer | YES | | 再订货量 |
| lead_time_days | integer | YES | | 前置天数 |
| standard_cost | numeric | YES | | 标准成本 |
| last_cost | numeric | YES | | 最近成本 |
| selling_price | numeric | YES | | 销售价格 |
| tax_rate | numeric | YES | | 税率 |
| status | record_status | YES | 'active' | 状态 |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### inventory.product_categories
产品分类表

### inventory.stock
库存表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| product_id | integer | NO | | 产品ID |
| warehouse_id | integer | NO | | 仓库ID |
| location_id | integer | YES | | 库位ID |
| lot_number | varchar | YES | | 批次号 |
| serial_number | varchar | YES | | 序列号 |
| quantity_on_hand | numeric | NO | | 现有数量 |
| quantity_reserved | numeric | YES | 0 | 预留数量 |
| quantity_available | numeric | YES | | 可用数量 |
| last_count_date | date | YES | | 最后盘点日期 |
| expiry_date | date | YES | | 过期日期 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### inventory.stock_movements
库存移动表

| Column | Type | Description |
|--------|------|-------------|
| id | bigint | 主键 |
| company_id | integer | 公司ID |
| movement_no | varchar | 移动单号 |
| movement_type | movement_type | 移动类型（in/out/transfer/adjustment） |
| movement_date | timestamptz | 移动日期 |
| product_id | integer | 产品ID |
| from_warehouse_id | integer | 源仓库ID |
| from_location_id | integer | 源库位ID |
| to_warehouse_id | integer | 目标仓库ID |
| to_location_id | integer | 目标库位ID |
| quantity | numeric | 数量 |
| lot_number | varchar | 批次号 |
| serial_number | varchar | 序列号 |
| unit_cost | numeric | 单位成本 |
| total_cost | numeric | 总成本 |
| reference_type | varchar | 关联类型 |
| reference_id | integer | 关联ID |
| reason | text | 原因 |
| created_by | integer | 创建人ID |
| created_at | timestamptz | 创建时间 |

### inventory.stock_counts / inventory.stock_count_lines
盘点单及明细表

---

## Schema: finance (财务)

### finance.chart_of_accounts
会计科目表

| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| company_id | integer | 公司ID |
| account_code | varchar | 科目编码 |
| account_name | varchar | 科目名称 |
| account_type | account_type | 科目类型（asset/liability/equity/revenue/expense） |
| parent_id | integer | 上级科目ID |
| level | integer | 层级 |
| is_header | boolean | 是否汇总科目 |
| currency | varchar | 币种 |
| description | text | 描述 |
| status | record_status | 状态 |

### finance.fiscal_periods
会计期间表

### finance.vouchers / finance.voucher_lines
凭证及明细表

| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| company_id | integer | 公司ID |
| voucher_no | varchar | 凭证号 |
| voucher_type | voucher_type | 凭证类型（receipt/payment/transfer/general） |
| voucher_date | date | 凭证日期 |
| fiscal_period_id | integer | 会计期间ID |
| description | text | 摘要 |
| total_debit | numeric | 借方合计 |
| total_credit | numeric | 贷方合计 |
| status | varchar | 状态 |
| prepared_by | integer | 制单人 |
| reviewed_by | integer | 审核人 |
| approved_by | integer | 审批人 |

### finance.invoices
发票表

### finance.payments
付款表

### finance.bank_accounts
银行账户表

### finance.bank_transactions
银行流水表

### finance.budgets
预算表

### finance.account_balances
科目余额表

---

## Schema: production (生产)

### production.bom / production.bom_lines
BOM物料清单及明细表

| Column | Type | Description |
|--------|------|-------------|
| id | integer | 主键 |
| company_id | integer | 公司ID |
| bom_no | varchar | BOM编号 |
| product_id | integer | 产品ID |
| version | varchar | 版本 |
| standard_quantity | numeric | 标准产量 |
| uom | varchar | 计量单位 |
| effective_date | date | 生效日期 |
| expiry_date | date | 失效日期 |
| is_active | boolean | 是否启用 |

**bom_lines:**
- component_id - 组件产品ID
- quantity - 用量
- scrap_rate - 损耗率
- is_critical - 是否关键物料

### production.work_orders
生产工单表

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | integer | NO | auto increment | 主键 |
| company_id | integer | NO | | 公司ID |
| wo_no | varchar | NO | | 工单号 |
| product_id | integer | NO | | 产品ID |
| bom_id | integer | YES | | BOM ID |
| sales_order_id | integer | YES | | 销售订单ID |
| planned_quantity | numeric | NO | | 计划数量 |
| completed_quantity | numeric | YES | 0 | 完工数量 |
| scrapped_quantity | numeric | YES | 0 | 报废数量 |
| uom | varchar | YES | | 计量单位 |
| warehouse_id | integer | YES | | 仓库ID |
| planned_start | date | YES | | 计划开始日期 |
| planned_end | date | YES | | 计划结束日期 |
| actual_start | timestamptz | YES | | 实际开始时间 |
| actual_end | timestamptz | YES | | 实际结束时间 |
| priority | integer | YES | 0 | 优先级 |
| status | work_order_status | YES | 'planned' | 工单状态 |
| notes | text | YES | | 备注 |
| created_by | integer | YES | | 创建人ID |
| created_at | timestamptz | YES | now() | 创建时间 |
| updated_at | timestamptz | YES | now() | 更新时间 |

### production.wo_material_consumption
工单物料消耗表

### production.quality_inspections / production.qc_checkpoints
质量检验及检查点表

---

## Enum Types

### record_status
记录状态
- `active` - 活跃
- `inactive` - 不活跃
- `deleted` - 已删除
- `archived` - 已归档

### gender
性别
- `male` - 男
- `female` - 女
- `other` - 其他

### contract_type
合同类型
- `full_time` - 全职
- `part_time` - 兼职
- `contract` - 合同工
- `internship` - 实习
- `consultant` - 顾问

### employee_status
员工状态
- `active` - 在职
- `on_leave` - 休假中
- `resigned` - 已离职
- `terminated` - 已解雇
- `retired` - 已退休

### education_level
学历
- `high_school` - 高中
- `associate` - 大专
- `bachelor` - 本科
- `master` - 硕士
- `doctorate` - 博士
- `other` - 其他

### attendance_type
考勤类型
- `normal` - 正常
- `late` - 迟到
- `early_leave` - 早退
- `absent` - 缺勤
- `business_trip` - 出差
- `remote` - 远程办公

### leave_type
请假类型
- `annual` - 年假
- `sick` - 病假
- `personal` - 事假
- `maternity` - 产假
- `paternity` - 陪产假
- `marriage` - 婚假
- `bereavement` - 丧假
- `unpaid` - 无薪假

### order_status (sales)
销售订单状态
- `draft` - 草稿
- `confirmed` - 已确认
- `processing` - 处理中
- `shipped` - 已发货
- `delivered` - 已交付
- `cancelled` - 已取消
- `returned` - 已退货

### po_status
采购订单状态
- `draft` - 草稿
- `pending_approval` - 待审批
- `approved` - 已审批
- `ordered` - 已下单
- `partial_received` - 部分收货
- `received` - 已收货
- `cancelled` - 已取消

### movement_type
库存移动类型
- `in` - 入库
- `out` - 出库
- `transfer` - 调拨
- `adjustment` - 调整
- `return` - 退货

### payment_status
付款状态
- `pending` - 待付款
- `partial` - 部分付款
- `paid` - 已付款
- `overdue` - 逾期
- `refunded` - 已退款

### account_type
会计科目类型
- `asset` - 资产
- `liability` - 负债
- `equity` - 所有者权益
- `revenue` - 收入
- `expense` - 费用

### voucher_type
凭证类型
- `receipt` - 收款
- `payment` - 付款
- `transfer` - 转账
- `general` - 通用

### work_order_status
工单状态
- `planned` - 计划中
- `released` - 已下发
- `in_progress` - 进行中
- `completed` - 已完成
- `cancelled` - 已取消
- `on_hold` - 暂停

### qc_result
质检结果
- `pass` - 通过
- `fail` - 不通过
- `conditional` - 有条件通过
- `pending` - 待检

---

## Views

### v_department_stats
部门统计视图 - 包含员工数、薪资总额、预算等

### v_company_dashboard
公司仪表盘视图 - 汇总员工数、客户数、供应商数、产品数、月销售额、月采购额等

---

## Common Query Patterns

### 获取部门下的所有员工
```sql
SELECT e.* FROM hr.employees e
WHERE e.department_id = $1 AND e.status = 'active'
ORDER BY e.employee_no;
```

### 获取员工的请假记录
```sql
SELECT lr.*, e.full_name as employee_name
FROM hr.leave_requests lr
JOIN hr.employees e ON lr.employee_id = e.id
WHERE lr.employee_id = $1
ORDER BY lr.start_date DESC;
```

### 获取客户的订单统计
```sql
SELECT c.id, c.name,
  COUNT(so.id) as order_count,
  SUM(so.total_amount) as total_amount
FROM sales.customers c
LEFT JOIN sales.sales_orders so ON c.id = so.customer_id
WHERE c.company_id = $1
GROUP BY c.id;
```

### 获取低库存产品
```sql
SELECT p.*, s.quantity_on_hand, s.quantity_available
FROM inventory.products p
JOIN inventory.stock s ON p.id = s.product_id
WHERE s.quantity_available <= p.reorder_point
AND p.status = 'active';
```

### 获取销售订单及明细
```sql
SELECT so.*,
  (SELECT json_agg(sol.*) FROM sales.sales_order_lines sol WHERE sol.order_id = so.id) as lines
FROM sales.sales_orders so
WHERE so.id = $1;
```

### 按月统计销售额
```sql
SELECT
  DATE_TRUNC('month', order_date) as month,
  COUNT(*) as order_count,
  SUM(total_amount) as total_sales
FROM sales.sales_orders
WHERE company_id = $1 AND status NOT IN ('draft', 'cancelled')
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month DESC;
```
