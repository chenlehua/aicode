# Git Commit Type 完整指南

## 概述

Git Commit Type 是基于 **Conventional Commits** 规范的提交信息格式，最初源于 Angular 团队的提交规范。这种标准化的提交格式有助于：
- 自动生成 CHANGELOG
- 快速浏览提交历史
- 触发自动化构建和发布流程
- 提高团队协作效率

---

## 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 示例
```
feat(user): add user login functionality

Implement OAuth 2.0 authentication with Google and GitHub providers.
Users can now sign in using their social accounts.

Closes #123
```

---

## 标准 Commit Types

以下是 `@commitlint/config-conventional` 推荐的标准类型：

### 1. **feat** (Feature)
**新功能、新特性**

- 用于添加新的功能或特性
- 会出现在 CHANGELOG 中
- 触发 MINOR 版本号更新（如 1.0.0 → 1.1.0）

**示例：**
```bash
feat: add dark mode support
feat(api): implement GraphQL endpoint
feat(payment): integrate Stripe payment gateway
```

---

### 2. **fix** (Bug Fix)
**修复 Bug**

- 用于修复已知的问题或缺陷
- 会出现在 CHANGELOG 中
- 触发 PATCH 版本号更新（如 1.0.0 → 1.0.1）

**示例：**
```bash
fix: resolve memory leak in data processing
fix(auth): correct token expiration logic
fix(ui): fix button alignment on mobile devices
```

---

### 3. **docs** (Documentation)
**文档变更**

- 仅修改文档，不涉及代码逻辑
- 包括 README、注释、API 文档等
- 不会触发版本号更新

**示例：**
```bash
docs: update installation instructions
docs(api): add examples for REST endpoints
docs: fix typos in contributing guide
```

---

### 4. **style** (Code Style)
**代码格式调整**

- 不影响代码运行的格式修改
- 包括空格、缩进、分号、格式化等
- 不会触发版本号更新

**示例：**
```bash
style: format code with Prettier
style(css): adjust indentation
style: remove trailing whitespace
```

---

### 5. **refactor** (Code Refactoring)
**代码重构**

- 既不是新增功能，也不是修复 Bug
- 改进代码结构、可读性或性能
- 不改变外部行为

**示例：**
```bash
refactor: simplify user validation logic
refactor(database): optimize query performance
refactor: extract utility functions to separate module
```

---

### 6. **perf** (Performance Improvements)
**性能优化**

- 提升性能的代码变更
- 包括算法优化、减少资源消耗等
- 可能会出现在 CHANGELOG 中

**示例：**
```bash
perf: improve image loading speed
perf(cache): implement Redis caching layer
perf: reduce bundle size by 30%
```

---

### 7. **test** (Tests)
**测试相关**

- 添加、修改或删除测试代码
- 包括单元测试、集成测试、E2E 测试
- 不会触发版本号更新

**示例：**
```bash
test: add unit tests for authentication module
test(e2e): update login flow tests
test: increase code coverage to 85%
```

---

### 8. **build** (Build System)
**构建系统或外部依赖变更**

- 影响构建系统或外部依赖的变更
- 包括 webpack、npm、gulp、package.json 等
- 不会直接触发版本号更新

**示例：**
```bash
build: upgrade webpack to v5
build(deps): update lodash to 4.17.21
build: add bundle analyzer plugin
```

---

### 9. **ci** (Continuous Integration)
**CI/CD 配置变更**

- 修改持续集成配置文件和脚本
- 包括 GitHub Actions、Travis CI、Jenkins 等
- 不会触发版本号更新

**示例：**
```bash
ci: add automated deployment workflow
ci(github): update Node.js version in Actions
ci: configure code coverage reporting
```

---

### 10. **chore** (Chores)
**其他杂项变更**

- 不属于以上任何类型的维护性任务
- 包括更新依赖、配置文件、工具等
- 不修改 src 或 test 文件
- 不会触发版本号更新

**示例：**
```bash
chore: update .gitignore
chore(deps): bump express from 4.17.1 to 4.18.0
chore: clean up unused dependencies
```

---

### 11. **revert** (Revert)
**回滚提交**

- 撤销之前的某个提交
- 应包含被回滚的提交的哈希值

**示例：**
```bash
revert: revert "feat: add new payment method"

This reverts commit a1b2c3d4e5f6.
```

---

## 扩展 Types（可选）

除了标准类型，团队可以根据需要添加自定义类型：

### **security** (Security)
**安全相关**
```bash
security: patch XSS vulnerability
security(auth): implement rate limiting
```

### **deps** (Dependencies)
**依赖更新**（也可用 build 或 chore）
```bash
deps: update all minor dependencies
deps(security): upgrade vulnerable packages
```

### **i18n** (Internationalization)
**国际化**
```bash
i18n: add Chinese translation
i18n: update locale files
```

### **a11y** (Accessibility)
**可访问性**
```bash
a11y: improve keyboard navigation
a11y: add ARIA labels to buttons
```

### **config** (Configuration)
**配置文件**
```bash
config: update ESLint rules
config: add environment variables
```

---

## Scope（范围）

Scope 是可选的，用于指定提交影响的范围：

```bash
feat(auth): add OAuth login
fix(database): resolve connection pooling issue
docs(api): update endpoint documentation
```

**常见 Scope 示例：**
- `auth` - 认证模块
- `api` - API 接口
- `ui` - 用户界面
- `database` / `db` - 数据库
- `config` - 配置
- `core` - 核心功能
- `user` - 用户相关
- `payment` - 支付模块

