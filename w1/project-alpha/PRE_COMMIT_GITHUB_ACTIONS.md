# Pre-commit 和 GitHub Actions 配置完成

## ✅ 已完成的配置

### 1. Pre-commit 配置

**文件**: `.pre-commit-config.yaml`

**配置的工具**:

- ✅ **通用检查**: 尾随空格、文件结尾、YAML/JSON/TOML 验证、大文件检查等
- ✅ **Python**: black (格式化), isort (导入排序), flake8 (代码检查)
- ✅ **TypeScript/JavaScript**: prettier (格式化), eslint (代码检查)
- ✅ **Docker**: hadolint (Dockerfile 检查)
- ✅ **YAML**: yamllint
- ✅ **Markdown**: markdownlint

### 2. GitHub Actions Workflows

#### CI Workflow (`.github/workflows/ci.yml`)

- ✅ Pre-commit 检查
- ✅ 后端测试（PostgreSQL 服务、迁移、linting）
- ✅ 前端测试（linting、类型检查、构建）
- ✅ Docker 镜像构建验证

#### Pre-commit Workflow (`.github/workflows/pre-commit.yml`)

- ✅ 在 PR 和 push 时自动运行 pre-commit 检查

#### Docker Build Workflow (`.github/workflows/docker-build.yml`)

- ✅ 构建并验证 Docker 镜像

### 3. 配置文件

#### Python 配置 (`backend/pyproject.toml`)

- ✅ Black 配置（行长度 100）
- ✅ isort 配置（兼容 black）
- ✅ Flake8 配置
- ✅ MyPy 配置（可选）

#### TypeScript 配置

- ✅ `frontend/.eslintrc.cjs` - ESLint 配置
- ✅ `frontend/.prettierrc.json` - Prettier 配置
- ✅ `frontend/.prettierignore` - Prettier 忽略文件

### 4. 工具脚本

- ✅ `setup-pre-commit.sh` - 一键设置脚本
- ✅ `Makefile` - 添加了 `install-pre-commit`, `format`, `format-check` 命令

## 🚀 快速开始

### 安装 Pre-commit

```bash
# 方法 1: 使用脚本（推荐）
./setup-pre-commit.sh

# 方法 2: 使用 Makefile
make install-pre-commit

# 方法 3: 手动安装
pip install pre-commit  # 或 uv pip install pre-commit
pre-commit install
cd frontend && npm install  # 安装前端依赖
```

### 运行 Pre-commit

```bash
# 检查所有文件
pre-commit run --all-files

# 只检查暂存的文件（提交时自动运行）
pre-commit run

# 格式化代码
make format

# 检查代码格式
make format-check
```

## 📋 Pre-commit Hooks 说明

### Python Hooks

| Hook | 说明 | 自动修复 |
|------|------|---------|
| black | 代码格式化 | ✅ |
| isort | 导入排序 | ✅ |
| flake8 | 代码检查 | ❌ |

### TypeScript/JavaScript Hooks

| Hook | 说明 | 自动修复 |
|------|------|---------|
| prettier | 代码格式化 | ✅ |
| eslint | 代码检查 | ❌ |

### 其他 Hooks

| Hook | 说明 | 自动修复 |
|------|------|---------|
| trailing-whitespace | 删除尾随空格 | ✅ |
| end-of-file-fixer | 文件结尾换行 | ✅ |
| check-yaml | YAML 语法检查 | ❌ |
| check-json | JSON 语法检查 | ❌ |
| check-toml | TOML 语法检查 | ❌ |
| hadolint | Dockerfile 检查 | ❌ |
| yamllint | YAML lint | ❌ |
| markdownlint | Markdown lint | ✅ |

## 🔧 配置说明

### 代码格式标准

- **Python**: 行长度 100，使用 black 风格
- **TypeScript**: 行长度 100，单引号，无分号
- **文件结尾**: LF (Unix 风格)

### 排除的文件

- Markdown 和 SQL 文件不检查尾随空格
- `node_modules`, `dist`, `build` 目录
- 缓存和临时文件

## 📝 使用示例

### 提交代码

```bash
# 1. 添加文件
git add .

# 2. 提交（pre-commit 会自动运行）
git commit -m "feat: add new feature"

# 如果有格式问题，pre-commit 会自动修复
# 修复后需要重新 add 和 commit
git add .
git commit -m "feat: add new feature"
```

### 手动格式化

```bash
# 格式化所有代码
make format

# 只格式化 Python
cd backend && uv run black . && uv run isort .

# 只格式化前端
cd frontend && npm run format
```

## 🐛 故障排查

### Pre-commit 运行失败

1. **查看错误信息**:

   ```bash
   pre-commit run --all-files
   ```

2. **更新 hooks**:

   ```bash
   pre-commit autoupdate
   ```

3. **清除缓存**:

   ```bash
   pre-commit clean
   ```

### GitHub Actions 失败

1. 查看 Actions 日志
2. 在本地运行相同的检查：

   ```bash
   pre-commit run --all-files
   make format-check
   ```

### ESLint 错误

确保安装了前端依赖：

```bash
cd frontend && npm install
```

## 📚 相关文档

- [Pre-commit 官方文档](https://pre-commit.com/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [项目设置指南](./.pre-commit-setup.md)

## ✨ 下一步

1. 运行 `./setup-pre-commit.sh` 安装 hooks
2. 运行 `pre-commit run --all-files` 检查所有文件
3. 提交代码时 hooks 会自动运行
4. GitHub Actions 会在 PR 时自动检查
