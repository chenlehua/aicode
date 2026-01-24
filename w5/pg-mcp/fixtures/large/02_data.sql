-- =====================================================
-- Large Test Database: Enterprise ERP System - Test Data
-- 企业 ERP 系统测试数据
-- =====================================================

-- =====================================================
-- 公司数据 (3 companies)
-- =====================================================

INSERT INTO public.companies (code, name, legal_name, tax_id, address, city, country, phone, email, website, founded_date) VALUES
('ACME', 'ACME 集团', 'ACME 集团有限公司', '91110000123456789A', '北京市朝阳区建国路88号', '北京', 'China', '010-12345678', 'contact@acme.com', 'https://www.acme.com', '2000-01-01'),
('BETA', 'Beta 科技', 'Beta 科技股份有限公司', '91310000987654321B', '上海市浦东新区陆家嘴88号', '上海', 'China', '021-87654321', 'info@beta-tech.com', 'https://www.beta-tech.com', '2005-06-15'),
('GAMMA', 'Gamma 制造', 'Gamma 制造集团有限公司', '91440000567891234C', '广州市天河区珠江新城100号', '广州', 'China', '020-56789012', 'contact@gamma-mfg.com', 'https://www.gamma-mfg.com', '2010-03-20');

-- =====================================================
-- 地点数据 (10 locations)
-- =====================================================

INSERT INTO public.locations (company_id, code, name, address, city, province, postal_code, is_headquarters) VALUES
(1, 'BJ-HQ', '北京总部', '北京市朝阳区建国路88号', '北京', '北京市', '100022', TRUE),
(1, 'BJ-R&D', '北京研发中心', '北京市海淀区中关村软件园', '北京', '北京市', '100085', FALSE),
(1, 'SH-BR', '上海分公司', '上海市浦东新区张江高科', '上海', '上海市', '201203', FALSE),
(1, 'SZ-FAC', '深圳工厂', '深圳市宝安区福永街道', '深圳', '广东省', '518103', FALSE),
(2, 'SH-HQ', '上海总部', '上海市浦东新区陆家嘴', '上海', '上海市', '200120', TRUE),
(2, 'HZ-BR', '杭州分部', '杭州市余杭区未来科技城', '杭州', '浙江省', '311121', FALSE),
(2, 'NJ-BR', '南京分部', '南京市江宁区软件大道', '南京', '江苏省', '211100', FALSE),
(3, 'GZ-HQ', '广州总部', '广州市天河区珠江新城', '广州', '广东省', '510623', TRUE),
(3, 'DG-FAC', '东莞工厂', '东莞市长安镇工业园', '东莞', '广东省', '523850', FALSE),
(3, 'FS-FAC', '佛山工厂', '佛山市南海区狮山镇', '佛山', '广东省', '528200', FALSE);

-- =====================================================
-- 部门数据 (50 departments)
-- =====================================================

-- 一级部门
INSERT INTO public.departments (company_id, code, name, description, level, sort_order) VALUES
(1, 'CEO', '总裁办', '公司最高管理层', 1, 1),
(1, 'HR', '人力资源部', '负责人力资源管理', 1, 2),
(1, 'FIN', '财务部', '负责财务管理', 1, 3),
(1, 'R&D', '研发部', '负责产品研发', 1, 4),
(1, 'SALES', '销售部', '负责销售业务', 1, 5),
(1, 'MFG', '生产部', '负责生产制造', 1, 6),
(1, 'QA', '质量部', '负责质量管理', 1, 7),
(1, 'SCM', '供应链部', '负责供应链管理', 1, 8),
(1, 'IT', '信息技术部', '负责IT系统', 1, 9),
(1, 'ADMIN', '行政部', '负责行政事务', 1, 10);

-- 二级部门
INSERT INTO public.departments (company_id, parent_id, code, name, description, level, sort_order) VALUES
(1, 2, 'HR-REC', '招聘组', '负责招聘', 2, 1),
(1, 2, 'HR-TRN', '培训组', '负责培训发展', 2, 2),
(1, 2, 'HR-PAY', '薪酬组', '负责薪酬福利', 2, 3),
(1, 3, 'FIN-ACC', '会计组', '负责会计核算', 2, 1),
(1, 3, 'FIN-TAX', '税务组', '负责税务管理', 2, 2),
(1, 3, 'FIN-BUD', '预算组', '负责预算控制', 2, 3),
(1, 4, 'R&D-SW', '软件研发', '软件开发团队', 2, 1),
(1, 4, 'R&D-HW', '硬件研发', '硬件开发团队', 2, 2),
(1, 4, 'R&D-TEST', '测试组', '质量测试团队', 2, 3),
(1, 5, 'SALES-DOM', '国内销售', '国内市场销售', 2, 1),
(1, 5, 'SALES-INT', '国际销售', '国际市场销售', 2, 2),
(1, 5, 'SALES-KEY', '大客户部', '大客户管理', 2, 3),
(1, 6, 'MFG-ASM', '装配车间', '产品装配', 2, 1),
(1, 6, 'MFG-MAC', '机加工车间', '机械加工', 2, 2),
(1, 6, 'MFG-PKG', '包装车间', '产品包装', 2, 3),
(1, 8, 'SCM-PUR', '采购组', '物料采购', 2, 1),
(1, 8, 'SCM-WH', '仓储组', '仓库管理', 2, 2),
(1, 8, 'SCM-LOG', '物流组', '物流配送', 2, 3);

-- Beta 公司部门
INSERT INTO public.departments (company_id, code, name, description, level, sort_order) VALUES
(2, 'CEO', '总裁办', '公司最高管理层', 1, 1),
(2, 'HR', '人力资源部', '负责人力资源管理', 1, 2),
(2, 'FIN', '财务部', '负责财务管理', 1, 3),
(2, 'R&D', '研发部', '负责产品研发', 1, 4),
(2, 'SALES', '销售部', '负责销售业务', 1, 5),
(2, 'MKT', '市场部', '负责市场营销', 1, 6),
(2, 'OPS', '运营部', '负责运营管理', 1, 7),
(2, 'CS', '客服部', '负责客户服务', 1, 8);

