-- =====================================================
-- Large Test Database: Enterprise ERP System
-- 企业 ERP 系统测试数据库（大型）
-- Tables: 55+ | Views: 20+ | Types: 15+ | Indexes: 100+
-- Modules: HR, Finance, Inventory, Sales, Procurement, Production
-- =====================================================

-- 清理现有对象
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;

-- 创建业务模块 schemas
CREATE SCHEMA hr;          -- 人力资源
CREATE SCHEMA finance;     -- 财务
CREATE SCHEMA inventory;   -- 库存
CREATE SCHEMA sales;       -- 销售
CREATE SCHEMA procurement; -- 采购
CREATE SCHEMA production;  -- 生产

-- =====================================================
-- 扩展 (Extensions)
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- =====================================================
-- 自定义类型 (Custom Types) - 15+ types
-- =====================================================

-- 通用状态
CREATE TYPE public.record_status AS ENUM ('active', 'inactive', 'deleted', 'archived');

-- 员工状态
CREATE TYPE hr.employee_status AS ENUM ('active', 'on_leave', 'resigned', 'terminated', 'retired');

-- 合同类型
CREATE TYPE hr.contract_type AS ENUM ('full_time', 'part_time', 'contract', 'internship', 'consultant');

-- 性别
CREATE TYPE hr.gender AS ENUM ('male', 'female', 'other');

-- 学历
CREATE TYPE hr.education_level AS ENUM ('high_school', 'associate', 'bachelor', 'master', 'doctorate', 'other');

-- 考勤类型
CREATE TYPE hr.attendance_type AS ENUM ('normal', 'late', 'early_leave', 'absent', 'business_trip', 'remote');

-- 请假类型
CREATE TYPE hr.leave_type AS ENUM ('annual', 'sick', 'personal', 'maternity', 'paternity', 'marriage', 'bereavement', 'unpaid');

-- 账户类型
CREATE TYPE finance.account_type AS ENUM ('asset', 'liability', 'equity', 'revenue', 'expense');

-- 凭证类型
CREATE TYPE finance.voucher_type AS ENUM ('receipt', 'payment', 'transfer', 'general');

-- 库存移动类型
CREATE TYPE inventory.movement_type AS ENUM ('in', 'out', 'transfer', 'adjustment', 'return');

-- 订单状态
CREATE TYPE sales.order_status AS ENUM ('draft', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'returned');

-- 支付状态
CREATE TYPE sales.payment_status AS ENUM ('pending', 'partial', 'paid', 'overdue', 'refunded');

-- 采购订单状态
CREATE TYPE procurement.po_status AS ENUM ('draft', 'pending_approval', 'approved', 'ordered', 'partial_received', 'received', 'cancelled');

-- 生产订单状态
CREATE TYPE production.work_order_status AS ENUM ('planned', 'released', 'in_progress', 'completed', 'cancelled', 'on_hold');

-- 质检结果
CREATE TYPE production.qc_result AS ENUM ('pass', 'fail', 'conditional', 'pending');

-- =====================================================
-- 公共模块表 (10 tables)
-- =====================================================

-- 1. 公司信息
CREATE TABLE public.companies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200),
    tax_id VARCHAR(50),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'China',
    phone VARCHAR(30),
    email VARCHAR(100),
    website VARCHAR(200),
    founded_date DATE,
    employee_count INTEGER DEFAULT 0,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE public.companies IS '公司/法人实体表';

-- 2. 部门
CREATE TABLE public.departments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    parent_id INTEGER REFERENCES departments(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    manager_id INTEGER,
    level INTEGER DEFAULT 1,
    path VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    budget DECIMAL(15,2),
    cost_center VARCHAR(20),
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

COMMENT ON TABLE public.departments IS '部门/组织架构表';

-- 3. 职位
CREATE TABLE public.positions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    department_id INTEGER REFERENCES departments(id),
    code VARCHAR(20) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    requirements TEXT,
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    headcount INTEGER DEFAULT 1,
    current_count INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

COMMENT ON TABLE public.positions IS '职位表';

-- 4. 地点/办公地点
CREATE TABLE public.locations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    province VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50) DEFAULT 'China',
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    is_headquarters BOOLEAN DEFAULT FALSE,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

COMMENT ON TABLE public.locations IS '地点/办公地点表';

-- 5. 系统用户
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    employee_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    failed_login_count INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE public.users IS '系统用户表';

-- 6. 角色
CREATE TABLE public.roles (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE public.roles IS '角色表';

-- 7. 权限
CREATE TABLE public.permissions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE public.permissions IS '权限表';

-- 8. 用户角色关联
CREATE TABLE public.user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);

-- 9. 角色权限关联
CREATE TABLE public.role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- 10. 审计日志
CREATE TABLE public.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE public.audit_logs IS '审计日志表';

-- =====================================================
-- 人力资源模块表 (12 tables)
-- =====================================================

-- 11. 员工
CREATE TABLE hr.employees (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    employee_no VARCHAR(20) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED,
    gender hr.gender,
    birth_date DATE,
    id_number VARCHAR(30),
    phone VARCHAR(20),
    email VARCHAR(100),
    personal_email VARCHAR(100),
    address TEXT,
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    department_id INTEGER REFERENCES public.departments(id),
    position_id INTEGER REFERENCES public.positions(id),
    manager_id INTEGER REFERENCES hr.employees(id),
    location_id INTEGER REFERENCES public.locations(id),
    hire_date DATE NOT NULL,
    probation_end_date DATE,
    contract_type hr.contract_type DEFAULT 'full_time',
    contract_end_date DATE,
    education_level hr.education_level,
    major VARCHAR(100),
    graduation_year INTEGER,
    base_salary DECIMAL(12,2),
    status hr.employee_status DEFAULT 'active',
    termination_date DATE,
    termination_reason TEXT,
    photo_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, employee_no)
);

COMMENT ON TABLE hr.employees IS '员工信息表';

-- 更新部门表的 manager_id 外键
ALTER TABLE public.departments ADD CONSTRAINT fk_dept_manager 
    FOREIGN KEY (manager_id) REFERENCES hr.employees(id);

-- 更新用户表的 employee_id 外键
ALTER TABLE public.users ADD CONSTRAINT fk_user_employee 
    FOREIGN KEY (employee_id) REFERENCES hr.employees(id);

