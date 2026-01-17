# Interview Database - Natural Language to SQL Examples

本文档包含面试管理系统数据库的自然语言查询描述及对应的 SQL 语句，用于测试 Text-to-SQL 能力。

---

## 1. 基础查询

### 1.1 查询所有正在招聘的职位
**问题**: 列出所有状态为开放的职位，显示职位名称、部门、薪资范围和招聘人数

```sql
SELECT p.title AS 职位名称, d.name AS 部门,
       p.salary_min AS 最低薪资, p.salary_max AS 最高薪资,
       p.headcount AS 招聘人数
FROM positions p
JOIN departments d ON p.department_id = d.id
WHERE p.status = 'open'
ORDER BY p.priority DESC, p.posted_at;
```

### 1.2 查找特定技能的候选人
**问题**: 找出所有掌握 Java 技能且熟练程度为高级或专家级别的候选人

```sql
SELECT c.name AS 候选人姓名, c.email, c.current_company AS 当前公司,
       cs.proficiency_level AS 熟练程度, cs.years_experience AS 经验年限
FROM candidates c
JOIN candidate_skills cs ON c.id = cs.candidate_id
JOIN skills s ON cs.skill_id = s.id
WHERE s.name = 'Java'
  AND cs.proficiency_level IN ('advanced', 'expert')
ORDER BY cs.years_experience DESC;
```

### 1.3 查看某个候选人的完整信息
**问题**: 获取候选人"李明辉"的详细信息，包括教育背景、工作经历和期望薪资

```sql
SELECT name AS 姓名, email AS 邮箱, phone AS 电话,
       current_company AS 当前公司, current_position AS 当前职位,
       years_of_experience AS 工作年限, education_level AS 学历,
       university AS 毕业院校, major AS 专业, graduation_year AS 毕业年份,
       expected_salary AS 期望薪资, notice_period AS 离职周期
FROM candidates
WHERE name = '李明辉';
```

---

## 2. 聚合统计查询

### 2.1 各部门招聘进度统计
**问题**: 统计每个部门的招聘职位数、总需求人数、已入职人数和剩余需求

```sql
SELECT d.name AS 部门名称,
       COUNT(p.id) AS 招聘职位数,
       SUM(p.headcount) AS 总需求人数,
       SUM(p.filled_count) AS 已入职人数,
       SUM(p.headcount - p.filled_count) AS 剩余需求
FROM departments d
LEFT JOIN positions p ON d.id = p.department_id AND p.status = 'open'
GROUP BY d.id, d.name
HAVING COUNT(p.id) > 0
ORDER BY 剩余需求 DESC;
```

### 2.2 招聘渠道效果分析
**问题**: 分析各招聘渠道的候选人数量、入职人数和转化率，按转化率降序排列

```sql
SELECT rc.name AS 渠道名称, rc.type AS 渠道类型,
       COUNT(c.id) AS 候选人数量,
       SUM(CASE WHEN c.status = 'hired' THEN 1 ELSE 0 END) AS 入职人数,
       ROUND(SUM(CASE WHEN c.status = 'hired' THEN 1 ELSE 0 END) * 100.0 /
             NULLIF(COUNT(c.id), 0), 2) AS 转化率,
       rc.cost_per_hire AS 单人成本
FROM recruitment_channels rc
LEFT JOIN candidates c ON rc.id = c.source_channel_id
GROUP BY rc.id, rc.name, rc.type, rc.cost_per_hire
ORDER BY 转化率 DESC;
```

### 2.3 面试官工作量统计
**问题**: 统计每位面试官参与的面试次数、已完成面试数、待进行面试数，以及给出的平均评分