-- Gamma 公司部门
INSERT INTO public.departments (company_id, code, name, description, level, sort_order) VALUES
(3, 'CEO', '总裁办', '公司最高管理层', 1, 1),
(3, 'HR', '人事部', '负责人事管理', 1, 2),
(3, 'FIN', '财务部', '负责财务管理', 1, 3),
(3, 'PROD', '生产部', '负责生产管理', 1, 4),
(3, 'QC', '品控部', '负责质量控制', 1, 5),
(3, 'PROC', '采购部', '负责采购管理', 1, 6),
(3, 'SALES', '销售部', '负责销售业务', 1, 7),
(3, 'MAINT', '设备部', '负责设备维护', 1, 8);

-- 更新部门路径
UPDATE public.departments SET path = '/' || id || '/' WHERE parent_id IS NULL;
UPDATE public.departments c SET path = (SELECT path FROM public.departments p WHERE p.id = c.parent_id) || c.id || '/' WHERE c.level = 2;

-- =====================================================
-- 职位数据 (40 positions)
-- =====================================================

INSERT INTO public.positions (company_id, department_id, code, title, description, salary_min, salary_max, headcount, level) VALUES
-- ACME 职位
(1, 1, 'CEO', '首席执行官', '公司最高管理者', 500000, 1000000, 1, 1),
(1, 1, 'VP', '副总裁', '分管业务副总', 300000, 500000, 3, 2),
(1, 2, 'HR-DIR', '人力资源总监', '人力资源负责人', 200000, 350000, 1, 3),
(1, 2, 'HR-MGR', '人力资源经理', '人力资源管理', 100000, 180000, 3, 4),
(1, 2, 'HR-SPEC', '人力资源专员', '人力资源执行', 60000, 100000, 10, 5),
(1, 3, 'CFO', '首席财务官', '财务负责人', 350000, 600000, 1, 2),
(1, 3, 'FIN-MGR', '财务经理', '财务管理', 120000, 200000, 3, 4),
(1, 3, 'ACCT', '会计', '会计核算', 60000, 100000, 15, 5),
(1, 4, 'CTO', '首席技术官', '技术负责人', 400000, 700000, 1, 2),
(1, 4, 'R&D-DIR', '研发总监', '研发管理', 250000, 400000, 2, 3),
(1, 4, 'SW-ARCH', '软件架构师', '系统架构设计', 200000, 350000, 5, 4),
(1, 4, 'SR-DEV', '高级开发工程师', '软件开发', 150000, 250000, 20, 5),
(1, 4, 'DEV', '开发工程师', '软件开发', 80000, 150000, 50, 6),
(1, 4, 'QA-ENG', '测试工程师', '质量测试', 70000, 120000, 20, 6),
(1, 5, 'SALES-DIR', '销售总监', '销售管理', 200000, 350000, 2, 3),
(1, 5, 'SALES-MGR', '销售经理', '区域销售管理', 100000, 180000, 8, 4),
(1, 5, 'SALES-REP', '销售代表', '销售执行', 60000, 120000, 30, 5),
(1, 6, 'PROD-DIR', '生产总监', '生产管理', 180000, 300000, 1, 3),
(1, 6, 'PROD-MGR', '生产经理', '车间管理', 100000, 160000, 5, 4),
(1, 6, 'PROD-SUP', '生产主管', '班组管理', 70000, 100000, 15, 5),
(1, 6, 'PROD-WKR', '生产工人', '生产操作', 40000, 70000, 100, 6),
-- Beta 职位
(2, 29, 'CEO', '首席执行官', '公司最高管理者', 400000, 800000, 1, 1),
(2, 32, 'CTO', '首席技术官', '技术负责人', 350000, 600000, 1, 2),
(2, 32, 'DEV', '开发工程师', '软件开发', 100000, 200000, 30, 5),
(2, 33, 'SALES-MGR', '销售经理', '销售管理', 120000, 200000, 5, 4),
(2, 33, 'SALES-REP', '销售代表', '销售执行', 70000, 150000, 20, 5),
-- Gamma 职位
(3, 37, 'CEO', '总经理', '公司最高管理者', 300000, 600000, 1, 1),
(3, 40, 'PROD-MGR', '生产经理', '生产管理', 100000, 180000, 3, 4),
(3, 40, 'PROD-WKR', '生产工人', '生产操作', 35000, 60000, 150, 6),
(3, 41, 'QC-MGR', 'QC经理', '质量管理', 90000, 150000, 2, 4),
(3, 43, 'SALES-REP', '销售代表', '销售执行', 50000, 100000, 15, 5);

-- =====================================================
-- 员工数据 (1000+ employees)
-- =====================================================

-- 核心管理层（手动插入）
INSERT INTO hr.employees (company_id, employee_no, first_name, last_name, gender, birth_date, phone, email, department_id, position_id, hire_date, contract_type, education_level, base_salary, status) VALUES
-- ACME 高管
(1, 'ACME-001', '志强', '张', 'male', '1970-05-15', '13800000001', 'zhiqiang.zhang@acme.com', 1, 1, '2000-01-01', 'full_time', 'master', 800000, 'active'),
(1, 'ACME-002', '美玲', '李', 'female', '1975-08-20', '13800000002', 'meiling.li@acme.com', 2, 3, '2002-03-15', 'full_time', 'master', 280000, 'active'),
(1, 'ACME-003', '建国', '王', 'male', '1972-11-08', '13800000003', 'jianguo.wang@acme.com', 3, 6, '2001-06-01', 'full_time', 'master', 450000, 'active'),
(1, 'ACME-004', '晓明', '赵', 'male', '1978-03-22', '13800000004', 'xiaoming.zhao@acme.com', 4, 9, '2005-01-10', 'full_time', 'doctorate', 550000, 'active'),
(1, 'ACME-005', '丽华', '刘', 'female', '1980-07-14', '13800000005', 'lihua.liu@acme.com', 5, 15, '2008-04-01', 'full_time', 'bachelor', 280000, 'active');