-- 12. 员工合同
CREATE TABLE hr.employee_contracts (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    contract_no VARCHAR(50) NOT NULL UNIQUE,
    contract_type hr.contract_type NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    salary DECIMAL(12,2),
    probation_salary DECIMAL(12,2),
    probation_months INTEGER DEFAULT 0,
    working_hours_per_week DECIMAL(4,1) DEFAULT 40,
    annual_leave_days INTEGER DEFAULT 0,
    sick_leave_days INTEGER DEFAULT 0,
    terms TEXT,
    signed_date DATE,
    signed_by INTEGER REFERENCES hr.employees(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE hr.employee_contracts IS '员工合同表';

-- 13. 考勤记录
CREATE TABLE hr.attendance (
    id BIGSERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    attendance_date DATE NOT NULL,
    check_in TIMESTAMP WITH TIME ZONE,
    check_out TIMESTAMP WITH TIME ZONE,
    work_hours DECIMAL(4,2),
    overtime_hours DECIMAL(4,2) DEFAULT 0,
    attendance_type hr.attendance_type DEFAULT 'normal',
    location_id INTEGER REFERENCES public.locations(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, attendance_date)
);

COMMENT ON TABLE hr.attendance IS '考勤记录表';

-- 14. 请假申请
CREATE TABLE hr.leave_requests (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    leave_type hr.leave_type NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days DECIMAL(4,1) NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES hr.employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE hr.leave_requests IS '请假申请表';

-- 15. 假期余额
CREATE TABLE hr.leave_balances (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    year INTEGER NOT NULL,
    leave_type hr.leave_type NOT NULL,
    entitled_days DECIMAL(5,1) DEFAULT 0,
    used_days DECIMAL(5,1) DEFAULT 0,
    carried_over DECIMAL(5,1) DEFAULT 0,
    remaining_days DECIMAL(5,1) GENERATED ALWAYS AS (entitled_days + carried_over - used_days) STORED,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, year, leave_type)
);

COMMENT ON TABLE hr.leave_balances IS '假期余额表';

-- 16. 薪资记录
CREATE TABLE hr.payroll (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    pay_period VARCHAR(7) NOT NULL, -- YYYY-MM
    base_salary DECIMAL(12,2) NOT NULL,
    overtime_pay DECIMAL(12,2) DEFAULT 0,
    bonus DECIMAL(12,2) DEFAULT 0,
    allowances DECIMAL(12,2) DEFAULT 0,
    deductions DECIMAL(12,2) DEFAULT 0,
    tax DECIMAL(12,2) DEFAULT 0,
    social_insurance DECIMAL(12,2) DEFAULT 0,
    housing_fund DECIMAL(12,2) DEFAULT 0,
    net_salary DECIMAL(12,2) NOT NULL,
    payment_date DATE,
    payment_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, pay_period)
);

COMMENT ON TABLE hr.payroll IS '薪资发放记录表';

-- 17. 绩效评估
CREATE TABLE hr.performance_reviews (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    reviewer_id INTEGER NOT NULL REFERENCES hr.employees(id),
    review_period VARCHAR(20) NOT NULL, -- Q1-2024, 2024-H1, etc.
    review_date DATE,
    overall_rating DECIMAL(3,1) CHECK (overall_rating >= 1 AND overall_rating <= 5),
    goals_rating DECIMAL(3,1),
    competency_rating DECIMAL(3,1),
    strengths TEXT,
    areas_for_improvement TEXT,
    goals_for_next_period TEXT,
    employee_comments TEXT,
    manager_comments TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    submitted_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE hr.performance_reviews IS '绩效评估表';

-- 18. 培训课程
CREATE TABLE hr.training_courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    duration_hours DECIMAL(5,1),
    instructor VARCHAR(100),
    max_participants INTEGER,
    cost_per_person DECIMAL(10,2),
    is_mandatory BOOLEAN DEFAULT FALSE,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE hr.training_courses IS '培训课程表';

-- 19. 培训记录
CREATE TABLE hr.training_records (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    course_id INTEGER NOT NULL REFERENCES hr.training_courses(id),
    session_date DATE,
    completion_date DATE,
    score DECIMAL(5,2),
    passed BOOLEAN,
    certificate_no VARCHAR(50),
    cost DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'enrolled',
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE hr.training_records IS '员工培训记录表';

-- 20. 招聘职位
CREATE TABLE hr.job_postings (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES public.positions(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    requirements TEXT,
    responsibilities TEXT,
    salary_range VARCHAR(50),
    location_id INTEGER REFERENCES public.locations(id),
    employment_type hr.contract_type,
    openings INTEGER DEFAULT 1,
    applications_count INTEGER DEFAULT 0,
    posted_date DATE,
    closing_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE hr.job_postings IS '招聘职位发布表';

-- 21. 求职申请
CREATE TABLE hr.job_applications (
    id SERIAL PRIMARY KEY,
    posting_id INTEGER NOT NULL REFERENCES hr.job_postings(id),
    applicant_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    resume_url VARCHAR(500),
    cover_letter TEXT,
    current_company VARCHAR(100),
    current_position VARCHAR(100),
    years_of_experience INTEGER,
    expected_salary DECIMAL(12,2),
    available_date DATE,
    referral_source VARCHAR(50),
    referrer_id INTEGER REFERENCES hr.employees(id),
    status VARCHAR(20) DEFAULT 'new',
    interview_date TIMESTAMP WITH TIME ZONE,
    interviewer_id INTEGER REFERENCES hr.employees(id),
    interview_feedback TEXT,
    offer_date DATE,
    offer_salary DECIMAL(12,2),
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE hr.job_applications IS '求职申请表';

-- 22. 员工技能
CREATE TABLE hr.employee_skills (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hr.employees(id),
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    years_of_experience INTEGER,
    certified BOOLEAN DEFAULT FALSE,
    certification_name VARCHAR(200),
    certification_date DATE,
    expiry_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, skill_name)
);

COMMENT ON TABLE hr.employee_skills IS '员工技能表';

-- =====================================================
-- 财务模块表 (10 tables)
-- =====================================================

-- 23. 会计科目
CREATE TABLE finance.chart_of_accounts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_type finance.account_type NOT NULL,
    parent_id INTEGER REFERENCES finance.chart_of_accounts(id),
    level INTEGER DEFAULT 1,
    is_header BOOLEAN DEFAULT FALSE,
    currency VARCHAR(3) DEFAULT 'CNY',
    description TEXT,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, account_code)
);

COMMENT ON TABLE finance.chart_of_accounts IS '会计科目表';

-- 24. 会计期间
CREATE TABLE finance.fiscal_periods (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    period_name VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    fiscal_year INTEGER NOT NULL,
    period_number INTEGER NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    closed_by INTEGER REFERENCES hr.employees(id),
    closed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, fiscal_year, period_number)
);

COMMENT ON TABLE finance.fiscal_periods IS '会计期间表';

-- 25. 凭证
CREATE TABLE finance.vouchers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    voucher_no VARCHAR(30) NOT NULL,
    voucher_type finance.voucher_type NOT NULL,
    voucher_date DATE NOT NULL,
    fiscal_period_id INTEGER REFERENCES finance.fiscal_periods(id),
    description TEXT,
    total_debit DECIMAL(15,2) DEFAULT 0,
    total_credit DECIMAL(15,2) DEFAULT 0,
    attachment_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    prepared_by INTEGER REFERENCES hr.employees(id),
    reviewed_by INTEGER REFERENCES hr.employees(id),
    approved_by INTEGER REFERENCES hr.employees(id),
    posted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, voucher_no)
);

COMMENT ON TABLE finance.vouchers IS '会计凭证表';

-- 26. 凭证分录
CREATE TABLE finance.voucher_lines (
    id SERIAL PRIMARY KEY,
    voucher_id INTEGER NOT NULL REFERENCES finance.vouchers(id) ON DELETE CASCADE,
    line_no INTEGER NOT NULL,
    account_id INTEGER NOT NULL REFERENCES finance.chart_of_accounts(id),
    description VARCHAR(200),
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'CNY',
    exchange_rate DECIMAL(10,6) DEFAULT 1,
    department_id INTEGER REFERENCES public.departments(id),
    project_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE finance.voucher_lines IS '凭证分录明细表';

-- 27. 账户余额
CREATE TABLE finance.account_balances (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    account_id INTEGER NOT NULL REFERENCES finance.chart_of_accounts(id),
    fiscal_period_id INTEGER NOT NULL REFERENCES finance.fiscal_periods(id),
    opening_balance DECIMAL(15,2) DEFAULT 0,
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    closing_balance DECIMAL(15,2) DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(account_id, fiscal_period_id)
);

COMMENT ON TABLE finance.account_balances IS '账户余额表';

-- 28. 银行账户
CREATE TABLE finance.bank_accounts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    account_number VARCHAR(50) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    branch_name VARCHAR(100),
    swift_code VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'CNY',
    gl_account_id INTEGER REFERENCES finance.chart_of_accounts(id),
    current_balance DECIMAL(15,2) DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, account_number)
);

COMMENT ON TABLE finance.bank_accounts IS '银行账户表';

