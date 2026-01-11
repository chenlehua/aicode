# Ticket Tag Management Tool

A simple ticket management tool with tag support, built with PostgreSQL, FastAPI, and React.

## Project Structure

```
project-alpha/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
└── docker-compose.yml # Docker configuration
```

## Project Phases

### Phase 1: Project Initialization ✅

- Docker environment setup with PostgreSQL
- Backend project initialization (FastAPI)
- Frontend project initialization (Vite + React + TypeScript + Tailwind CSS)

### Phase 2: Database Design and Migration ✅

- Alembic configuration
- SQLAlchemy models (Tag, Ticket, TicketTag)
- Database migration with triggers and indexes

### Phase 3: Backend API Development ✅

- Pydantic schemas
- Service layer
- Router layer with error handling
- Complete RESTful API endpoints

### Phase 4: Frontend Foundation ✅

- TypeScript type definitions
- API clients with Axios
- React Query hooks
- Routing configuration

### Phase 5: Frontend Core Features ✅

- UI components (Layout, Filters, Tags, Tickets, Dialogs)
- Page integration
- Toast notifications
- Form validation

### Phase 6: Integration Testing and Optimization ✅

- Integration test documentation
- Performance optimization (caching, skeleton screens)
- Mobile responsive design
- Keyboard navigation support

## Getting Started

### Prerequisites

- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Python 3.11+ (uv will manage Python versions)
- Node.js 18+

#### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Install dependencies and create virtual environment (uv will handle this automatically):

```bash
uv sync
```

3. Start the backend server:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Or use the convenience script:

```bash
# From project root
./start-backend.sh
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Database Setup

1. Start PostgreSQL container:

```bash
docker-compose up -d
```

2. Verify database is running:

```bash
docker-compose ps
```

## Phase 1 Verification

### 1. Verify Docker PostgreSQL Container

```bash
# Start database
docker-compose up -d

# Check container status
docker-compose ps

# Verify database connection (optional)
docker-compose exec db psql -U ticketapp -d ticketapp -c "SELECT version();"
```

Expected: Container should be running and healthy.

### 2. Verify Backend FastAPI Server

```bash
cd backend

# Install dependencies and sync virtual environment
uv sync

# Start server
uv run uvicorn app.main:app --reload --port 8000
```

Or use the convenience script from project root:

```bash
./start-backend.sh
```

Expected:

- Server starts without errors
- API available at `http://localhost:8000`
- API docs available at `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health` returns `{"status": "healthy"}`

### 3. Verify Frontend Vite Server

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Expected:

- Server starts without errors
- Frontend available at `http://localhost:5173`
- Page displays "Ticket Tag Management" title

## Docker 部署

### 快速开始

使用 Makefile（推荐）：

```bash
# 启动所有服务
make up

# 查看服务状态
make ps

# 查看日志
make logs

# 停止服务
make down
```

使用 Docker Compose：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 服务地址

启动后访问：

- **前端**: <http://localhost>
- **后端 API**: <http://localhost:8000>
- **API 文档**: <http://localhost:8000/docs>

### 数据库操作

```bash
# 运行迁移
make migrate

# 加载测试数据
make seed

# 访问数据库
make shell-db
```

### 更多部署信息

详细部署文档请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 开发模式

### 本地开发（不使用 Docker）

```bash
# 1. 启动数据库
make dev-up
# 或
docker-compose up -d db

# 2. 启动后端（新终端）
cd backend
./start-backend.sh

# 3. 启动前端（新终端）
cd frontend
npm run dev
```

## Code Quality & CI/CD

### Pre-commit Hooks

项目配置了 pre-commit hooks 用于代码质量检查：

```bash
# 安装 pre-commit
pip install pre-commit
# 或
uv pip install pre-commit

# 安装 Git hooks
make install-pre-commit
# 或
pre-commit install

# 手动运行检查
pre-commit run --all-files

# 格式化代码
make format
```

**配置的工具**:

- Python: black, isort, flake8
- TypeScript/JavaScript: prettier, eslint
- 其他: yamllint, markdownlint, hadolint

详细配置请参考 [.pre-commit-setup.md](./.pre-commit-setup.md)

### GitHub Actions

项目配置了 GitHub Actions 用于持续集成：

- **CI Workflow**: 运行 pre-commit、后端测试、前端测试、Docker 构建
- **Pre-commit Workflow**: 在 PR 和 push 时自动运行 pre-commit 检查

工作流文件位于 `.github/workflows/`

## Next Steps

- Phase 2: Database Design & Migration ✅
- Phase 3: Backend API Development ✅
- Phase 4: Frontend Foundation ✅
- Phase 5: Frontend Core Features ✅
- Phase 6: Integration Testing & Optimization ✅