-- 批量生成员工
INSERT INTO hr.employees (company_id, employee_no, first_name, last_name, gender, birth_date, phone, email, department_id, position_id, hire_date, contract_type, education_level, base_salary, status)
SELECT 
    CASE WHEN gs <= 500 THEN 1 WHEN gs <= 750 THEN 2 ELSE 3 END,
    CASE WHEN gs <= 500 THEN 'ACME-' WHEN gs <= 750 THEN 'BETA-' ELSE 'GAMMA-' END || LPAD((gs % 500 + 6)::TEXT, 4, '0'),
    CASE (gs % 20)
        WHEN 0 THEN '伟' WHEN 1 THEN '芳' WHEN 2 THEN '明' WHEN 3 THEN '华' WHEN 4 THEN '强'
        WHEN 5 THEN '丽' WHEN 6 THEN '军' WHEN 7 THEN '敏' WHEN 8 THEN '磊' WHEN 9 THEN '娜'
        WHEN 10 THEN '静' WHEN 11 THEN '杰' WHEN 12 THEN '洋' WHEN 13 THEN '勇' WHEN 14 THEN '艳'
        WHEN 15 THEN '涛' WHEN 16 THEN '超' WHEN 17 THEN '霞' WHEN 18 THEN '鹏' ELSE '秀'
    END,
    CASE (gs % 10)
        WHEN 0 THEN '张' WHEN 1 THEN '李' WHEN 2 THEN '王' WHEN 3 THEN '刘' WHEN 4 THEN '陈'
        WHEN 5 THEN '杨' WHEN 6 THEN '赵' WHEN 7 THEN '黄' WHEN 8 THEN '周' ELSE '吴'
    END,
    CASE WHEN random() < 0.55 THEN 'male' ELSE 'female' END::hr.gender,
    (DATE '1970-01-01' + ((random() * 10000)::int || ' days')::interval)::date,
    '1' || LPAD((3800000000 + gs)::TEXT, 10, '0'),
    'emp' || gs || '@example.com',
    CASE WHEN gs <= 500 THEN 1 + (gs % 28) WHEN gs <= 750 THEN 29 + (gs % 8) ELSE 37 + (gs % 8) END,
    CASE WHEN gs <= 500 THEN 1 + (gs % 21) WHEN gs <= 750 THEN 22 + (gs % 5) ELSE 27 + (gs % 5) END,
    (DATE '2010-01-01' + ((random() * 5000)::int || ' days')::interval)::date,
    CASE WHEN random() < 0.85 THEN 'full_time' 
         WHEN random() < 0.95 THEN 'contract' 
         ELSE 'part_time' END::hr.contract_type,
    CASE (gs % 5)
        WHEN 0 THEN 'bachelor' WHEN 1 THEN 'master' WHEN 2 THEN 'bachelor'
        WHEN 3 THEN 'high_school' ELSE 'associate'
    END::hr.education_level,
    50000 + (random() * 200000)::int,
    CASE WHEN random() < 0.92 THEN 'active' 
         WHEN random() < 0.97 THEN 'on_leave' 
         ELSE 'resigned' END::hr.employee_status
FROM generate_series(6, 1005) AS gs;

-- 设置部门经理
UPDATE public.departments SET manager_id = 2 WHERE id = 2;
UPDATE public.departments SET manager_id = 3 WHERE id = 3;
UPDATE public.departments SET manager_id = 4 WHERE id = 4;
UPDATE public.departments SET manager_id = 5 WHERE id = 5;

-- =====================================================
-- 系统用户和角色数据
-- =====================================================

INSERT INTO public.roles (code, name, description, is_system) VALUES
('ADMIN', '系统管理员', '系统最高权限', TRUE),
('HR_ADMIN', '人事管理员', '人事模块管理', FALSE),
('FIN_ADMIN', '财务管理员', '财务模块管理', FALSE),
('SALES_ADMIN', '销售管理员', '销售模块管理', FALSE),
('INV_ADMIN', '库存管理员', '库存模块管理', FALSE),
('PROD_ADMIN', '生产管理员', '生产模块管理', FALSE),
('VIEWER', '只读用户', '只读权限', FALSE);

INSERT INTO public.permissions (code, name, module, description) VALUES
('hr.employee.read', '查看员工', 'hr', '查看员工信息'),
('hr.employee.write', '编辑员工', 'hr', '编辑员工信息'),
('hr.payroll.read', '查看薪资', 'hr', '查看薪资信息'),
('hr.payroll.write', '编辑薪资', 'hr', '编辑薪资信息'),
('finance.voucher.read', '查看凭证', 'finance', '查看会计凭证'),
('finance.voucher.write', '编辑凭证', 'finance', '编辑会计凭证'),
('inventory.stock.read', '查看库存', 'inventory', '查看库存信息'),
('inventory.stock.write', '调整库存', 'inventory', '调整库存数量'),
('sales.order.read', '查看订单', 'sales', '查看销售订单'),
('sales.order.write', '编辑订单', 'sales', '编辑销售订单'),
('procurement.po.read', '查看采购', 'procurement', '查看采购订单'),
('procurement.po.write', '编辑采购', 'procurement', '编辑采购订单'),
('production.wo.read', '查看工单', 'production', '查看生产工单'),
('production.wo.write', '编辑工单', 'production', '编辑生产工单');