-- 29. 银行交易
CREATE TABLE finance.bank_transactions (
    id BIGSERIAL PRIMARY KEY,
    bank_account_id INTEGER NOT NULL REFERENCES finance.bank_accounts(id),
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    reference_no VARCHAR(50),
    description TEXT,
    debit_amount DECIMAL(15,2) DEFAULT 0,
    credit_amount DECIMAL(15,2) DEFAULT 0,
    balance_after DECIMAL(15,2),
    counterparty VARCHAR(200),
    voucher_id INTEGER REFERENCES finance.vouchers(id),
    reconciled BOOLEAN DEFAULT FALSE,
    reconciled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE finance.bank_transactions IS '银行交易记录表';

-- 30. 预算
CREATE TABLE finance.budgets (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    fiscal_year INTEGER NOT NULL,
    department_id INTEGER REFERENCES public.departments(id),
    account_id INTEGER REFERENCES finance.chart_of_accounts(id),
    budget_name VARCHAR(100) NOT NULL,
    annual_amount DECIMAL(15,2) NOT NULL,
    q1_amount DECIMAL(15,2),
    q2_amount DECIMAL(15,2),
    q3_amount DECIMAL(15,2),
    q4_amount DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'draft',
    approved_by INTEGER REFERENCES hr.employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE finance.budgets IS '预算表';

-- 31. 发票
CREATE TABLE finance.invoices (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    invoice_no VARCHAR(50) NOT NULL,
    invoice_type VARCHAR(20) NOT NULL, -- sales, purchase
    invoice_date DATE NOT NULL,
    due_date DATE,
    party_type VARCHAR(20) NOT NULL, -- customer, supplier
    party_id INTEGER,
    party_name VARCHAR(200),
    subtotal DECIMAL(15,2) NOT NULL,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,
    paid_amount DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'CNY',
    exchange_rate DECIMAL(10,6) DEFAULT 1,
    payment_status sales.payment_status DEFAULT 'pending',
    notes TEXT,
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, invoice_no)
);

COMMENT ON TABLE finance.invoices IS '发票表';

-- 32. 收付款
CREATE TABLE finance.payments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    payment_no VARCHAR(50) NOT NULL,
    payment_type VARCHAR(20) NOT NULL, -- received, made
    payment_date DATE NOT NULL,
    party_type VARCHAR(20),
    party_id INTEGER,
    party_name VARCHAR(200),
    bank_account_id INTEGER REFERENCES finance.bank_accounts(id),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    payment_method VARCHAR(30),
    reference_no VARCHAR(50),
    voucher_id INTEGER REFERENCES finance.vouchers(id),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'completed',
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, payment_no)
);

COMMENT ON TABLE finance.payments IS '收付款记录表';

-- =====================================================
-- 库存模块表 (8 tables)
-- =====================================================

-- 33. 仓库
CREATE TABLE inventory.warehouses (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    location_id INTEGER REFERENCES public.locations(id),
    address TEXT,
    contact_person VARCHAR(100),
    contact_phone VARCHAR(20),
    capacity INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

COMMENT ON TABLE inventory.warehouses IS '仓库表';

-- 34. 库位
CREATE TABLE inventory.storage_locations (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES inventory.warehouses(id),
    code VARCHAR(30) NOT NULL,
    name VARCHAR(100),
    zone VARCHAR(20),
    aisle VARCHAR(10),
    rack VARCHAR(10),
    shelf VARCHAR(10),
    bin VARCHAR(10),
    capacity INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(warehouse_id, code)
);

COMMENT ON TABLE inventory.storage_locations IS '库位表';

-- 35. 产品/物料
CREATE TABLE inventory.products (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    sku VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER,
    brand VARCHAR(100),
    uom VARCHAR(20) DEFAULT 'PCS',
    weight DECIMAL(10,3),
    weight_unit VARCHAR(5) DEFAULT 'kg',
    dimensions VARCHAR(50),
    barcode VARCHAR(50),
    is_serialized BOOLEAN DEFAULT FALSE,
    is_batch_tracked BOOLEAN DEFAULT FALSE,
    minimum_stock INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 0,
    reorder_quantity INTEGER DEFAULT 0,
    lead_time_days INTEGER DEFAULT 0,
    standard_cost DECIMAL(15,4),
    last_cost DECIMAL(15,4),
    selling_price DECIMAL(15,2),
    tax_rate DECIMAL(5,2) DEFAULT 0,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, sku)
);

COMMENT ON TABLE inventory.products IS '产品/物料主数据表';

-- 36. 产品类别
CREATE TABLE inventory.product_categories (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES inventory.product_categories(id),
    level INTEGER DEFAULT 1,
    path VARCHAR(255),
    gl_inventory_account INTEGER REFERENCES finance.chart_of_accounts(id),
    gl_cogs_account INTEGER REFERENCES finance.chart_of_accounts(id),
    gl_revenue_account INTEGER REFERENCES finance.chart_of_accounts(id),
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

-- 更新产品表的类别外键
ALTER TABLE inventory.products ADD CONSTRAINT fk_product_category 
    FOREIGN KEY (category_id) REFERENCES inventory.product_categories(id);

COMMENT ON TABLE inventory.product_categories IS '产品类别表';

-- 37. 库存
CREATE TABLE inventory.stock (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    warehouse_id INTEGER NOT NULL REFERENCES inventory.warehouses(id),
    location_id INTEGER REFERENCES inventory.storage_locations(id),
    lot_number VARCHAR(50),
    serial_number VARCHAR(50),
    quantity_on_hand DECIMAL(15,3) NOT NULL DEFAULT 0,
    quantity_reserved DECIMAL(15,3) DEFAULT 0,
    quantity_available DECIMAL(15,3) GENERATED ALWAYS AS (quantity_on_hand - quantity_reserved) STORED,
    last_count_date DATE,
    expiry_date DATE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE inventory.stock IS '库存表';

-- 库存唯一索引（使用 COALESCE 处理 NULL 值）
CREATE UNIQUE INDEX idx_stock_unique ON inventory.stock (
    product_id, warehouse_id, COALESCE(location_id, 0), 
    COALESCE(lot_number, ''), COALESCE(serial_number, '')
);

-- 38. 库存移动
CREATE TABLE inventory.stock_movements (
    id BIGSERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    movement_no VARCHAR(30) NOT NULL,
    movement_type inventory.movement_type NOT NULL,
    movement_date TIMESTAMP WITH TIME ZONE NOT NULL,
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    from_warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    from_location_id INTEGER REFERENCES inventory.storage_locations(id),
    to_warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    to_location_id INTEGER REFERENCES inventory.storage_locations(id),
    quantity DECIMAL(15,3) NOT NULL,
    uom VARCHAR(20),
    lot_number VARCHAR(50),
    serial_number VARCHAR(50),
    unit_cost DECIMAL(15,4),
    total_cost DECIMAL(15,2),
    reference_type VARCHAR(30),
    reference_id INTEGER,
    reason TEXT,
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE inventory.stock_movements IS '库存移动记录表';

-- 39. 库存盘点
CREATE TABLE inventory.stock_counts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    count_no VARCHAR(30) NOT NULL UNIQUE,
    warehouse_id INTEGER NOT NULL REFERENCES inventory.warehouses(id),
    count_date DATE NOT NULL,
    count_type VARCHAR(20) DEFAULT 'full', -- full, cycle, spot
    status VARCHAR(20) DEFAULT 'draft',
    counted_by INTEGER REFERENCES hr.employees(id),
    approved_by INTEGER REFERENCES hr.employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE inventory.stock_counts IS '库存盘点表';

-- 40. 盘点明细
CREATE TABLE inventory.stock_count_lines (
    id SERIAL PRIMARY KEY,
    count_id INTEGER NOT NULL REFERENCES inventory.stock_counts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    location_id INTEGER REFERENCES inventory.storage_locations(id),
    lot_number VARCHAR(50),
    system_quantity DECIMAL(15,3),
    counted_quantity DECIMAL(15,3),
    variance DECIMAL(15,3) GENERATED ALWAYS AS (counted_quantity - system_quantity) STORED,
    unit_cost DECIMAL(15,4),
    variance_value DECIMAL(15,2),
    adjustment_posted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE inventory.stock_count_lines IS '盘点明细表';

-- =====================================================
-- 销售模块表 (8 tables)
-- =====================================================

-- 41. 客户
CREATE TABLE sales.customers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    customer_code VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200),
    tax_id VARCHAR(50),
    customer_type VARCHAR(20) DEFAULT 'regular',
    industry VARCHAR(50),
    contact_person VARCHAR(100),
    phone VARCHAR(30),
    email VARCHAR(100),
    website VARCHAR(200),
    billing_address TEXT,
    shipping_address TEXT,
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'China',
    credit_limit DECIMAL(15,2) DEFAULT 0,
    current_balance DECIMAL(15,2) DEFAULT 0,
    payment_terms INTEGER DEFAULT 30,
    currency VARCHAR(3) DEFAULT 'CNY',
    sales_rep_id INTEGER REFERENCES hr.employees(id),
    price_list_id INTEGER,
    discount_rate DECIMAL(5,2) DEFAULT 0,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, customer_code)
);

COMMENT ON TABLE sales.customers IS '客户表';

-- 42. 销售订单
CREATE TABLE sales.sales_orders (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    order_no VARCHAR(30) NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES sales.customers(id),
    order_date DATE NOT NULL,
    requested_date DATE,
    promised_date DATE,
    warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    sales_rep_id INTEGER REFERENCES hr.employees(id),
    currency VARCHAR(3) DEFAULT 'CNY',
    exchange_rate DECIMAL(10,6) DEFAULT 1,
    subtotal DECIMAL(15,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    shipping_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    shipping_address TEXT,
    shipping_method VARCHAR(50),
    payment_terms INTEGER,
    notes TEXT,
    internal_notes TEXT,
    status sales.order_status DEFAULT 'draft',
    approved_by INTEGER REFERENCES hr.employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, order_no)
);

COMMENT ON TABLE sales.sales_orders IS '销售订单表';

-- 43. 销售订单明细
CREATE TABLE sales.sales_order_lines (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sales.sales_orders(id) ON DELETE CASCADE,
    line_no INTEGER NOT NULL,
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    description VARCHAR(500),
    quantity DECIMAL(15,3) NOT NULL,
    uom VARCHAR(20),
    unit_price DECIMAL(15,4) NOT NULL,
    discount_rate DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    line_total DECIMAL(15,2) NOT NULL,
    quantity_shipped DECIMAL(15,3) DEFAULT 0,
    quantity_invoiced DECIMAL(15,3) DEFAULT 0,
    requested_date DATE,
    warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE sales.sales_order_lines IS '销售订单明细表';

-- 44. 发货单
CREATE TABLE sales.shipments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    shipment_no VARCHAR(30) NOT NULL,
    order_id INTEGER NOT NULL REFERENCES sales.sales_orders(id),
    customer_id INTEGER NOT NULL REFERENCES sales.customers(id),
    shipment_date DATE NOT NULL,
    warehouse_id INTEGER NOT NULL REFERENCES inventory.warehouses(id),
    shipping_address TEXT,
    carrier VARCHAR(100),
    tracking_number VARCHAR(100),
    shipping_cost DECIMAL(15,2) DEFAULT 0,
    weight DECIMAL(10,3),
    packages INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'draft',
    shipped_by INTEGER REFERENCES hr.employees(id),
    shipped_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, shipment_no)
);