```sql
SELECT e.name AS 面试官姓名, d.name AS 所属部门,
       COUNT(DISTINCT ip.interview_id) AS 参与面试总数,
       SUM(CASE WHEN i.status = 'completed' THEN 1 ELSE 0 END) AS 已完成面试,
       SUM(CASE WHEN i.status = 'scheduled' THEN 1 ELSE 0 END) AS 待进行面试,
       ROUND(AVG(f.overall_score), 2) AS 平均评分
FROM employees e
JOIN departments d ON e.department_id = d.id
LEFT JOIN interview_panelists ip ON e.id = ip.interviewer_id
LEFT JOIN interviews i ON ip.interview_id = i.id
LEFT JOIN interview_feedback f ON i.id = f.interview_id AND e.id = f.interviewer_id
WHERE e.is_interviewer = TRUE
GROUP BY e.id, e.name, d.name
ORDER BY 参与面试总数 DESC;
```

### 2.4 各职级薪资范围分析
**问题**: 按职位级别统计平均薪资范围（最低和最高），以及对应的职位数量

```sql
SELECT job_level AS 职位级别,
       COUNT(*) AS 职位数量,
       ROUND(AVG(salary_min), 0) AS 平均最低薪资,
       ROUND(AVG(salary_max), 0) AS 平均最高薪资,
       MIN(salary_min) AS 最低薪资下限,
       MAX(salary_max) AS 最高薪资上限
FROM positions
WHERE status = 'open'
GROUP BY job_level
ORDER BY 平均最高薪资 DESC;
```

---

## 3. 多表关联查询

### 3.1 候选人面试全流程追踪
**问题**: 查看所有正在面试中的候选人，显示其申请的职位、已完成的面试轮次、最近一次面试时间和平均评分

```sql
SELECT c.name AS 候选人姓名, c.current_company AS 当前公司,
       p.title AS 申请职位, d.name AS 目标部门,
       COUNT(DISTINCT CASE WHEN i.status = 'completed' THEN i.id END) AS 已完成面试轮数,
       MAX(i.scheduled_at) AS 最近面试时间,
       ROUND(AVG(f.overall_score), 2) AS 平均评分
FROM candidates c
JOIN applications a ON c.id = a.candidate_id
JOIN positions p ON a.position_id = p.id
JOIN departments d ON p.department_id = d.id
LEFT JOIN interviews i ON a.id = i.application_id
LEFT JOIN interview_feedback f ON i.id = f.interview_id
WHERE a.status = 'interviewing'
GROUP BY c.id, c.name, c.current_company, p.title, d.name
ORDER BY 最近面试时间 DESC;
```

### 3.2 职位技能匹配度分析
**问题**: 对于"高级Java开发工程师"职位，找出技能匹配度最高的候选人（匹配技能数量/职位要求技能数量）

```sql
SELECT c.name AS 候选人姓名, c.years_of_experience AS 工作年限,
       COUNT(DISTINCT cs.skill_id) AS 匹配技能数,
       (SELECT COUNT(*) FROM position_skills WHERE position_id = p.id) AS 要求技能数,
       ROUND(COUNT(DISTINCT cs.skill_id) * 100.0 /
             (SELECT COUNT(*) FROM position_skills WHERE position_id = p.id), 2) AS 匹配度
FROM positions p
JOIN position_skills ps ON p.id = ps.position_id
JOIN candidate_skills cs ON ps.skill_id = cs.skill_id
JOIN candidates c ON cs.candidate_id = c.id
WHERE p.title = '高级Java开发工程师'
  AND c.status NOT IN ('hired', 'rejected', 'withdrawn', 'blacklisted')
GROUP BY c.id, c.name, c.years_of_experience, p.id
ORDER BY 匹配度 DESC, 工作年限 DESC
LIMIT 10;
```

### 3.3 Offer 详情查询
**问题**: 列出所有已发出但尚未回复的 Offer，显示候选人信息、职位、薪资待遇和过期日期