-- 系统用户
INSERT INTO public.users (username, email, password_hash, employee_id, is_active, is_superuser) VALUES
('admin', 'admin@acme.com', '$2b$12$hash_admin', 1, TRUE, TRUE),
('hr_admin', 'hr_admin@acme.com', '$2b$12$hash_hr', 2, TRUE, FALSE),
('fin_admin', 'fin_admin@acme.com', '$2b$12$hash_fin', 3, TRUE, FALSE),
('cto', 'cto@acme.com', '$2b$12$hash_cto', 4, TRUE, FALSE),
('sales_dir', 'sales@acme.com', '$2b$12$hash_sales', 5, TRUE, FALSE);

-- =====================================================
-- 考勤数据 (30000+ records)
-- =====================================================

INSERT INTO hr.attendance (employee_id, attendance_date, check_in, check_out, work_hours, overtime_hours, attendance_type)
SELECT 
    e.id,
    d::date,
    d + TIME '08:30:00' + (random() * INTERVAL '1 hour'),
    d + TIME '17:30:00' + (random() * INTERVAL '3 hours'),
    8 + (random() * 3)::DECIMAL(4,2),
    CASE WHEN random() < 0.2 THEN (random() * 3)::DECIMAL(4,2) ELSE 0 END,
    CASE 
        WHEN random() < 0.85 THEN 'normal'
        WHEN random() < 0.92 THEN 'late'
        WHEN random() < 0.97 THEN 'early_leave'
        ELSE 'business_trip'
    END::hr.attendance_type
FROM hr.employees e
CROSS JOIN generate_series(
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE,
    '1 day'
) d
WHERE e.status = 'active' AND EXTRACT(DOW FROM d) NOT IN (0, 6) AND random() < 0.95
LIMIT 30000;

-- =====================================================
-- 请假数据 (500+ records)
-- =====================================================

INSERT INTO hr.leave_requests (employee_id, leave_type, start_date, end_date, days, reason, status, created_at)
SELECT 
    e.id,
    (ARRAY['annual', 'sick', 'personal', 'annual', 'sick'])[1 + floor(random() * 5)::int]::hr.leave_type,
    (CURRENT_DATE - ((random() * 180)::int || ' days')::interval)::date,
    (CURRENT_DATE - ((random() * 180)::int || ' days')::interval + ((1 + floor(random() * 5))::int || ' days')::interval)::date,
    1 + floor(random() * 5)::DECIMAL(4,1),
    CASE (floor(random() * 5)::int)
        WHEN 0 THEN '家庭事务需要处理'
        WHEN 1 THEN '身体不适需要休息'
        WHEN 2 THEN '个人事务'
        WHEN 3 THEN '年假休息'
        ELSE '医院检查'
    END,
    CASE WHEN random() < 0.8 THEN 'approved' WHEN random() < 0.95 THEN 'pending' ELSE 'rejected' END::VARCHAR(20),
    NOW() - (random() * 180 || ' days')::interval
FROM hr.employees e
WHERE e.status = 'active' AND random() < 0.5
LIMIT 500;

-- =====================================================
-- 薪资数据 (12000+ records, 12 months)
-- =====================================================

INSERT INTO hr.payroll (employee_id, pay_period, base_salary, overtime_pay, bonus, allowances, deductions, tax, social_insurance, housing_fund, net_salary, payment_date, payment_status)
SELECT 
    e.id,
    TO_CHAR(d, 'YYYY-MM'),
    e.base_salary / 12,
    (random() * 2000)::DECIMAL(12,2),
    CASE WHEN EXTRACT(MONTH FROM d) IN (1, 7) THEN (random() * 10000)::DECIMAL(12,2) ELSE 0 END,
    1000 + (random() * 1000)::DECIMAL(12,2),
    (random() * 500)::DECIMAL(12,2),
    (e.base_salary / 12 * 0.1)::DECIMAL(12,2),
    (e.base_salary / 12 * 0.08)::DECIMAL(12,2),
    (e.base_salary / 12 * 0.07)::DECIMAL(12,2),
    ((e.base_salary / 12) * 0.75)::DECIMAL(12,2),
    (d + INTERVAL '5 days')::date,
    CASE WHEN d < CURRENT_DATE THEN 'paid' ELSE 'pending' END
FROM hr.employees e
CROSS JOIN generate_series(
    DATE_TRUNC('month', CURRENT_DATE - INTERVAL '11 months'),
    DATE_TRUNC('month', CURRENT_DATE),
    '1 month'
) d
WHERE e.status = 'active'
LIMIT 12000;

-- =====================================================
-- 培训课程和记录
-- =====================================================

INSERT INTO hr.training_courses (code, name, description, category, duration_hours, instructor, max_participants, cost_per_person, is_mandatory) VALUES
('TRN-001', '新员工入职培训', '公司文化和规章制度', '入职培训', 8, '人力资源部', 30, 0, TRUE),
('TRN-002', '安全生产培训', '生产安全知识', '安全培训', 4, '安全部门', 50, 0, TRUE),
('TRN-003', 'Python 编程基础', 'Python 语言入门', '技术培训', 40, '技术培训师', 20, 2000, FALSE),
('TRN-004', '项目管理 PMP', 'PMP 认证培训', '管理培训', 60, '外部讲师', 30, 5000, FALSE),
('TRN-005', '领导力发展', '中层管理者领导力', '管理培训', 16, '外部讲师', 25, 3000, FALSE),
('TRN-006', 'Excel 高级应用', '数据分析和报表', '技能培训', 8, '内部培训师', 40, 500, FALSE),
('TRN-007', '沟通技巧', '有效沟通方法', '软技能', 8, '外部讲师', 30, 1000, FALSE),
('TRN-008', '质量管理体系', 'ISO 9001 培训', '质量培训', 16, '质量顾问', 40, 1500, FALSE);

