# Docker 部署方案总结

## 📦 新增文件

### Docker 配置文件

1. **`backend/Dockerfile`** - 后端 Docker 镜像构建文件
   - 基于 Python 3.11-slim
   - 使用 uv 管理依赖
   - 自动运行数据库迁移
   - 启动 FastAPI 服务器

2. **`frontend/Dockerfile`** - 前端生产环境 Docker 镜像
   - 多阶段构建（构建 + Nginx）
   - 使用 Node.js 18 构建
   - 使用 Nginx Alpine 提供服务
   - 支持环境变量配置

3. **`frontend/Dockerfile.dev`** - 前端开发环境 Docker 镜像
   - 支持热重载
   - 用于开发模式

4. **`frontend/nginx.conf`** - Nginx 配置文件
   - SPA 路由支持
   - Gzip 压缩
   - 静态资源缓存
   - 安全头设置

5. **`docker-compose.yml`** - Docker Compose 主配置文件
   - 数据库服务（PostgreSQL）
   - 后端服务（FastAPI）
   - 前端服务（Nginx）
   - 网络配置
   - 健康检查

6. **`docker-compose.dev.yml`** - 开发环境覆盖配置
   - 开发模式配置
   - 热重载支持

### 忽略文件

7. **`backend/.dockerignore`** - 后端构建忽略文件
8. **`frontend/.dockerignore`** - 前端构建忽略文件

### 工具文件

9. **`Makefile`** - 便捷操作命令
   - 构建、启动、停止服务
   - 日志查看
   - 数据库操作
   - 清理命令

### 文档

10. **`DEPLOYMENT.md`** - 详细部署文档
11. **`DOCKER_SETUP.md`** - 本文档

## 🚀 快速开始

### 1. 使用 Makefile（推荐）

```bash
# 查看所有命令
make help

# 构建并启动所有服务
make up

# 查看服务状态
make ps

# 查看日志
make logs

# 运行数据库迁移
make migrate

# 加载测试数据
make seed

# 停止服务
make down
```

### 2. 使用 Docker Compose

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📋 Makefile 命令详解

### 基本操作

| 命令 | 说明 |
|------|------|
| `make help` | 显示帮助信息 |
| `make build` | 构建所有 Docker 镜像 |
| `make up` | 启动所有服务（后台运行） |
| `make down` | 停止所有服务 |
| `make restart` | 重启所有服务 |
| `make ps` | 查看运行中的容器 |

### 日志查看

| 命令 | 说明 |
|------|------|
| `make logs` | 查看所有服务日志 |
| `make logs-backend` | 查看后端日志 |
| `make logs-frontend` | 查看前端日志 |
| `make logs-db` | 查看数据库日志 |

### 数据库操作

| 命令 | 说明 |
|------|------|
| `make migrate` | 运行数据库迁移 |
| `make seed` | 加载测试数据 |
| `make shell-db` | 打开 PostgreSQL shell |

### 开发工具

| 命令 | 说明 |
|------|------|
| `make shell-backend` | 打开后端容器 shell |
| `make dev-up` | 仅启动数据库（用于本地开发） |
| `make dev-down` | 停止数据库 |

### 清理操作

| 命令 | 说明 |
|------|------|
| `make clean` | 停止并删除所有容器、卷和镜像 |
| `make rebuild` | 清理、重建并重启所有服务 |

## 🌐 服务地址

启动后，以下服务可用：

- **前端**: <http://localhost>
- **后端 API**: <http://localhost:8000>
- **API 文档**: <http://localhost:8000/docs>
- **数据库**: localhost:5432

## 🔧 配置说明

### 环境变量

#### 后端环境变量（docker-compose.yml）

```yaml
backend:
  environment:
    DATABASE_URL: postgresql://ticketapp:ticketapp@db:5432/ticketapp
    DEBUG: "False"
    API_V1_PREFIX: /api/v1
```

#### 前端环境变量（构建时）

```yaml
frontend:
  build:
    args:
      VITE_API_URL: http://localhost:8000/api/v1
```

### 端口配置

默认端口：

- 前端: 80
- 后端: 8000
- 数据库: 5432

如需修改，编辑 `docker-compose.yml` 中的 `ports` 配置。

## 🏗️ 架构说明

### 服务架构

```
┌─────────────┐
│   Frontend  │ (Nginx, Port 80)
│   (React)   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   Backend   │ (FastAPI, Port 8000)
│   (Python)  │
└──────┬──────┘
       │ SQL
       ▼
┌─────────────┐
│  Database   │ (PostgreSQL, Port 5432)
│             │
└─────────────┘
```

### 网络配置

所有服务在 `ticketapp-network` 网络中，可以通过服务名互相访问：

- 前端 → 后端: `http://backend:8000`
- 后端 → 数据库: `postgresql://ticketapp:ticketapp@db:5432/ticketapp`

## 📝 开发模式

### 方式 1: 仅数据库使用 Docker

```bash
# 启动数据库
make dev-up

# 后端和前端在本地运行
cd backend && ./start-backend.sh
cd frontend && npm run dev
```

### 方式 2: 使用开发 Docker Compose

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🔍 故障排查

### 查看服务状态

```bash
make ps
docker-compose ps
```

### 查看日志

```bash
# 所有服务
make logs

# 特定服务
make logs-backend
make logs-frontend
make logs-db
```

### 重启服务

```bash
make restart
# 或
docker-compose restart [service_name]
```

### 重建服务

```bash
# 重建特定服务
docker-compose build backend
docker-compose up -d backend

# 重建所有服务
make rebuild
```

## 🧪 测试部署

### 1. 启动服务

```bash
make up
```

### 2. 等待服务就绪

```bash
# 检查服务状态
make ps

# 检查健康状态
curl http://localhost:8000/health
curl http://localhost
```

### 3. 运行迁移

```bash
make migrate
```

### 4. 加载测试数据

```bash
make seed
```

### 5. 访问应用

- 前端: <http://localhost>
- API 文档: <http://localhost:8000/docs>

## 🔒 安全建议

1. **生产环境配置**
   - 修改数据库密码
   - 使用环境变量文件（`.env`）
   - 启用 HTTPS
   - 限制数据库端口访问

2. **资源限制**
   - 在 `docker-compose.yml` 中添加资源限制
   - 监控容器资源使用

3. **备份策略**
   - 定期备份数据库
   - 使用 Docker volumes 持久化数据

## 📚 相关文档

- [DEPLOYMENT.md](./DEPLOYMENT.md) - 详细部署文档
- [README.md](./README.md) - 项目主文档
- [backend/docs/INTEGRATION_TEST.md](./backend/docs/INTEGRATION_TEST.md) - 集成测试文档

## ✅ 验证清单

部署完成后，请验证：

- [ ] 所有服务正常启动
- [ ] 前端可以访问
- [ ] 后端 API 可以访问
- [ ] API 文档可以访问
- [ ] 数据库迁移成功
- [ ] 测试数据加载成功
- [ ] 前端可以调用后端 API
- [ ] 日志正常输出

## 🎉 完成

Docker 部署方案已配置完成，可以使用 `make up` 一键启动所有服务！