```sql
SELECT c.name AS 候选人姓名, c.email AS 邮箱,
       o.job_title AS 职位, o.job_level AS 职级,
       d.name AS 部门, o.base_salary AS 基本薪资,
       o.bonus_percentage AS 奖金比例, o.signing_bonus AS 签字费,
       o.equity_shares AS 股权数量, o.start_date AS 入职日期,
       o.expiry_date AS 过期日期, o.status AS 状态
FROM offers o
JOIN applications a ON o.application_id = a.id
JOIN candidates c ON a.candidate_id = c.id
JOIN departments d ON o.department_id = d.id
WHERE o.status = 'sent'
ORDER BY o.expiry_date;
```

### 3.4 面试反馈汇总
**问题**: 查看候选人"张鹏程"所有面试的详细反馈，包括面试轮次、面试官、各项评分和录用建议

```sql
SELECT irt.name AS 面试轮次, i.scheduled_at AS 面试时间,
       e.name AS 面试官,
       f.technical_score AS 技术评分,
       f.communication_score AS 沟通评分,
       f.problem_solving_score AS 解决问题评分,
       f.culture_fit_score AS 文化匹配评分,
       f.overall_score AS 综合评分,
       f.recommendation AS 录用建议,
       f.strengths AS 优势, f.weaknesses AS 不足
FROM candidates c
JOIN applications a ON c.id = a.candidate_id
JOIN interviews i ON a.id = i.application_id
JOIN interview_round_types irt ON i.round_type_id = irt.id
JOIN interview_feedback f ON i.id = f.interview_id
JOIN employees e ON f.interviewer_id = e.id
WHERE c.name = '张鹏程'
ORDER BY i.scheduled_at, irt.sequence;
```

---

## 4. 子查询与复杂条件

### 4.1 高于平均期望薪资的候选人
**问题**: 找出期望薪资高于所有候选人平均期望薪资的候选人，并显示其高出的百分比

```sql
SELECT name AS 候选人姓名, current_company AS 当前公司,
       expected_salary AS 期望薪资,
       (SELECT ROUND(AVG(expected_salary), 0) FROM candidates WHERE expected_salary IS NOT NULL) AS 平均期望薪资,
       ROUND((expected_salary - (SELECT AVG(expected_salary) FROM candidates WHERE expected_salary IS NOT NULL)) * 100.0 /
             (SELECT AVG(expected_salary) FROM candidates WHERE expected_salary IS NOT NULL), 2) AS 高出百分比
FROM candidates
WHERE expected_salary > (SELECT AVG(expected_salary) FROM candidates WHERE expected_salary IS NOT NULL)
ORDER BY expected_salary DESC;
```

### 4.2 从未参加面试的候选人
**问题**: 找出已提交申请但从未被安排面试的候选人

```sql
SELECT c.name AS 候选人姓名, c.email AS 邮箱,
       p.title AS 申请职位, a.application_date AS 申请日期,
       a.status AS 申请状态
FROM candidates c
JOIN applications a ON c.id = a.candidate_id
JOIN positions p ON a.position_id = p.id
WHERE NOT EXISTS (
    SELECT 1 FROM interviews i WHERE i.application_id = a.id
)
ORDER BY a.application_date;
```

### 4.3 内推成功率分析
**问题**: 统计每位推荐人的推荐成功率（被推荐候选人入职的比例）

```sql
SELECT e.name AS 推荐人姓名, e.department_id,
       d.name AS 所属部门,
       COUNT(c.id) AS 推荐候选人数,
       SUM(CASE WHEN c.status = 'hired' THEN 1 ELSE 0 END) AS 成功入职数,
       ROUND(SUM(CASE WHEN c.status = 'hired' THEN 1 ELSE 0 END) * 100.0 /
             NULLIF(COUNT(c.id), 0), 2) AS 推荐成功率
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN candidates c ON e.id = c.referrer_id
GROUP BY e.id, e.name, e.department_id, d.name
ORDER BY 推荐成功率 DESC, 推荐候选人数 DESC;
```

### 4.4 职位竞争激烈程度
**问题**: 计算每个开放职位的竞争程度（申请人数/招聘人数），找出竞争最激烈的前5个职位