INSERT INTO hr.training_records (employee_id, course_id, session_date, completion_date, score, passed, status, cost)
SELECT 
    e.id,
    c.id,
    (CURRENT_DATE - ((random() * 365)::int || ' days')::interval)::date,
    (CURRENT_DATE - ((random() * 365)::int || ' days')::interval + INTERVAL '5 days')::date,
    60 + (random() * 40)::DECIMAL(5,2),
    random() < 0.9,
    CASE WHEN random() < 0.7 THEN 'completed' WHEN random() < 0.9 THEN 'enrolled' ELSE 'cancelled' END,
    c.cost_per_person
FROM hr.employees e
CROSS JOIN hr.training_courses c
WHERE random() < 0.1
LIMIT 2000;

-- =====================================================
-- 财务数据
-- =====================================================

-- 会计科目
INSERT INTO finance.chart_of_accounts (company_id, account_code, account_name, account_type, level, is_header) VALUES
-- 资产类
(1, '1001', '库存现金', 'asset', 2, FALSE),
(1, '1002', '银行存款', 'asset', 2, FALSE),
(1, '1012', '其他货币资金', 'asset', 2, FALSE),
(1, '1101', '交易性金融资产', 'asset', 2, FALSE),
(1, '1121', '应收票据', 'asset', 2, FALSE),
(1, '1122', '应收账款', 'asset', 2, FALSE),
(1, '1123', '预付账款', 'asset', 2, FALSE),
(1, '1131', '应收股利', 'asset', 2, FALSE),
(1, '1132', '应收利息', 'asset', 2, FALSE),
(1, '1221', '其他应收款', 'asset', 2, FALSE),
(1, '1401', '材料采购', 'asset', 2, FALSE),
(1, '1402', '在途物资', 'asset', 2, FALSE),
(1, '1403', '原材料', 'asset', 2, FALSE),
(1, '1404', '库存商品', 'asset', 2, FALSE),
(1, '1601', '固定资产', 'asset', 2, FALSE),
(1, '1602', '累计折旧', 'asset', 2, FALSE),
-- 负债类
(1, '2001', '短期借款', 'liability', 2, FALSE),
(1, '2201', '应付票据', 'liability', 2, FALSE),
(1, '2202', '应付账款', 'liability', 2, FALSE),
(1, '2203', '预收账款', 'liability', 2, FALSE),
(1, '2211', '应付职工薪酬', 'liability', 2, FALSE),
(1, '2221', '应交税费', 'liability', 2, FALSE),
-- 所有者权益
(1, '4001', '实收资本', 'equity', 2, FALSE),
(1, '4002', '资本公积', 'equity', 2, FALSE),
(1, '4101', '盈余公积', 'equity', 2, FALSE),
(1, '4103', '本年利润', 'equity', 2, FALSE),
(1, '4104', '利润分配', 'equity', 2, FALSE),
-- 收入类
(1, '6001', '主营业务收入', 'revenue', 2, FALSE),
(1, '6051', '其他业务收入', 'revenue', 2, FALSE),
(1, '6111', '投资收益', 'revenue', 2, FALSE),
-- 费用类
(1, '6401', '主营业务成本', 'expense', 2, FALSE),
(1, '6402', '其他业务成本', 'expense', 2, FALSE),
(1, '6403', '营业税金及附加', 'expense', 2, FALSE),
(1, '6601', '销售费用', 'expense', 2, FALSE),
(1, '6602', '管理费用', 'expense', 2, FALSE),
(1, '6603', '财务费用', 'expense', 2, FALSE);

-- 会计期间
INSERT INTO finance.fiscal_periods (company_id, period_name, start_date, end_date, fiscal_year, period_number, is_closed) VALUES
(1, '2024-01', '2024-01-01', '2024-01-31', 2024, 1, TRUE),
(1, '2024-02', '2024-02-01', '2024-02-29', 2024, 2, TRUE),
(1, '2024-03', '2024-03-01', '2024-03-31', 2024, 3, TRUE),
(1, '2024-04', '2024-04-01', '2024-04-30', 2024, 4, TRUE),
(1, '2024-05', '2024-05-01', '2024-05-31', 2024, 5, TRUE),
(1, '2024-06', '2024-06-01', '2024-06-30', 2024, 6, TRUE),
(1, '2024-07', '2024-07-01', '2024-07-31', 2024, 7, TRUE),
(1, '2024-08', '2024-08-01', '2024-08-31', 2024, 8, TRUE),
(1, '2024-09', '2024-09-01', '2024-09-30', 2024, 9, TRUE),
(1, '2024-10', '2024-10-01', '2024-10-31', 2024, 10, TRUE),
(1, '2024-11', '2024-11-01', '2024-11-30', 2024, 11, TRUE),
(1, '2024-12', '2024-12-01', '2024-12-31', 2024, 12, FALSE),
(1, '2025-01', '2025-01-01', '2025-01-31', 2025, 1, FALSE);

-- 银行账户
INSERT INTO finance.bank_accounts (company_id, account_number, account_name, bank_name, branch_name, currency, current_balance, is_primary) VALUES
(1, '6222021234567890123', 'ACME 基本户', '中国工商银行', '北京朝阳支行', 'CNY', 5000000.00, TRUE),
(1, '6222021234567890124', 'ACME 一般户', '中国建设银行', '北京建国路支行', 'CNY', 2000000.00, FALSE),
(1, '6222021234567890125', 'ACME 外币户', '中国银行', '北京外汇支行', 'USD', 100000.00, FALSE),
(2, '6222029876543210987', 'Beta 基本户', '招商银行', '上海浦东支行', 'CNY', 3000000.00, TRUE),
(3, '6222025555666677778', 'Gamma 基本户', '中国农业银行', '广州天河支行', 'CNY', 2500000.00, TRUE);

-- =====================================================
-- 库存数据
-- =====================================================

