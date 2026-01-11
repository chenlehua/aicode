# Docker 部署指南

本文档介绍如何使用 Docker Compose 部署 Ticket Tag Management 应用。

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Make (可选，用于便捷命令)

## 快速开始

### 1. 使用 Makefile（推荐）

```bash
# 构建并启动所有服务
make up

# 查看服务状态
make ps

# 查看日志
make logs

# 停止所有服务
make down
```

### 2. 使用 Docker Compose

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 服务说明

启动后，以下服务将可用：

- **前端**: <http://localhost>
- **后端 API**: <http://localhost:8000>
- **API 文档**: <http://localhost:8000/docs>
- **数据库**: localhost:5432

## Makefile 命令

### 基本命令

```bash
make help          # 显示所有可用命令
make build         # 构建所有 Docker 镜像
make up            # 启动所有服务
make down          # 停止所有服务
make restart       # 重启所有服务
make ps            # 查看运行中的容器
```

### 日志命令

```bash
make logs           # 查看所有服务日志
make logs-backend   # 查看后端日志
make logs-frontend  # 查看前端日志
make logs-db        # 查看数据库日志
```

### 数据库命令

```bash
make migrate        # 运行数据库迁移
make seed           # 加载测试数据
make shell-db       # 打开 PostgreSQL shell
```

### 开发命令

```bash
make shell-backend  # 打开后端容器 shell
make dev-up         # 仅启动数据库（用于本地开发）
make dev-down       # 停止数据库
```

### 清理命令

```bash
make clean          # 停止并删除所有容器、卷和镜像
make rebuild        # 清理、重建并重启所有服务
```

## 数据库操作

### 运行迁移

```bash
make migrate
# 或
docker-compose exec backend uv run alembic upgrade head
```

### 加载测试数据

```bash
make seed
# 或
docker-compose exec -T db psql -U ticketapp -d ticketapp < backend/docs/seed.sql
```

### 访问数据库

```bash
make shell-db
# 或
docker-compose exec db psql -U ticketapp -d ticketapp
```

## 环境变量配置

### 后端环境变量

在 `docker-compose.yml` 中配置：

```yaml
backend:
  environment:
    DATABASE_URL: postgresql://ticketapp:ticketapp@db:5432/ticketapp
    DEBUG: "False"
    API_V1_PREFIX: /api/v1
```

### 前端环境变量

在构建时通过 `build.args` 配置：

```yaml
frontend:
  build:
    args:
      VITE_API_URL: http://localhost:8000/api/v1
```

## 生产环境部署

### 1. 修改环境变量

创建 `.env` 文件或修改 `docker-compose.yml` 中的环境变量：

```bash
# 后端
DATABASE_URL=postgresql://user:password@db:5432/ticketapp
DEBUG=False

# 前端构建参数
VITE_API_URL=https://api.yourdomain.com/api/v1
```

### 2. 构建生产镜像

```bash
docker-compose -f docker-compose.yml build
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 配置反向代理（可选）

如果需要使用域名访问，可以配置 Nginx 反向代理：

```nginx
# /etc/nginx/sites-available/ticketapp
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 开发模式

使用开发模式可以启用热重载：

```bash
# 使用开发配置
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 或使用 Makefile
make dev-up  # 仅启动数据库，前端和后端在本地运行
```

## 故障排查

### 查看服务状态

```bash
make ps
# 或
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
docker-compose restart
```

### 重建服务

```bash
# 重建特定服务
docker-compose build backend
docker-compose up -d backend

# 重建所有服务
make rebuild
```

### 清理数据

```bash
# 停止并删除所有容器和卷
make clean

# 仅删除数据卷（保留镜像）
docker-compose down -v
```

## 健康检查

### 检查服务健康状态

```bash
# 检查容器状态
docker-compose ps

# 检查后端健康
curl http://localhost:8000/health

# 检查前端
curl http://localhost

# 检查数据库连接
docker-compose exec db pg_isready -U ticketapp
```

## 性能优化

### 1. 数据库连接池

后端已配置 SQLAlchemy 连接池，默认配置适合大多数场景。

### 2. Nginx 缓存

前端 Nginx 配置已启用静态资源缓存和 gzip 压缩。

### 3. 资源限制

可以在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## 安全建议

1. **更改默认密码**: 修改数据库密码
2. **使用环境变量**: 敏感信息使用环境变量，不要硬编码
3. **启用 HTTPS**: 生产环境使用 HTTPS
4. **限制网络访问**: 使用防火墙限制数据库端口访问
5. **定期更新镜像**: 保持 Docker 镜像和依赖包更新

## 备份和恢复

### 备份数据库

```bash
docker-compose exec db pg_dump -U ticketapp ticketapp > backup.sql
```

### 恢复数据库

```bash
docker-compose exec -T db psql -U ticketapp -d ticketapp < backup.sql
```

## 常见问题

### Q: 端口已被占用

A: 修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:8000"  # 后端使用 8080
  - "3000:80"    # 前端使用 3000
```

### Q: 前端无法连接后端

A: 检查 `VITE_API_URL` 配置是否正确，确保前端可以访问后端地址。

### Q: 数据库迁移失败

A: 确保数据库服务已启动并健康：

```bash
make logs-db
make migrate
```

### Q: 容器启动失败

A: 查看详细日志：

```bash
docker-compose logs backend
docker-compose logs frontend
```

## 更多信息

- [Docker 文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [项目 README](./README.md)