```sql
SELECT p.title AS 职位名称, d.name AS 部门,
       p.headcount AS 招聘人数,
       COUNT(a.id) AS 申请人数,
       ROUND(COUNT(a.id) * 1.0 / p.headcount, 2) AS 竞争比
FROM positions p
JOIN departments d ON p.department_id = d.id
LEFT JOIN applications a ON p.id = a.position_id
WHERE p.status = 'open'
GROUP BY p.id, p.title, d.name, p.headcount
ORDER BY 竞争比 DESC
LIMIT 5;
```

---

## 5. 时间相关查询

### 5.1 本周待进行的面试
**问题**: 列出本周所有待进行的面试，包括候选人、职位、面试时间、面试官和面试类型

```sql
SELECT c.name AS 候选人姓名, p.title AS 应聘职位,
       i.scheduled_at AS 面试时间, i.interview_mode AS 面试方式,
       irt.name AS 面试轮次,
       GROUP_CONCAT(e.name SEPARATOR ', ') AS 面试官,
       i.location AS 地点, i.meeting_link AS 会议链接
FROM interviews i
JOIN applications a ON i.application_id = a.id
JOIN candidates c ON a.candidate_id = c.id
JOIN positions p ON a.position_id = p.id
JOIN interview_round_types irt ON i.round_type_id = irt.id
JOIN interview_panelists ip ON i.id = ip.interview_id
JOIN employees e ON ip.interviewer_id = e.id
WHERE i.status = 'scheduled'
  AND i.scheduled_at >= CURDATE()
  AND i.scheduled_at < DATE_ADD(CURDATE(), INTERVAL 7 DAY)
GROUP BY i.id, c.name, p.title, i.scheduled_at, i.interview_mode,
         irt.name, i.location, i.meeting_link
ORDER BY i.scheduled_at;
```

### 5.2 招聘周期分析
**问题**: 计算已成功入职的候选人从申请到发出 Offer 的平均天数，按职位级别分组

```sql
SELECT p.job_level AS 职位级别,
       COUNT(DISTINCT o.id) AS 入职人数,
       ROUND(AVG(DATEDIFF(o.offer_date, a.application_date)), 1) AS 平均招聘周期天数,
       MIN(DATEDIFF(o.offer_date, a.application_date)) AS 最短周期,
       MAX(DATEDIFF(o.offer_date, a.application_date)) AS 最长周期
FROM offers o
JOIN applications a ON o.application_id = a.id
JOIN positions p ON a.position_id = p.id
WHERE o.status = 'accepted'
GROUP BY p.job_level
ORDER BY 平均招聘周期天数;
```

### 5.3 面试超期未反馈统计
**问题**: 找出已完成但超过3天未提交反馈的面试

```sql
SELECT i.id AS 面试ID, c.name AS 候选人姓名, p.title AS 应聘职位,
       irt.name AS 面试轮次, i.scheduled_at AS 面试时间,
       e.name AS 面试官,
       DATEDIFF(CURDATE(), i.scheduled_at) AS 已过天数
FROM interviews i
JOIN applications a ON i.application_id = a.id
JOIN candidates c ON a.candidate_id = c.id
JOIN positions p ON a.position_id = p.id
JOIN interview_round_types irt ON i.round_type_id = irt.id
JOIN interview_panelists ip ON i.id = ip.interview_id
JOIN employees e ON ip.interviewer_id = e.id
WHERE i.status = 'completed'
  AND NOT EXISTS (
      SELECT 1 FROM interview_feedback f
      WHERE f.interview_id = i.id AND f.interviewer_id = e.id AND f.is_submitted = TRUE
  )
  AND DATEDIFF(CURDATE(), i.scheduled_at) > 3
ORDER BY i.scheduled_at;
```

### 5.4 月度招聘趋势
**问题**: 统计最近6个月每月的申请数、面试数、Offer数和入职数