COMMENT ON TABLE sales.shipments IS '发货单表';

-- 45. 发货单明细
CREATE TABLE sales.shipment_lines (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER NOT NULL REFERENCES sales.shipments(id) ON DELETE CASCADE,
    order_line_id INTEGER REFERENCES sales.sales_order_lines(id),
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    quantity DECIMAL(15,3) NOT NULL,
    lot_number VARCHAR(50),
    serial_number VARCHAR(50),
    location_id INTEGER REFERENCES inventory.storage_locations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE sales.shipment_lines IS '发货单明细表';

-- 46. 销售退货
CREATE TABLE sales.sales_returns (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    return_no VARCHAR(30) NOT NULL,
    order_id INTEGER REFERENCES sales.sales_orders(id),
    customer_id INTEGER NOT NULL REFERENCES sales.customers(id),
    return_date DATE NOT NULL,
    warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    reason TEXT,
    total_amount DECIMAL(15,2) DEFAULT 0,
    refund_amount DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES hr.employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, return_no)
);

COMMENT ON TABLE sales.sales_returns IS '销售退货表';

-- 47. 报价单
CREATE TABLE sales.quotations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    quote_no VARCHAR(30) NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES sales.customers(id),
    quote_date DATE NOT NULL,
    valid_until DATE,
    sales_rep_id INTEGER REFERENCES hr.employees(id),
    currency VARCHAR(3) DEFAULT 'CNY',
    subtotal DECIMAL(15,2) DEFAULT 0,
    discount_amount DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    terms TEXT,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    converted_to_order_id INTEGER REFERENCES sales.sales_orders(id),
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, quote_no)
);

COMMENT ON TABLE sales.quotations IS '销售报价单表';

-- 48. 价格表
CREATE TABLE sales.price_lists (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    currency VARCHAR(3) DEFAULT 'CNY',
    start_date DATE,
    end_date DATE,
    is_default BOOLEAN DEFAULT FALSE,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

COMMENT ON TABLE sales.price_lists IS '价格表';

-- =====================================================
-- 采购模块表 (6 tables)
-- =====================================================

-- 49. 供应商
CREATE TABLE procurement.suppliers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    supplier_code VARCHAR(20) NOT NULL,
    name VARCHAR(200) NOT NULL,
    legal_name VARCHAR(200),
    tax_id VARCHAR(50),
    supplier_type VARCHAR(20) DEFAULT 'regular',
    industry VARCHAR(50),
    contact_person VARCHAR(100),
    phone VARCHAR(30),
    email VARCHAR(100),
    website VARCHAR(200),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'China',
    payment_terms INTEGER DEFAULT 30,
    currency VARCHAR(3) DEFAULT 'CNY',
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    current_balance DECIMAL(15,2) DEFAULT 0,
    bank_name VARCHAR(100),
    bank_account VARCHAR(50),
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, supplier_code)
);

COMMENT ON TABLE procurement.suppliers IS '供应商表';

-- 50. 采购订单
CREATE TABLE procurement.purchase_orders (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    po_no VARCHAR(30) NOT NULL,
    supplier_id INTEGER NOT NULL REFERENCES procurement.suppliers(id),
    order_date DATE NOT NULL,
    expected_date DATE,
    warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    buyer_id INTEGER REFERENCES hr.employees(id),
    currency VARCHAR(3) DEFAULT 'CNY',
    exchange_rate DECIMAL(10,6) DEFAULT 1,
    subtotal DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    shipping_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    payment_terms INTEGER,
    shipping_address TEXT,
    notes TEXT,
    internal_notes TEXT,
    status procurement.po_status DEFAULT 'draft',
    approved_by INTEGER REFERENCES hr.employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, po_no)
);

COMMENT ON TABLE procurement.purchase_orders IS '采购订单表';

-- 51. 采购订单明细
CREATE TABLE procurement.purchase_order_lines (
    id SERIAL PRIMARY KEY,
    po_id INTEGER NOT NULL REFERENCES procurement.purchase_orders(id) ON DELETE CASCADE,
    line_no INTEGER NOT NULL,
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    description VARCHAR(500),
    quantity DECIMAL(15,3) NOT NULL,
    uom VARCHAR(20),
    unit_price DECIMAL(15,4) NOT NULL,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    line_total DECIMAL(15,2) NOT NULL,
    quantity_received DECIMAL(15,3) DEFAULT 0,
    quantity_invoiced DECIMAL(15,3) DEFAULT 0,
    expected_date DATE,
    warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE procurement.purchase_order_lines IS '采购订单明细表';

-- 52. 收货单
CREATE TABLE procurement.goods_receipts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    receipt_no VARCHAR(30) NOT NULL,
    po_id INTEGER NOT NULL REFERENCES procurement.purchase_orders(id),
    supplier_id INTEGER NOT NULL REFERENCES procurement.suppliers(id),
    receipt_date DATE NOT NULL,
    warehouse_id INTEGER NOT NULL REFERENCES inventory.warehouses(id),
    status VARCHAR(20) DEFAULT 'draft',
    received_by INTEGER REFERENCES hr.employees(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, receipt_no)
);