---

## Breaking Changes（破坏性变更）

破坏性变更会触发 MAJOR 版本号更新（如 1.0.0 → 2.0.0）

### 标记方式 1：在 type 后添加 `!`
```bash
feat!: change API response format

BREAKING CHANGE: The API now returns data in a different structure.
Old: { user: {...} }
New: { data: { user: {...} } }
```

### 标记方式 2：在 footer 中添加 `BREAKING CHANGE:`
```bash
refactor(api): restructure user endpoints

BREAKING CHANGE: 
- Renamed /users to /accounts
- Changed response format from array to object
```

---

## 提交信息最佳实践

### ✅ 好的提交信息

```bash
feat(auth): implement two-factor authentication

Add SMS and email-based 2FA options for enhanced security.
Users can enable 2FA in their account settings.

Closes #456
```

**特点：**
- 类型明确
- 简洁的主题（50 字符内）
- 详细的描述（如有必要）
- 关联 issue 编号

---

### ❌ 不好的提交信息

```bash
update stuff
fix bug
changes
WIP
```

**问题：**
- 没有类型标识
- 信息模糊
- 无法理解变更内容

---

## 完整示例

### 示例 1：新功能
```bash
feat(search): add fuzzy search with autocomplete

Implement fuzzy search algorithm using Fuse.js library.
Added autocomplete suggestions with debouncing for better UX.

- Search delay: 300ms
- Max suggestions: 10
- Highlights matching characters

Closes #789
```

### 示例 2：Bug 修复
```bash
fix(cart): prevent duplicate items in shopping cart

Fixed race condition that allowed users to add the same item
multiple times by clicking rapidly.

Added mutex lock and debouncing to add-to-cart button.

Fixes #234
```

### 示例 3：破坏性变更
```bash
feat(api)!: migrate to RESTful API v2

BREAKING CHANGE: API endpoints have been restructured.

Migration guide:
- GET /user/:id → GET /api/v2/users/:id
- POST /login → POST /api/v2/auth/login
- All responses now wrapped in { data, meta } structure

See docs/migration-v2.md for full details.
```

### 示例 4：性能优化
```bash
perf(images): implement lazy loading and WebP format

Reduced initial page load by 40% through:
- Lazy loading images below the fold
- Converting images to WebP with fallback
- Implementing progressive image loading

Metrics:
- First Contentful Paint: 1.2s → 0.7s
- Largest Contentful Paint: 2.8s → 1.6s
```

---

## 常见问题 FAQ

### Q1: 一个提交包含多种类型的改动怎么办？
**A:** 应该拆分成多个提交，每个提交只包含一种类型的改动。

```bash
# 不推荐
feat: add feature and fix bugs

# 推荐
feat: add user profile page
fix: resolve login redirect issue
```

---

### Q2: `chore` 和 `build` 有什么区别？
**A:** 
- `build`: 影响构建系统或依赖（webpack、npm、gulp）
- `chore`: 其他维护性任务（更新 .gitignore、清理代码）

---

### Q3: 什么时候用 `refactor` vs `perf`？
**A:**
- `refactor`: 改进代码结构，不影响性能
- `perf`: 专门为了提升性能的优化

---

### Q4: 是否必须使用 Scope？
**A:** 不是必须的，但在大型项目中强烈推荐使用以提高可读性。

---

## 版本号规则（Semantic Versioning）

根据提交类型自动更新版本号：

| 提交类型 | 版本变化 | 示例 |
|---------|---------|------|
| `fix` | PATCH | 1.0.0 → 1.0.1 |
| `feat` | MINOR | 1.0.0 → 1.1.0 |
| `BREAKING CHANGE` | MAJOR | 1.0.0 → 2.0.0 |
| 其他类型 | 不触发 | - |

---

## 工具推荐

### 1. **Commitlint**
验证提交信息格式

```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional']
};
```

### 2. **Commitizen**
交互式生成提交信息

```bash
npm install -g commitizen
npm install --save-dev cz-conventional-changelog

# 使用
git cz
```

### 3. **Husky**
Git hooks 自动化

```bash
npm install --save-dev husky

# package.json
{
  "husky": {
    "hooks": {
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  }
}
```

### 4. **Standard Version**
自动生成 CHANGELOG 和版本号

```bash
npm install --save-dev standard-version

# 使用
npm run release
```

---

## 配置示例

### `.commitlintrc.json`
```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert"
      ]
    ],
    "subject-case": [2, "never", ["upper-case"]],
    "subject-max-length": [2, "always", 100]
  }
}
```

---

## 团队规范模板

```markdown
# 项目提交规范

## 必须遵守
1. 所有提交必须包含类型标识
2. 主题不超过 50 个字符
3. 使用现在时态（"add" 而非 "added"）
4. 不要在主题末尾加句号

## 推荐
1. 添加 Scope 标识影响范围
2. 重大变更添加详细说明
3. 关联相关 issue 编号
4. 提供详细的 body 说明（如有必要）

## 类型使用指南
- 新功能 → feat
- Bug 修复 → fix
- 文档 → docs
- 格式 → style
- 重构 → refactor
- 性能 → perf
- 测试 → test
- 构建 → build
- CI/CD → ci
- 其他 → chore
```

---

## 总结

良好的提交信息规范能够：
✅ 提高代码审查效率  
✅ 自动化版本管理和发布  
✅ 生成清晰的更新日志  
✅ 方便追踪问题和回滚  
✅ 提升团队协作质量  

记住：**清晰的提交历史是项目可维护性的关键！**