```sql
SELECT DATE_FORMAT(a.application_date, '%Y-%m') AS 月份,
       COUNT(DISTINCT a.id) AS 申请数,
       COUNT(DISTINCT i.id) AS 面试数,
       COUNT(DISTINCT o.id) AS Offer数,
       SUM(CASE WHEN o.status = 'accepted' THEN 1 ELSE 0 END) AS 入职数
FROM applications a
LEFT JOIN interviews i ON a.id = i.application_id
LEFT JOIN offers o ON a.id = o.application_id
WHERE a.application_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY DATE_FORMAT(a.application_date, '%Y-%m')
ORDER BY 月份;
```

---

## 6. 高级分析查询

### 6.1 候选人漏斗分析
**问题**: 分析招聘漏斗，统计各阶段的候选人数量和转化率

```sql
SELECT
    '申请' AS 阶段,
    COUNT(*) AS 人数,
    100.00 AS 转化率
FROM applications
UNION ALL
SELECT
    '面试中' AS 阶段,
    COUNT(*) AS 人数,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM applications), 2) AS 转化率
FROM applications WHERE status IN ('interviewing', 'interview_scheduled')
UNION ALL
SELECT
    '待Offer' AS 阶段,
    COUNT(*) AS 人数,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM applications), 2) AS 转化率
FROM applications WHERE status = 'offer_pending'
UNION ALL
SELECT
    '已发Offer' AS 阶段,
    COUNT(*) AS 人数,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM applications), 2) AS 转化率
FROM applications WHERE status IN ('offered', 'accepted')
UNION ALL
SELECT
    '已入职' AS 阶段,
    COUNT(*) AS 人数,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM applications), 2) AS 转化率
FROM applications WHERE status = 'accepted';
```

### 6.2 面试官评分倾向分析
**问题**: 分析每位面试官的评分习惯，找出评分偏高或偏低的面试官

```sql
SELECT e.name AS 面试官姓名,
       COUNT(f.id) AS 评分次数,
       ROUND(AVG(f.overall_score), 2) AS 平均分,
       (SELECT ROUND(AVG(overall_score), 2) FROM interview_feedback) AS 全体平均分,
       ROUND(AVG(f.overall_score) - (SELECT AVG(overall_score) FROM interview_feedback), 2) AS 偏差值,
       CASE
           WHEN AVG(f.overall_score) > (SELECT AVG(overall_score) FROM interview_feedback) + 0.5 THEN '偏高'
           WHEN AVG(f.overall_score) < (SELECT AVG(overall_score) FROM interview_feedback) - 0.5 THEN '偏低'
           ELSE '正常'
       END AS 评分倾向
FROM employees e
JOIN interview_feedback f ON e.id = f.interviewer_id
WHERE f.is_submitted = TRUE
GROUP BY e.id, e.name
HAVING COUNT(f.id) >= 3
ORDER BY 偏差值 DESC;
```

### 6.3 技能需求热度排名
**问题**: 统计所有开放职位中各技能的需求次数，找出最热门的10项技能

```sql
SELECT s.name AS 技能名称, s.category AS 技能类别,
       COUNT(ps.position_id) AS 需求职位数,
       SUM(CASE WHEN ps.is_required = TRUE THEN 1 ELSE 0 END) AS 必须技能次数,
       GROUP_CONCAT(DISTINCT p.title SEPARATOR ', ') AS 相关职位
FROM skills s
JOIN position_skills ps ON s.id = ps.skill_id
JOIN positions p ON ps.position_id = p.id
WHERE p.status = 'open'
GROUP BY s.id, s.name, s.category
ORDER BY 需求职位数 DESC, 必须技能次数 DESC
LIMIT 10;
```

### 6.4 部门人才储备分析
**问题**: 分析各部门当前在招聘流程中的候选人储备情况