-- 仓库
INSERT INTO inventory.warehouses (company_id, code, name, location_id, contact_person, contact_phone, capacity, is_active) VALUES
(1, 'WH-BJ-01', '北京主仓库', 1, '仓库主管', '13800001001', 10000, TRUE),
(1, 'WH-SZ-01', '深圳工厂仓库', 4, '工厂仓管', '13800001002', 20000, TRUE),
(1, 'WH-SH-01', '上海分仓', 3, '分仓主管', '13800001003', 5000, TRUE),
(2, 'WH-SH-HQ', 'Beta 上海仓库', 5, '仓库经理', '13800002001', 8000, TRUE),
(3, 'WH-GZ-01', 'Gamma 广州仓库', 8, '仓管员', '13800003001', 15000, TRUE),
(3, 'WH-DG-01', 'Gamma 东莞仓库', 9, '仓管员', '13800003002', 25000, TRUE);

-- 库位
INSERT INTO inventory.storage_locations (warehouse_id, code, name, zone, aisle, rack, shelf, bin, capacity, is_active)
SELECT 
    wh.id,
    'LOC-' || wh.code || '-' || LPAD(gs::TEXT, 4, '0'),
    zone || '-' || aisle || '-' || rack || '-' || shelf,
    zone,
    aisle,
    rack,
    shelf,
    bin,
    100,
    TRUE
FROM inventory.warehouses wh
CROSS JOIN LATERAL (
    SELECT 
        gs,
        (ARRAY['A', 'B', 'C', 'D'])[1 + (gs / 100) % 4] AS zone,
        LPAD(((gs / 10) % 10 + 1)::TEXT, 2, '0') AS aisle,
        LPAD((gs % 10 + 1)::TEXT, 2, '0') AS rack,
        LPAD((gs % 5 + 1)::TEXT, 2, '0') AS shelf,
        LPAD((gs % 10 + 1)::TEXT, 2, '0') AS bin
    FROM generate_series(1, 50) AS gs
) t;

-- 产品类别
INSERT INTO inventory.product_categories (company_id, code, name, level) VALUES
(1, 'RAW', '原材料', 1),
(1, 'RAW-MTL', '金属材料', 2),
(1, 'RAW-PLS', '塑料材料', 2),
(1, 'RAW-ELC', '电子元件', 2),
(1, 'WIP', '在制品', 1),
(1, 'FG', '成品', 1),
(1, 'FG-ELEC', '电子产品', 2),
(1, 'FG-MECH', '机械产品', 2),
(1, 'PKG', '包装材料', 1),
(1, 'SPARE', '备件', 1);

-- 更新类别父子关系
UPDATE inventory.product_categories SET parent_id = 1 WHERE code IN ('RAW-MTL', 'RAW-PLS', 'RAW-ELC');
UPDATE inventory.product_categories SET parent_id = 6 WHERE code IN ('FG-ELEC', 'FG-MECH');

-- 产品
INSERT INTO inventory.products (company_id, sku, name, description, category_id, uom, weight, minimum_stock, reorder_point, reorder_quantity, lead_time_days, standard_cost, selling_price, status)
SELECT 
    1,
    'SKU-' || LPAD(gs::TEXT, 6, '0'),
    CASE (gs % 10)
        WHEN 0 THEN '铝合金板材 ' || gs
        WHEN 1 THEN 'ABS塑料颗粒 ' || gs
        WHEN 2 THEN '电容器 ' || gs
        WHEN 3 THEN '电阻器 ' || gs
        WHEN 4 THEN '集成电路 ' || gs
        WHEN 5 THEN '智能控制器 ' || gs
        WHEN 6 THEN '电机组件 ' || gs
        WHEN 7 THEN '传感器模块 ' || gs
        WHEN 8 THEN '包装盒 ' || gs
        ELSE '备件 ' || gs
    END,
    '产品描述 ' || gs,
    1 + (gs % 10),
    CASE WHEN gs % 10 IN (0, 1) THEN 'KG' WHEN gs % 10 IN (8) THEN 'PCS' ELSE 'PCS' END,
    (random() * 10)::DECIMAL(10,3),
    10 + (random() * 90)::int,
    20 + (random() * 80)::int,
    100 + (random() * 400)::int,
    7 + (random() * 21)::int,
    10 + (random() * 990)::DECIMAL(15,4),
    20 + (random() * 1980)::DECIMAL(15,2),
    'active'
FROM generate_series(1, 300) AS gs;

-- 库存
INSERT INTO inventory.stock (product_id, warehouse_id, location_id, quantity_on_hand, quantity_reserved, last_count_date)
SELECT 
    p.id,
    w.id,
    (SELECT id FROM inventory.storage_locations WHERE warehouse_id = w.id ORDER BY random() LIMIT 1),
    (random() * 500)::DECIMAL(15,3),
    (random() * 50)::DECIMAL(15,3),
    CURRENT_DATE - (random() * 30)::int
FROM inventory.products p
CROSS JOIN inventory.warehouses w
WHERE random() < 0.4
LIMIT 500;

-- =====================================================
-- 销售数据
-- =====================================================