COMMENT ON TABLE procurement.goods_receipts IS '收货单表';

-- 53. 收货单明细
CREATE TABLE procurement.goods_receipt_lines (
    id SERIAL PRIMARY KEY,
    receipt_id INTEGER NOT NULL REFERENCES procurement.goods_receipts(id) ON DELETE CASCADE,
    po_line_id INTEGER REFERENCES procurement.purchase_order_lines(id),
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    quantity DECIMAL(15,3) NOT NULL,
    lot_number VARCHAR(50),
    expiry_date DATE,
    location_id INTEGER REFERENCES inventory.storage_locations(id),
    unit_cost DECIMAL(15,4),
    qc_status production.qc_result DEFAULT 'pending',
    qc_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE procurement.goods_receipt_lines IS '收货单明细表';

-- 54. 供应商产品
CREATE TABLE procurement.supplier_products (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES procurement.suppliers(id),
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    supplier_sku VARCHAR(50),
    supplier_name VARCHAR(200),
    unit_price DECIMAL(15,4),
    currency VARCHAR(3) DEFAULT 'CNY',
    minimum_order_qty DECIMAL(15,3) DEFAULT 1,
    lead_time_days INTEGER DEFAULT 0,
    is_preferred BOOLEAN DEFAULT FALSE,
    status record_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(supplier_id, product_id)
);

COMMENT ON TABLE procurement.supplier_products IS '供应商产品目录表';

-- =====================================================
-- 生产模块表 (6 tables)
-- =====================================================

-- 55. 物料清单 (BOM)
CREATE TABLE production.bom (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    bom_no VARCHAR(30) NOT NULL,
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    version VARCHAR(20) DEFAULT '1.0',
    description TEXT,
    standard_quantity DECIMAL(15,3) DEFAULT 1,
    uom VARCHAR(20),
    effective_date DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES hr.employees(id),
    approved_by INTEGER REFERENCES hr.employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, bom_no)
);

COMMENT ON TABLE production.bom IS '物料清单 (BOM) 表';

-- 56. BOM 明细
CREATE TABLE production.bom_lines (
    id SERIAL PRIMARY KEY,
    bom_id INTEGER NOT NULL REFERENCES production.bom(id) ON DELETE CASCADE,
    line_no INTEGER NOT NULL,
    component_id INTEGER NOT NULL REFERENCES inventory.products(id),
    quantity DECIMAL(15,6) NOT NULL,
    uom VARCHAR(20),
    scrap_rate DECIMAL(5,2) DEFAULT 0,
    is_critical BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE production.bom_lines IS 'BOM 明细表';

-- 57. 生产工单
CREATE TABLE production.work_orders (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    wo_no VARCHAR(30) NOT NULL,
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    bom_id INTEGER REFERENCES production.bom(id),
    sales_order_id INTEGER REFERENCES sales.sales_orders(id),
    planned_quantity DECIMAL(15,3) NOT NULL,
    completed_quantity DECIMAL(15,3) DEFAULT 0,
    scrapped_quantity DECIMAL(15,3) DEFAULT 0,
    uom VARCHAR(20),
    warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    planned_start DATE,
    planned_end DATE,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    priority INTEGER DEFAULT 5,
    status production.work_order_status DEFAULT 'planned',
    notes TEXT,
    created_by INTEGER REFERENCES hr.employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, wo_no)
);

COMMENT ON TABLE production.work_orders IS '生产工单表';