```sql
SELECT d.name AS 部门名称,
       COUNT(DISTINCT CASE WHEN a.status = 'pending' THEN c.id END) AS 待筛选,
       COUNT(DISTINCT CASE WHEN a.status = 'reviewing' THEN c.id END) AS 筛选中,
       COUNT(DISTINCT CASE WHEN a.status = 'interviewing' THEN c.id END) AS 面试中,
       COUNT(DISTINCT CASE WHEN a.status IN ('offer_pending', 'offered') THEN c.id END) AS 待入职,
       COUNT(DISTINCT c.id) AS 总储备
FROM departments d
JOIN positions p ON d.id = p.department_id
JOIN applications a ON p.id = a.position_id
JOIN candidates c ON a.candidate_id = c.id
WHERE p.status = 'open'
GROUP BY d.id, d.name
ORDER BY 总储备 DESC;
```

---

## 7. 复杂业务场景查询

### 7.1 面试冲突检测
**问题**: 检测某一天是否有面试官的面试时间安排冲突（同一面试官同一时间段有多场面试）

```sql
SELECT e.name AS 面试官姓名,
       DATE(i1.scheduled_at) AS 日期,
       i1.scheduled_at AS 面试1开始时间,
       DATE_ADD(i1.scheduled_at, INTERVAL i1.duration MINUTE) AS 面试1结束时间,
       i2.scheduled_at AS 面试2开始时间,
       DATE_ADD(i2.scheduled_at, INTERVAL i2.duration MINUTE) AS 面试2结束时间
FROM interviews i1
JOIN interview_panelists ip1 ON i1.id = ip1.interview_id
JOIN interviews i2 ON i2.id > i1.id
JOIN interview_panelists ip2 ON i2.id = ip2.interview_id
JOIN employees e ON ip1.interviewer_id = e.id
WHERE ip1.interviewer_id = ip2.interviewer_id
  AND i1.status = 'scheduled' AND i2.status = 'scheduled'
  AND DATE(i1.scheduled_at) = DATE(i2.scheduled_at)
  AND i1.scheduled_at < DATE_ADD(i2.scheduled_at, INTERVAL i2.duration MINUTE)
  AND i2.scheduled_at < DATE_ADD(i1.scheduled_at, INTERVAL i1.duration MINUTE);
```

### 7.2 推荐入职候选人
**问题**: 基于面试评分，找出各职位应该优先发 Offer 的候选人（所有面试官都给出 hire 或 strong_hire 的建议）

```sql
SELECT c.name AS 候选人姓名, p.title AS 应聘职位,
       COUNT(DISTINCT i.id) AS 完成面试轮数,
       ROUND(AVG(f.overall_score), 2) AS 平均评分,
       GROUP_CONCAT(DISTINCT f.recommendation SEPARATOR ', ') AS 录用建议
FROM candidates c
JOIN applications a ON c.id = a.candidate_id
JOIN positions p ON a.position_id = p.id
JOIN interviews i ON a.id = i.application_id
JOIN interview_feedback f ON i.id = f.interview_id
WHERE a.status = 'interviewing'
  AND i.status = 'completed'
GROUP BY c.id, c.name, p.id, p.title
HAVING SUM(CASE WHEN f.recommendation IN ('hire', 'strong_hire') THEN 0 ELSE 1 END) = 0
   AND COUNT(DISTINCT f.id) >= 2
ORDER BY 平均评分 DESC;
```

### 7.3 高端人才追踪
**问题**: 找出期望薪资在50000以上、工作经验10年以上、且来自知名公司的候选人

```sql
SELECT c.name AS 候选人姓名, c.current_company AS 当前公司,
       c.current_position AS 当前职位, c.years_of_experience AS 工作年限,
       c.education_level AS 学历, c.university AS 毕业院校,
       c.expected_salary AS 期望薪资, c.status AS 状态,
       rc.name AS 来源渠道
FROM candidates c
LEFT JOIN recruitment_channels rc ON c.source_channel_id = rc.id
WHERE c.expected_salary >= 50000
  AND c.years_of_experience >= 10
  AND c.current_company IN ('阿里巴巴', '腾讯', '百度', '字节跳动', '美团', '京东', '华为', '蚂蚁集团', '小米', '网易')
ORDER BY c.expected_salary DESC;
```