-- 客户
INSERT INTO sales.customers (company_id, customer_code, name, legal_name, tax_id, customer_type, contact_person, phone, email, billing_address, shipping_address, city, credit_limit, payment_terms)
SELECT 
    1,
    'CUST-' || LPAD(gs::TEXT, 5, '0'),
    CASE (gs % 10)
        WHEN 0 THEN '华为技术有限公司'
        WHEN 1 THEN '阿里巴巴集团'
        WHEN 2 THEN '腾讯科技'
        WHEN 3 THEN '京东商城'
        WHEN 4 THEN '字节跳动'
        WHEN 5 THEN '美团点评'
        WHEN 6 THEN '小米科技'
        WHEN 7 THEN '网易公司'
        WHEN 8 THEN '百度在线'
        ELSE '拼多多'
    END || ' 分公司 ' || gs,
    '客户法人名称 ' || gs,
    '91' || LPAD(gs::TEXT, 15, '0') || 'A',
    CASE WHEN gs % 5 = 0 THEN 'vip' WHEN gs % 3 = 0 THEN 'enterprise' ELSE 'regular' END,
    '联系人 ' || gs,
    '13' || LPAD((900000000 + gs)::TEXT, 9, '0'),
    'customer' || gs || '@example.com',
    '客户账单地址 ' || gs,
    '客户收货地址 ' || gs,
    CASE (gs % 5) WHEN 0 THEN '北京' WHEN 1 THEN '上海' WHEN 2 THEN '广州' WHEN 3 THEN '深圳' ELSE '杭州' END,
    100000 + (random() * 900000)::DECIMAL(15,2),
    CASE WHEN gs % 3 = 0 THEN 30 WHEN gs % 3 = 1 THEN 45 ELSE 60 END
FROM generate_series(1, 200) AS gs;

-- 销售订单
INSERT INTO sales.sales_orders (company_id, order_no, customer_id, order_date, warehouse_id, currency, subtotal, discount_amount, tax_amount, total_amount, shipping_address, status, created_at)
SELECT 
    1,
    'SO-' || TO_CHAR(CURRENT_DATE - (gs || ' days')::interval, 'YYYYMMDD') || '-' || LPAD(gs::TEXT, 4, '0'),
    (SELECT id FROM sales.customers ORDER BY random() LIMIT 1),
    CURRENT_DATE - (gs || ' days')::interval,
    (SELECT id FROM inventory.warehouses WHERE company_id = 1 ORDER BY random() LIMIT 1),
    'CNY',
    (random() * 100000)::DECIMAL(15,2),
    (random() * 5000)::DECIMAL(15,2),
    (random() * 10000)::DECIMAL(15,2),
    (random() * 100000)::DECIMAL(15,2),
    '收货地址 ' || gs,
    (ARRAY['confirmed', 'processing', 'shipped', 'delivered', 'delivered', 'delivered'])[1 + (gs % 6)]::sales.order_status,
    NOW() - (gs || ' days')::interval
FROM generate_series(1, 500) AS gs;

-- 销售订单明细
INSERT INTO sales.sales_order_lines (order_id, line_no, product_id, description, quantity, uom, unit_price, tax_rate, tax_amount, line_total)
SELECT 
    so.id,
    row_number() OVER (PARTITION BY so.id ORDER BY p.id),
    p.id,
    p.name,
    1 + (random() * 50)::int,
    p.uom,
    p.selling_price,
    13,
    (p.selling_price * (1 + (random() * 50)::int) * 0.13)::DECIMAL(15,2),
    (p.selling_price * (1 + (random() * 50)::int) * 1.13)::DECIMAL(15,2)
FROM sales.sales_orders so
CROSS JOIN LATERAL (
    SELECT id, name, uom, selling_price FROM inventory.products ORDER BY random() LIMIT (2 + floor(random() * 5)::int)
) p
LIMIT 2000;

-- =====================================================
-- 采购数据
-- =====================================================

-- 供应商
INSERT INTO procurement.suppliers (company_id, supplier_code, name, legal_name, tax_id, supplier_type, contact_person, phone, email, address, city, payment_terms, rating)
SELECT 
    1,
    'SUP-' || LPAD(gs::TEXT, 5, '0'),
    CASE (gs % 8)
        WHEN 0 THEN '华东金属材料公司'
        WHEN 1 THEN '南方塑料原料厂'
        WHEN 2 THEN '深圳电子元器件公司'
        WHEN 3 THEN '东莞精密五金厂'
        WHEN 4 THEN '苏州包装材料公司'
        WHEN 5 THEN '浙江化工材料厂'
        WHEN 6 THEN '上海电气设备公司'
        ELSE '广州通用零部件厂'
    END || ' ' || gs,
    '供应商法人名称 ' || gs,
    '91' || LPAD((2000000000 + gs)::TEXT, 15, '0') || 'B',
    CASE WHEN gs % 4 = 0 THEN 'manufacturer' WHEN gs % 4 = 1 THEN 'distributor' ELSE 'trading' END,
    '采购联系人 ' || gs,
    '13' || LPAD((800000000 + gs)::TEXT, 9, '0'),
    'supplier' || gs || '@example.com',
    '供应商地址 ' || gs,
    CASE (gs % 5) WHEN 0 THEN '东莞' WHEN 1 THEN '苏州' WHEN 2 THEN '深圳' WHEN 3 THEN '宁波' ELSE '佛山' END,
    CASE WHEN gs % 3 = 0 THEN 30 WHEN gs % 3 = 1 THEN 45 ELSE 60 END,
    3 + floor(random() * 3)::int
FROM generate_series(1, 100) AS gs;

-- 供应商产品目录
INSERT INTO procurement.supplier_products (supplier_id, product_id, supplier_sku, unit_price, minimum_order_qty, lead_time_days, is_preferred)
SELECT 
    s.id,
    p.id,
    'SUP-' || s.id || '-' || p.sku,
    p.standard_cost * (0.8 + random() * 0.4),
    10 + floor(random() * 90)::int,
    7 + floor(random() * 21)::int,
    random() < 0.3
FROM procurement.suppliers s
CROSS JOIN inventory.products p
WHERE random() < 0.1
LIMIT 500;