-- 58. 工单物料消耗
CREATE TABLE production.wo_material_consumption (
    id SERIAL PRIMARY KEY,
    wo_id INTEGER NOT NULL REFERENCES production.work_orders(id),
    product_id INTEGER NOT NULL REFERENCES inventory.products(id),
    planned_quantity DECIMAL(15,3) NOT NULL,
    issued_quantity DECIMAL(15,3) DEFAULT 0,
    consumed_quantity DECIMAL(15,3) DEFAULT 0,
    returned_quantity DECIMAL(15,3) DEFAULT 0,
    warehouse_id INTEGER REFERENCES inventory.warehouses(id),
    location_id INTEGER REFERENCES inventory.storage_locations(id),
    lot_number VARCHAR(50),
    issue_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE production.wo_material_consumption IS '工单物料消耗表';

-- 59. 质量检验
CREATE TABLE production.quality_inspections (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES public.companies(id),
    inspection_no VARCHAR(30) NOT NULL,
    inspection_type VARCHAR(30) NOT NULL, -- incoming, in_process, final
    reference_type VARCHAR(30),
    reference_id INTEGER,
    product_id INTEGER REFERENCES inventory.products(id),
    lot_number VARCHAR(50),
    inspection_date DATE NOT NULL,
    quantity_inspected DECIMAL(15,3),
    quantity_passed DECIMAL(15,3),
    quantity_failed DECIMAL(15,3),
    result production.qc_result DEFAULT 'pending',
    inspector_id INTEGER REFERENCES hr.employees(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, inspection_no)
);

COMMENT ON TABLE production.quality_inspections IS '质量检验表';

-- 60. 质检项目
CREATE TABLE production.qc_checkpoints (
    id SERIAL PRIMARY KEY,
    inspection_id INTEGER NOT NULL REFERENCES production.quality_inspections(id) ON DELETE CASCADE,
    checkpoint_name VARCHAR(100) NOT NULL,
    specification VARCHAR(200),
    min_value DECIMAL(15,4),
    max_value DECIMAL(15,4),
    actual_value DECIMAL(15,4),
    text_value VARCHAR(200),
    result production.qc_result,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE production.qc_checkpoints IS '质检项目明细表';

-- =====================================================
-- 索引 (100+ indexes)
-- =====================================================

-- 公共模块索引
CREATE INDEX idx_companies_status ON public.companies(status);
CREATE INDEX idx_departments_company_id ON public.departments(company_id);
CREATE INDEX idx_departments_parent_id ON public.departments(parent_id);
CREATE INDEX idx_positions_company_id ON public.positions(company_id);
CREATE INDEX idx_positions_department_id ON public.positions(department_id);
CREATE INDEX idx_locations_company_id ON public.locations(company_id);
CREATE INDEX idx_users_username ON public.users(username);
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_employee_id ON public.users(employee_id);
CREATE INDEX idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_table_name ON public.audit_logs(table_name);
CREATE INDEX idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- HR 模块索引
CREATE INDEX idx_employees_company_id ON hr.employees(company_id);
CREATE INDEX idx_employees_department_id ON hr.employees(department_id);
CREATE INDEX idx_employees_position_id ON hr.employees(position_id);
CREATE INDEX idx_employees_manager_id ON hr.employees(manager_id);
CREATE INDEX idx_employees_status ON hr.employees(status);
CREATE INDEX idx_employees_hire_date ON hr.employees(hire_date);
CREATE INDEX idx_employees_full_name ON hr.employees USING gin(full_name gin_trgm_ops);
CREATE INDEX idx_attendance_employee_date ON hr.attendance(employee_id, attendance_date);
CREATE INDEX idx_attendance_date ON hr.attendance(attendance_date);
CREATE INDEX idx_leave_requests_employee_id ON hr.leave_requests(employee_id);
CREATE INDEX idx_leave_requests_status ON hr.leave_requests(status);
CREATE INDEX idx_payroll_employee_period ON hr.payroll(employee_id, pay_period);
CREATE INDEX idx_performance_reviews_employee ON hr.performance_reviews(employee_id);
CREATE INDEX idx_training_records_employee ON hr.training_records(employee_id);
CREATE INDEX idx_job_postings_status ON hr.job_postings(status);
CREATE INDEX idx_job_applications_posting ON hr.job_applications(posting_id);
CREATE INDEX idx_job_applications_status ON hr.job_applications(status);

-- 财务模块索引
CREATE INDEX idx_coa_company_id ON finance.chart_of_accounts(company_id);
CREATE INDEX idx_coa_account_type ON finance.chart_of_accounts(account_type);
CREATE INDEX idx_vouchers_company_id ON finance.vouchers(company_id);
CREATE INDEX idx_vouchers_voucher_date ON finance.vouchers(voucher_date);
CREATE INDEX idx_vouchers_status ON finance.vouchers(status);
CREATE INDEX idx_voucher_lines_voucher_id ON finance.voucher_lines(voucher_id);
CREATE INDEX idx_voucher_lines_account_id ON finance.voucher_lines(account_id);
CREATE INDEX idx_bank_accounts_company_id ON finance.bank_accounts(company_id);
CREATE INDEX idx_bank_transactions_account ON finance.bank_transactions(bank_account_id);
CREATE INDEX idx_bank_transactions_date ON finance.bank_transactions(transaction_date);
CREATE INDEX idx_invoices_company_id ON finance.invoices(company_id);
CREATE INDEX idx_invoices_party ON finance.invoices(party_type, party_id);
CREATE INDEX idx_invoices_status ON finance.invoices(payment_status);
CREATE INDEX idx_payments_company_id ON finance.payments(company_id);
CREATE INDEX idx_payments_date ON finance.payments(payment_date);

-- 库存模块索引
CREATE INDEX idx_warehouses_company_id ON inventory.warehouses(company_id);
CREATE INDEX idx_storage_locations_warehouse ON inventory.storage_locations(warehouse_id);
CREATE INDEX idx_products_company_id ON inventory.products(company_id);
CREATE INDEX idx_products_sku ON inventory.products(sku);
CREATE INDEX idx_products_category_id ON inventory.products(category_id);
CREATE INDEX idx_products_status ON inventory.products(status);
CREATE INDEX idx_products_name ON inventory.products USING gin(name gin_trgm_ops);
CREATE INDEX idx_stock_product_id ON inventory.stock(product_id);
CREATE INDEX idx_stock_warehouse_id ON inventory.stock(warehouse_id);
CREATE INDEX idx_stock_location_id ON inventory.stock(location_id);
CREATE INDEX idx_stock_movements_product ON inventory.stock_movements(product_id);
CREATE INDEX idx_stock_movements_date ON inventory.stock_movements(movement_date);
CREATE INDEX idx_stock_movements_type ON inventory.stock_movements(movement_type);
CREATE INDEX idx_stock_counts_warehouse ON inventory.stock_counts(warehouse_id);
CREATE INDEX idx_stock_counts_date ON inventory.stock_counts(count_date);

-- 销售模块索引
CREATE INDEX idx_customers_company_id ON sales.customers(company_id);
CREATE INDEX idx_customers_code ON sales.customers(customer_code);
CREATE INDEX idx_customers_name ON sales.customers USING gin(name gin_trgm_ops);
CREATE INDEX idx_customers_sales_rep ON sales.customers(sales_rep_id);
CREATE INDEX idx_sales_orders_company_id ON sales.sales_orders(company_id);
CREATE INDEX idx_sales_orders_customer_id ON sales.sales_orders(customer_id);
CREATE INDEX idx_sales_orders_date ON sales.sales_orders(order_date);
CREATE INDEX idx_sales_orders_status ON sales.sales_orders(status);
CREATE INDEX idx_sales_order_lines_order_id ON sales.sales_order_lines(order_id);
CREATE INDEX idx_sales_order_lines_product_id ON sales.sales_order_lines(product_id);
CREATE INDEX idx_shipments_order_id ON sales.shipments(order_id);
CREATE INDEX idx_shipments_date ON sales.shipments(shipment_date);
CREATE INDEX idx_quotations_customer_id ON sales.quotations(customer_id);
CREATE INDEX idx_quotations_status ON sales.quotations(status);

-- 采购模块索引
CREATE INDEX idx_suppliers_company_id ON procurement.suppliers(company_id);
CREATE INDEX idx_suppliers_code ON procurement.suppliers(supplier_code);
CREATE INDEX idx_suppliers_name ON procurement.suppliers USING gin(name gin_trgm_ops);
CREATE INDEX idx_purchase_orders_company_id ON procurement.purchase_orders(company_id);
CREATE INDEX idx_purchase_orders_supplier_id ON procurement.purchase_orders(supplier_id);
CREATE INDEX idx_purchase_orders_date ON procurement.purchase_orders(order_date);
CREATE INDEX idx_purchase_orders_status ON procurement.purchase_orders(status);
CREATE INDEX idx_po_lines_po_id ON procurement.purchase_order_lines(po_id);
CREATE INDEX idx_po_lines_product_id ON procurement.purchase_order_lines(product_id);
CREATE INDEX idx_goods_receipts_po_id ON procurement.goods_receipts(po_id);
CREATE INDEX idx_goods_receipts_date ON procurement.goods_receipts(receipt_date);
CREATE INDEX idx_supplier_products_supplier ON procurement.supplier_products(supplier_id);
CREATE INDEX idx_supplier_products_product ON procurement.supplier_products(product_id);

-- 生产模块索引
CREATE INDEX idx_bom_company_id ON production.bom(company_id);
CREATE INDEX idx_bom_product_id ON production.bom(product_id);
CREATE INDEX idx_bom_lines_bom_id ON production.bom_lines(bom_id);
CREATE INDEX idx_bom_lines_component_id ON production.bom_lines(component_id);
CREATE INDEX idx_work_orders_company_id ON production.work_orders(company_id);
CREATE INDEX idx_work_orders_product_id ON production.work_orders(product_id);
CREATE INDEX idx_work_orders_status ON production.work_orders(status);
CREATE INDEX idx_work_orders_planned_start ON production.work_orders(planned_start);
CREATE INDEX idx_wo_material_wo_id ON production.wo_material_consumption(wo_id);
CREATE INDEX idx_qc_inspections_product ON production.quality_inspections(product_id);
CREATE INDEX idx_qc_inspections_date ON production.quality_inspections(inspection_date);
CREATE INDEX idx_qc_inspections_result ON production.quality_inspections(result);

-- =====================================================
-- 视图 (20+ views)
-- =====================================================

-- 1. 员工详情视图
CREATE VIEW hr.v_employee_details AS
SELECT 
    e.id,
    e.employee_no,
    e.full_name,
    e.email,
    e.phone,
    e.gender,
    e.birth_date,
    e.hire_date,
    e.status,
    c.name AS company_name,
    d.name AS department_name,
    p.title AS position_title,
    l.name AS location_name,
    m.full_name AS manager_name,
    e.base_salary,
    e.contract_type
FROM hr.employees e
JOIN public.companies c ON e.company_id = c.id
LEFT JOIN public.departments d ON e.department_id = d.id
LEFT JOIN public.positions p ON e.position_id = p.id
LEFT JOIN public.locations l ON e.location_id = l.id
LEFT JOIN hr.employees m ON e.manager_id = m.id;

-- 2. 部门统计视图
CREATE VIEW public.v_department_stats AS
SELECT 
    d.id,
    d.name,
    d.code,
    c.name AS company_name,
    m.full_name AS manager_name,
    COUNT(e.id) AS employee_count,
    COALESCE(SUM(e.base_salary), 0) AS total_salary,
    d.budget,
    d.budget - COALESCE(SUM(e.base_salary), 0) AS budget_remaining
FROM public.departments d
JOIN public.companies c ON d.company_id = c.id
LEFT JOIN hr.employees m ON d.manager_id = m.id
LEFT JOIN hr.employees e ON d.id = e.department_id AND e.status = 'active'
GROUP BY d.id, c.name, m.full_name;

-- 3. 月度考勤统计视图
CREATE VIEW hr.v_monthly_attendance AS
SELECT 
    e.id AS employee_id,
    e.full_name,
    d.name AS department_name,
    DATE_TRUNC('month', a.attendance_date) AS month,
    COUNT(*) AS total_days,
    SUM(CASE WHEN a.attendance_type = 'normal' THEN 1 ELSE 0 END) AS normal_days,
    SUM(CASE WHEN a.attendance_type = 'late' THEN 1 ELSE 0 END) AS late_days,
    SUM(CASE WHEN a.attendance_type = 'absent' THEN 1 ELSE 0 END) AS absent_days,
    SUM(a.work_hours) AS total_work_hours,
    SUM(a.overtime_hours) AS total_overtime_hours
FROM hr.employees e
LEFT JOIN hr.attendance a ON e.id = a.employee_id
LEFT JOIN public.departments d ON e.department_id = d.id
GROUP BY e.id, e.full_name, d.name, DATE_TRUNC('month', a.attendance_date);

-- 4. 账户余额汇总视图
CREATE VIEW finance.v_account_summary AS
SELECT 
    coa.id,
    coa.account_code,
    coa.account_name,
    coa.account_type,
    c.name AS company_name,
    COALESCE(SUM(ab.debit_amount), 0) AS total_debit,
    COALESCE(SUM(ab.credit_amount), 0) AS total_credit,
    COALESCE(SUM(ab.closing_balance), 0) AS current_balance
FROM finance.chart_of_accounts coa
JOIN public.companies c ON coa.company_id = c.id
LEFT JOIN finance.account_balances ab ON coa.id = ab.account_id
GROUP BY coa.id, c.name;

-- 5. 库存汇总视图
CREATE VIEW inventory.v_stock_summary AS
SELECT 
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    pc.name AS category_name,
    w.name AS warehouse_name,
    SUM(s.quantity_on_hand) AS total_on_hand,
    SUM(s.quantity_reserved) AS total_reserved,
    SUM(s.quantity_available) AS total_available,
    p.minimum_stock,
    p.reorder_point,
    CASE WHEN SUM(s.quantity_available) <= p.minimum_stock THEN TRUE ELSE FALSE END AS is_low_stock
FROM inventory.products p
LEFT JOIN inventory.product_categories pc ON p.category_id = pc.id
LEFT JOIN inventory.stock s ON p.id = s.product_id
LEFT JOIN inventory.warehouses w ON s.warehouse_id = w.id
GROUP BY p.id, pc.name, w.name;

-- 6. 低库存预警视图
CREATE VIEW inventory.v_low_stock_alert AS
SELECT 
    p.id,
    p.sku,
    p.name,
    pc.name AS category_name,
    p.minimum_stock,
    p.reorder_point,
    p.reorder_quantity,
    COALESCE(SUM(s.quantity_available), 0) AS available_quantity,
    p.reorder_point - COALESCE(SUM(s.quantity_available), 0) AS shortage_quantity
FROM inventory.products p
LEFT JOIN inventory.product_categories pc ON p.category_id = pc.id
LEFT JOIN inventory.stock s ON p.id = s.product_id
WHERE p.status = 'active'
GROUP BY p.id, pc.name
HAVING COALESCE(SUM(s.quantity_available), 0) <= p.reorder_point;

-- 7. 销售订单概览视图
CREATE VIEW sales.v_order_overview AS
SELECT 
    so.id,
    so.order_no,
    so.order_date,
    c.name AS customer_name,
    sr.full_name AS sales_rep,
    so.total_amount,
    so.status,
    COUNT(sol.id) AS line_count,
    SUM(sol.quantity) AS total_quantity,
    SUM(sol.quantity_shipped) AS shipped_quantity
FROM sales.sales_orders so
JOIN sales.customers c ON so.customer_id = c.id
LEFT JOIN hr.employees sr ON so.sales_rep_id = sr.id
LEFT JOIN sales.sales_order_lines sol ON so.id = sol.order_id
GROUP BY so.id, c.name, sr.full_name;

-- 8. 客户销售统计视图
CREATE VIEW sales.v_customer_sales_stats AS
SELECT 
    c.id AS customer_id,
    c.customer_code,
    c.name,
    c.customer_type,
    COUNT(DISTINCT so.id) AS order_count,
    COALESCE(SUM(so.total_amount), 0) AS total_sales,
    COALESCE(AVG(so.total_amount), 0) AS avg_order_value,
    MAX(so.order_date) AS last_order_date,
    c.credit_limit,
    c.current_balance
FROM sales.customers c
LEFT JOIN sales.sales_orders so ON c.id = so.customer_id AND so.status NOT IN ('cancelled', 'returned')
GROUP BY c.id;

-- 9. 采购订单概览视图
CREATE VIEW procurement.v_po_overview AS
SELECT 
    po.id,
    po.po_no,
    po.order_date,
    s.name AS supplier_name,
    b.full_name AS buyer_name,
    po.total_amount,
    po.status,
    COUNT(pol.id) AS line_count,
    SUM(pol.quantity) AS total_quantity,
    SUM(pol.quantity_received) AS received_quantity
FROM procurement.purchase_orders po
JOIN procurement.suppliers s ON po.supplier_id = s.id
LEFT JOIN hr.employees b ON po.buyer_id = b.id
LEFT JOIN procurement.purchase_order_lines pol ON po.id = pol.po_id
GROUP BY po.id, s.name, b.full_name;

-- 10. 供应商采购统计视图
CREATE VIEW procurement.v_supplier_stats AS
SELECT 
    s.id AS supplier_id,
    s.supplier_code,
    s.name,
    s.supplier_type,
    s.rating,
    COUNT(DISTINCT po.id) AS po_count,
    COALESCE(SUM(po.total_amount), 0) AS total_purchases,
    COALESCE(AVG(po.total_amount), 0) AS avg_po_value,
    MAX(po.order_date) AS last_po_date,
    s.current_balance
FROM procurement.suppliers s
LEFT JOIN procurement.purchase_orders po ON s.id = po.supplier_id AND po.status NOT IN ('cancelled')
GROUP BY s.id;

-- 11. 生产工单概览视图
CREATE VIEW production.v_work_order_overview AS
SELECT 
    wo.id,
    wo.wo_no,
    p.sku AS product_sku,
    p.name AS product_name,
    wo.planned_quantity,
    wo.completed_quantity,
    wo.scrapped_quantity,
    wo.planned_start,
    wo.planned_end,
    wo.actual_start,
    wo.actual_end,
    wo.status,
    w.name AS warehouse_name
FROM production.work_orders wo
JOIN inventory.products p ON wo.product_id = p.id
LEFT JOIN inventory.warehouses w ON wo.warehouse_id = w.id;

-- 12. BOM 成本视图
CREATE VIEW production.v_bom_cost AS
SELECT 
    b.id AS bom_id,
    b.bom_no,
    p.sku AS product_sku,
    p.name AS product_name,
    b.standard_quantity,
    SUM(bl.quantity * COALESCE(c.standard_cost, 0)) AS total_material_cost
FROM production.bom b
JOIN inventory.products p ON b.product_id = p.id
LEFT JOIN production.bom_lines bl ON b.id = bl.bom_id
LEFT JOIN inventory.products c ON bl.component_id = c.id
GROUP BY b.id, p.sku, p.name;

-- 13. 每日销售报表视图
CREATE VIEW sales.v_daily_sales AS
SELECT 
    DATE(so.order_date) AS sale_date,
    so.company_id,
    COUNT(DISTINCT so.id) AS order_count,
    COUNT(DISTINCT so.customer_id) AS customer_count,
    SUM(so.total_amount) AS total_sales,
    AVG(so.total_amount) AS avg_order_value
FROM sales.sales_orders so
WHERE so.status NOT IN ('draft', 'cancelled')
GROUP BY DATE(so.order_date), so.company_id
ORDER BY sale_date DESC;

-- 14. 产品销售排行视图
CREATE VIEW sales.v_product_sales_ranking AS
SELECT 
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    pc.name AS category_name,
    SUM(sol.quantity) AS total_quantity_sold,
    SUM(sol.line_total) AS total_revenue,
    COUNT(DISTINCT sol.order_id) AS order_count
FROM inventory.products p
LEFT JOIN inventory.product_categories pc ON p.category_id = pc.id
LEFT JOIN sales.sales_order_lines sol ON p.id = sol.product_id
LEFT JOIN sales.sales_orders so ON sol.order_id = so.id AND so.status NOT IN ('draft', 'cancelled')
GROUP BY p.id, pc.name
ORDER BY total_revenue DESC NULLS LAST;

-- 15. 质检统计视图
CREATE VIEW production.v_qc_stats AS
SELECT 
    DATE_TRUNC('month', qi.inspection_date) AS month,
    qi.inspection_type,
    COUNT(*) AS total_inspections,
    SUM(CASE WHEN qi.result = 'pass' THEN 1 ELSE 0 END) AS passed_count,
    SUM(CASE WHEN qi.result = 'fail' THEN 1 ELSE 0 END) AS failed_count,
    ROUND(100.0 * SUM(CASE WHEN qi.result = 'pass' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS pass_rate
FROM production.quality_inspections qi
GROUP BY DATE_TRUNC('month', qi.inspection_date), qi.inspection_type
ORDER BY month DESC;

-- 16. 应收账款账龄视图
CREATE VIEW finance.v_ar_aging AS
SELECT 
    c.id AS customer_id,
    c.name AS customer_name,
    i.id AS invoice_id,
    i.invoice_no,
    i.invoice_date,
    i.due_date,
    i.total_amount,
    i.paid_amount,
    i.total_amount - i.paid_amount AS balance,
    CASE 
        WHEN i.due_date >= CURRENT_DATE THEN 'Current'
        WHEN CURRENT_DATE - i.due_date <= 30 THEN '1-30 Days'
        WHEN CURRENT_DATE - i.due_date <= 60 THEN '31-60 Days'
        WHEN CURRENT_DATE - i.due_date <= 90 THEN '61-90 Days'
        ELSE 'Over 90 Days'
    END AS aging_bucket
FROM finance.invoices i
JOIN sales.customers c ON i.party_type = 'customer' AND i.party_id = c.id
WHERE i.invoice_type = 'sales' AND i.payment_status NOT IN ('paid', 'refunded');

-- 17. 应付账款账龄视图
CREATE VIEW finance.v_ap_aging AS
SELECT 
    s.id AS supplier_id,
    s.name AS supplier_name,
    i.id AS invoice_id,
    i.invoice_no,
    i.invoice_date,
    i.due_date,
    i.total_amount,
    i.paid_amount,
    i.total_amount - i.paid_amount AS balance,
    CASE 
        WHEN i.due_date >= CURRENT_DATE THEN 'Current'
        WHEN CURRENT_DATE - i.due_date <= 30 THEN '1-30 Days'
        WHEN CURRENT_DATE - i.due_date <= 60 THEN '31-60 Days'
        WHEN CURRENT_DATE - i.due_date <= 90 THEN '61-90 Days'
        ELSE 'Over 90 Days'
    END AS aging_bucket
FROM finance.invoices i
JOIN procurement.suppliers s ON i.party_type = 'supplier' AND i.party_id = s.id
WHERE i.invoice_type = 'purchase' AND i.payment_status NOT IN ('paid', 'refunded');

-- 18. 库存移动历史视图
CREATE VIEW inventory.v_movement_history AS
SELECT 
    sm.id,
    sm.movement_no,
    sm.movement_type,
    sm.movement_date,
    p.sku AS product_sku,
    p.name AS product_name,
    fw.name AS from_warehouse,
    tw.name AS to_warehouse,
    sm.quantity,
    sm.unit_cost,
    sm.total_cost,
    e.full_name AS created_by_name
FROM inventory.stock_movements sm
JOIN inventory.products p ON sm.product_id = p.id
LEFT JOIN inventory.warehouses fw ON sm.from_warehouse_id = fw.id
LEFT JOIN inventory.warehouses tw ON sm.to_warehouse_id = tw.id
LEFT JOIN hr.employees e ON sm.created_by = e.id
ORDER BY sm.movement_date DESC;

-- 19. 员工薪资汇总视图
CREATE VIEW hr.v_payroll_summary AS
SELECT 
    pr.pay_period,
    d.name AS department_name,
    COUNT(DISTINCT pr.employee_id) AS employee_count,
    SUM(pr.base_salary) AS total_base_salary,
    SUM(pr.overtime_pay) AS total_overtime,
    SUM(pr.bonus) AS total_bonus,
    SUM(pr.deductions) AS total_deductions,
    SUM(pr.net_salary) AS total_net_salary
FROM hr.payroll pr
JOIN hr.employees e ON pr.employee_id = e.id
LEFT JOIN public.departments d ON e.department_id = d.id
GROUP BY pr.pay_period, d.name
ORDER BY pr.pay_period DESC, d.name;

-- 20. 公司仪表板视图
CREATE VIEW public.v_company_dashboard AS
SELECT 
    c.id AS company_id,
    c.name AS company_name,
    (SELECT COUNT(*) FROM hr.employees WHERE company_id = c.id AND status = 'active') AS active_employees,
    (SELECT COUNT(*) FROM sales.customers WHERE company_id = c.id AND status = 'active') AS active_customers,
    (SELECT COUNT(*) FROM procurement.suppliers WHERE company_id = c.id AND status = 'active') AS active_suppliers,
    (SELECT COUNT(*) FROM inventory.products WHERE company_id = c.id AND status = 'active') AS active_products,
    (SELECT COALESCE(SUM(total_amount), 0) FROM sales.sales_orders WHERE company_id = c.id AND order_date >= DATE_TRUNC('month', CURRENT_DATE)) AS mtd_sales,
    (SELECT COALESCE(SUM(total_amount), 0) FROM procurement.purchase_orders WHERE company_id = c.id AND order_date >= DATE_TRUNC('month', CURRENT_DATE)) AS mtd_purchases
FROM public.companies c
WHERE c.status = 'active';

-- =====================================================
-- 函数 (Functions)
-- =====================================================

-- 生成单据编号函数
CREATE OR REPLACE FUNCTION public.generate_document_number(prefix VARCHAR, company_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
    seq_name VARCHAR;
    seq_val BIGINT;
    doc_no VARCHAR;
BEGIN
    seq_name := 'doc_seq_' || prefix || '_' || company_id;
    
    -- 创建序列（如果不存在）
    EXECUTE 'CREATE SEQUENCE IF NOT EXISTS ' || seq_name || ' START WITH 1';
    
    -- 获取下一个值
    EXECUTE 'SELECT nextval(''' || seq_name || ''')' INTO seq_val;
    
    -- 生成编号
    doc_no := prefix || TO_CHAR(NOW(), 'YYYYMMDD') || LPAD(seq_val::TEXT, 6, '0');
    RETURN doc_no;
END;
$$ LANGUAGE plpgsql;

-- 计算工作日函数
CREATE OR REPLACE FUNCTION public.count_working_days(start_date DATE, end_date DATE)
RETURNS INTEGER AS $$
DECLARE
    total_days INTEGER := 0;
    curr_date DATE := start_date;
BEGIN
    WHILE curr_date <= end_date LOOP
        IF EXTRACT(DOW FROM curr_date) NOT IN (0, 6) THEN
            total_days := total_days + 1;
        END IF;
        curr_date := curr_date + 1;
    END LOOP;
    RETURN total_days;
END;
$$ LANGUAGE plpgsql;

-- 更新员工数量触发器函数
CREATE OR REPLACE FUNCTION public.update_department_employee_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        UPDATE public.companies SET employee_count = (
            SELECT COUNT(*) FROM hr.employees WHERE company_id = NEW.company_id AND status = 'active'
        ) WHERE id = NEW.company_id;
    END IF;
    IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
        UPDATE public.companies SET employee_count = (
            SELECT COUNT(*) FROM hr.employees WHERE company_id = OLD.company_id AND status = 'active'
        ) WHERE id = OLD.company_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 触发器
CREATE TRIGGER trigger_update_company_employee_count
AFTER INSERT OR UPDATE OR DELETE ON hr.employees
FOR EACH ROW EXECUTE FUNCTION public.update_department_employee_count();