### 7.4 候选人重复申请检测
**问题**: 找出在多个职位都有申请记录的候选人

```sql
SELECT c.name AS 候选人姓名, c.email AS 邮箱,
       COUNT(DISTINCT a.position_id) AS 申请职位数,
       GROUP_CONCAT(DISTINCT p.title SEPARATOR '; ') AS 申请职位列表,
       GROUP_CONCAT(DISTINCT a.status SEPARATOR '; ') AS 申请状态
FROM candidates c
JOIN applications a ON c.id = a.candidate_id
JOIN positions p ON a.position_id = p.id
GROUP BY c.id, c.name, c.email
HAVING COUNT(DISTINCT a.position_id) > 1
ORDER BY 申请职位数 DESC;
```

---

## 8. 数据质量检查查询

### 8.1 信息不完整的候选人
**问题**: 找出缺少关键信息（邮箱、电话、简历）的候选人

```sql
SELECT name AS 候选人姓名,
       CASE WHEN email IS NULL OR email = '' THEN '缺失' ELSE '有' END AS 邮箱,
       CASE WHEN phone IS NULL OR phone = '' THEN '缺失' ELSE '有' END AS 电话,
       CASE WHEN resume_url IS NULL OR resume_url = '' THEN '缺失' ELSE '有' END AS 简历,
       status AS 状态
FROM candidates
WHERE email IS NULL OR email = ''
   OR phone IS NULL OR phone = ''
   OR resume_url IS NULL OR resume_url = ''
ORDER BY name;
```

### 8.2 审批待处理事项
**问题**: 列出所有待审批的事项，包括职位开放审批、Offer审批和薪资例外审批

```sql
SELECT ha.type AS 审批类型,
       CASE ha.type
           WHEN 'position_opening' THEN (SELECT title FROM positions WHERE id = ha.reference_id)
           WHEN 'offer' THEN (SELECT c.name FROM offers o JOIN applications a ON o.application_id = a.id JOIN candidates c ON a.candidate_id = c.id WHERE o.id = ha.reference_id)
           WHEN 'salary_exception' THEN (SELECT c.name FROM offers o JOIN applications a ON o.application_id = a.id JOIN candidates c ON a.candidate_id = c.id WHERE o.id = ha.reference_id)
           ELSE '其他'
       END AS 相关信息,
       requester.name AS 申请人,
       approver.name AS 审批人,
       ha.requested_at AS 申请时间,
       DATEDIFF(CURDATE(), ha.requested_at) AS 等待天数
FROM hiring_approvals ha
JOIN employees requester ON ha.requester_id = requester.id
JOIN employees approver ON ha.approver_id = approver.id
WHERE ha.status = 'pending'
ORDER BY ha.requested_at;
```

---

## 9. 特定业务场景

### 9.1 校招候选人分析
**问题**: 分析校园招聘渠道的候选人情况，按毕业院校统计

```sql
SELECT c.university AS 毕业院校,
       COUNT(*) AS 候选人数,
       AVG(c.expected_salary) AS 平均期望薪资,
       SUM(CASE WHEN c.status = 'hired' THEN 1 ELSE 0 END) AS 已入职,
       SUM(CASE WHEN c.status = 'interviewing' THEN 1 ELSE 0 END) AS 面试中
FROM candidates c
JOIN recruitment_channels rc ON c.source_channel_id = rc.id
WHERE rc.type = 'campus'
  AND c.graduation_year >= YEAR(CURDATE()) - 1
GROUP BY c.university
ORDER BY 候选人数 DESC;
```

### 9.2 远程职位申请情况
**问题**: 统计支持远程办公的职位的申请情况