-- 采购订单
INSERT INTO procurement.purchase_orders (company_id, po_no, supplier_id, order_date, expected_date, warehouse_id, currency, subtotal, tax_amount, total_amount, status, created_at)
SELECT 
    1,
    'PO-' || TO_CHAR(CURRENT_DATE - (gs || ' days')::interval, 'YYYYMMDD') || '-' || LPAD(gs::TEXT, 4, '0'),
    (SELECT id FROM procurement.suppliers ORDER BY random() LIMIT 1),
    CURRENT_DATE - (gs || ' days')::interval,
    (CURRENT_DATE - (gs || ' days')::interval + ((14 + floor(random() * 14))::int || ' days')::interval)::date,
    (SELECT id FROM inventory.warehouses WHERE company_id = 1 ORDER BY random() LIMIT 1),
    'CNY',
    (random() * 50000)::DECIMAL(15,2),
    (random() * 5000)::DECIMAL(15,2),
    (random() * 55000)::DECIMAL(15,2),
    (ARRAY['approved', 'ordered', 'partial_received', 'received', 'received', 'received'])[1 + (gs % 6)]::procurement.po_status,
    NOW() - (gs || ' days')::interval
FROM generate_series(1, 300) AS gs;

-- 采购订单明细
INSERT INTO procurement.purchase_order_lines (po_id, line_no, product_id, description, quantity, uom, unit_price, tax_rate, tax_amount, line_total)
SELECT 
    po.id,
    row_number() OVER (PARTITION BY po.id ORDER BY p.id),
    p.id,
    p.name,
    10 + (random() * 200)::int,
    p.uom,
    p.standard_cost,
    13,
    (p.standard_cost * (10 + (random() * 200)::int) * 0.13)::DECIMAL(15,2),
    (p.standard_cost * (10 + (random() * 200)::int) * 1.13)::DECIMAL(15,2)
FROM procurement.purchase_orders po
CROSS JOIN LATERAL (
    SELECT id, name, uom, standard_cost FROM inventory.products ORDER BY random() LIMIT (2 + floor(random() * 4)::int)
) p
LIMIT 1200;

-- =====================================================
-- 生产数据
-- =====================================================

-- BOM
INSERT INTO production.bom (company_id, bom_no, product_id, version, description, standard_quantity, is_active)
SELECT 
    1,
    'BOM-' || LPAD(gs::TEXT, 5, '0'),
    (SELECT id FROM inventory.products WHERE category_id IN (6, 7, 8) ORDER BY random() LIMIT 1),
    '1.0',
    'BOM 版本 1.0',
    1,
    TRUE
FROM generate_series(1, 50) AS gs;

-- BOM 明细
INSERT INTO production.bom_lines (bom_id, line_no, component_id, quantity, uom, scrap_rate, is_critical)
SELECT 
    b.id,
    row_number() OVER (PARTITION BY b.id ORDER BY p.id),
    p.id,
    1 + (random() * 10)::DECIMAL(15,6),
    p.uom,
    (random() * 5)::DECIMAL(5,2),
    random() < 0.2
FROM production.bom b
CROSS JOIN LATERAL (
    SELECT id, uom FROM inventory.products WHERE category_id IN (1, 2, 3, 4) ORDER BY random() LIMIT (3 + floor(random() * 5)::int)
) p;

-- 生产工单
INSERT INTO production.work_orders (company_id, wo_no, product_id, bom_id, planned_quantity, completed_quantity, warehouse_id, planned_start, planned_end, status, created_at)
SELECT 
    1,
    'WO-' || TO_CHAR(CURRENT_DATE - (gs || ' days')::interval, 'YYYYMMDD') || '-' || LPAD(gs::TEXT, 4, '0'),
    b.product_id,
    b.id,
    50 + (random() * 450)::int,
    CASE WHEN gs > 50 THEN (50 + (random() * 450)::int) ELSE (random() * 200)::int END,
    (SELECT id FROM inventory.warehouses WHERE company_id = 1 ORDER BY random() LIMIT 1),
    CURRENT_DATE - (gs || ' days')::interval,
    (CURRENT_DATE - (gs || ' days')::interval + ((7 + floor(random() * 14))::int || ' days')::interval)::date,
    CASE 
        WHEN gs <= 20 THEN 'planned'
        WHEN gs <= 40 THEN 'in_progress'
        WHEN gs <= 50 THEN 'released'
        ELSE 'completed'
    END::production.work_order_status,
    NOW() - (gs || ' days')::interval
FROM generate_series(1, 200) AS gs
CROSS JOIN LATERAL (
    SELECT id, product_id FROM production.bom ORDER BY random() LIMIT 1
) b;

-- 质量检验
INSERT INTO production.quality_inspections (company_id, inspection_no, inspection_type, product_id, lot_number, inspection_date, quantity_inspected, quantity_passed, quantity_failed, result, notes)
SELECT 
    1,
    'QC-' || TO_CHAR(CURRENT_DATE - (gs || ' days')::interval, 'YYYYMMDD') || '-' || LPAD(gs::TEXT, 4, '0'),
    (ARRAY['incoming', 'in_process', 'final'])[1 + (gs % 3)],
    (SELECT id FROM inventory.products ORDER BY random() LIMIT 1),
    'LOT-' || TO_CHAR(CURRENT_DATE - (gs || ' days')::interval, 'YYYYMMDD') || '-' || gs,
    CURRENT_DATE - (gs || ' days')::interval,
    (100 + random() * 400)::DECIMAL(15,3),
    (90 + random() * 360)::DECIMAL(15,3),
    (random() * 50)::DECIMAL(15,3),
    CASE WHEN random() < 0.9 THEN 'pass' WHEN random() < 0.95 THEN 'conditional' ELSE 'fail' END::production.qc_result,
    '检验备注 ' || gs
FROM generate_series(1, 300) AS gs;

-- =====================================================
-- 更新统计数据
-- =====================================================

-- 更新公司员工数量
UPDATE public.companies SET employee_count = (
    SELECT COUNT(*) FROM hr.employees WHERE company_id = companies.id AND status = 'active'
);

-- 更新职位当前人数
UPDATE public.positions SET current_count = (
    SELECT COUNT(*) FROM hr.employees WHERE position_id = positions.id AND status = 'active'
);
