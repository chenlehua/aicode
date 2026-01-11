# 故障排查指南

## 前端不显示数据

### 问题诊断步骤

1. **检查服务状态**

   ```bash
   make ps
   # 或
   docker-compose ps
   ```

   确保所有服务都在运行。

2. **检查后端 API**

   ```bash
   curl http://localhost:8000/api/v1/tickets
   curl http://localhost:8000/api/v1/tags
   ```

   应该返回 JSON 数据。

3. **检查数据库数据**

   ```bash
   make shell-db
   # 在 PostgreSQL shell 中执行：
   SELECT COUNT(*) FROM tickets;
   SELECT COUNT(*) FROM tags;
   ```

4. **检查 CORS 配置**

   ```bash
   curl -I -X OPTIONS -H "Origin: http://localhost" http://localhost:8000/api/v1/tickets
   ```

   应该看到 `access-control-allow-origin: http://localhost`

5. **检查浏览器控制台**
   - 打开浏览器开发者工具（F12）
   - 查看 Console 标签页的错误信息
   - 查看 Network 标签页，检查 API 请求是否成功

6. **检查前端构建**

   ```bash
   # 重新构建前端
   docker-compose build frontend
   docker-compose up -d frontend
   ```

### 常见问题及解决方案

#### 问题 1: CORS 错误

**症状**: 浏览器控制台显示 CORS 错误

**解决方案**:

- 确保后端 CORS 配置包含 `http://localhost`
- 重启后端服务：`docker-compose restart backend`

#### 问题 2: API 请求失败

**症状**: Network 标签页显示 API 请求返回 404 或 500

**解决方案**:

- 检查后端服务是否正常运行：`docker-compose logs backend`
- 检查 API URL 配置是否正确
- 确保数据库迁移已运行：`make migrate`

#### 问题 3: 前端显示空白页

**症状**: 页面加载但没有任何内容

**解决方案**:

- 检查浏览器控制台是否有 JavaScript 错误
- 检查前端构建是否成功：`docker-compose logs frontend`
- 重新构建前端：`docker-compose build frontend && docker-compose up -d frontend`

#### 问题 4: 数据为空

**症状**: 页面显示但列表为空

**解决方案**:

- 检查数据库是否有数据：`make shell-db`
- 如果没有数据，加载测试数据：`make seed`
- 检查 API 是否返回数据：`curl http://localhost:8000/api/v1/tickets`

### 快速修复命令

```bash
# 1. 重启所有服务
make restart

# 2. 运行数据库迁移
make migrate

# 3. 加载测试数据
make seed

# 4. 查看所有日志
make logs

# 5. 重新构建并启动
make rebuild
```

### 验证步骤

1. 访问前端：<http://localhost>
2. 应该能看到 Ticket 列表
3. 应该能看到标签列表
4. 可以创建、编辑、删除 Ticket

如果问题仍然存在，请检查：

- 浏览器控制台的错误信息
- 后端日志：`make logs-backend`
- 前端日志：`make logs-frontend`