```sql
SELECT p.title AS 职位名称, p.remote_policy AS 远程政策,
       p.location AS 工作地点,
       COUNT(a.id) AS 申请人数,
       SUM(CASE WHEN a.status = 'interviewing' THEN 1 ELSE 0 END) AS 面试中,
       p.salary_min AS 最低薪资, p.salary_max AS 最高薪资
FROM positions p
LEFT JOIN applications a ON p.id = a.position_id
WHERE p.status = 'open'
  AND p.remote_policy IN ('remote', 'hybrid')
GROUP BY p.id, p.title, p.remote_policy, p.location, p.salary_min, p.salary_max
ORDER BY 申请人数 DESC;
```

### 9.3 面试问题使用频率
**问题**: 统计面试问题库中各问题的使用频率和平均得分

```sql
SELECT iq.question AS 面试问题,
       iq.category AS 问题类别, iq.difficulty AS 难度,
       COUNT(iqr.id) AS 使用次数,
       ROUND(AVG(iqr.score), 2) AS 平均得分
FROM interview_questions iq
LEFT JOIN interview_question_records iqr ON iq.id = iqr.question_id
WHERE iq.is_active = TRUE
GROUP BY iq.id, iq.question, iq.category, iq.difficulty
ORDER BY 使用次数 DESC
LIMIT 20;
```

### 9.4 部门招聘完成率
**问题**: 计算各部门的招聘完成率（已入职/总需求）

```sql
SELECT d.name AS 部门名称,
       SUM(p.headcount) AS 总需求人数,
       SUM(p.filled_count) AS 已入职人数,
       ROUND(SUM(p.filled_count) * 100.0 / NULLIF(SUM(p.headcount), 0), 2) AS 完成率,
       SUM(p.headcount - p.filled_count) AS 缺口人数
FROM departments d
JOIN positions p ON d.id = p.department_id
WHERE p.status IN ('open', 'filled')
GROUP BY d.id, d.name
ORDER BY 完成率 DESC;
```

---

## 10. 综合报表查询

### 10.1 招聘仪表板数据
**问题**: 生成招聘仪表板所需的关键指标数据

```sql
SELECT
    (SELECT COUNT(*) FROM positions WHERE status = 'open') AS 开放职位数,
    (SELECT SUM(headcount - filled_count) FROM positions WHERE status = 'open') AS 总缺口人数,
    (SELECT COUNT(*) FROM candidates WHERE status = 'interviewing') AS 面试中候选人,
    (SELECT COUNT(*) FROM interviews WHERE status = 'scheduled' AND scheduled_at >= CURDATE()) AS 待进行面试,
    (SELECT COUNT(*) FROM offers WHERE status = 'sent') AS 待回复Offer,
    (SELECT COUNT(*) FROM applications WHERE status = 'pending') AS 待筛选简历,
    (SELECT COUNT(*) FROM hiring_approvals WHERE status = 'pending') AS 待审批事项;
```

### 10.2 招聘经理工作台
**问题**: 为招聘经理生成其负责职位的招聘进度汇总

```sql
SELECT p.title AS 职位名称, p.priority AS 优先级,
       p.headcount AS 需求人数, p.filled_count AS 已入职,
       COUNT(DISTINCT a.id) AS 申请人数,
       SUM(CASE WHEN a.status = 'interviewing' THEN 1 ELSE 0 END) AS 面试中,
       SUM(CASE WHEN a.status IN ('offered', 'offer_pending') THEN 1 ELSE 0 END) AS 待入职,
       DATEDIFF(CURDATE(), p.posted_at) AS 开放天数,
       hm.name AS 招聘经理
FROM positions p
JOIN employees hm ON p.hiring_manager_id = hm.id
LEFT JOIN applications a ON p.id = a.position_id
WHERE p.status = 'open'
GROUP BY p.id, p.title, p.priority, p.headcount, p.filled_count, p.posted_at, hm.name
ORDER BY p.priority DESC, 开放天数 DESC;
```
