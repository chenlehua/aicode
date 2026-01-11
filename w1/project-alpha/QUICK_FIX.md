# 前端不显示数据 - 快速修复

## 问题确认

API 正常工作：

- ✅ 后端健康检查正常
- ✅ Tickets API 返回 50 条数据
- ✅ Tags API 返回数据
- ✅ CORS 配置正确

## 解决方案

### 方案 1: 清除浏览器缓存（最可能的原因）

1. **Chrome/Edge**:
   - 按 `Ctrl+Shift+Delete` (Windows) 或 `Cmd+Shift+Delete` (Mac)
   - 选择"缓存的图片和文件"
   - 点击"清除数据"
   - 刷新页面 (`Ctrl+F5` 或 `Cmd+Shift+R`)

2. **Firefox**:
   - 按 `Ctrl+Shift+Delete` (Windows) 或 `Cmd+Shift+Delete` (Mac)
   - 选择"缓存"
   - 点击"立即清除"
   - 刷新页面 (`Ctrl+F5` 或 `Cmd+Shift+R`)

3. **Safari**:
   - 按 `Cmd+Option+E` 清除缓存
   - 按 `Cmd+Shift+R` 强制刷新

### 方案 2: 重新构建前端

```bash
# 停止前端服务
docker-compose stop frontend

# 重新构建前端（不使用缓存）
docker-compose build --no-cache frontend

# 启动前端服务
docker-compose up -d frontend
```

### 方案 3: 检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 查看 **Console** 标签页
3. 查看 **Network** 标签页
4. 检查是否有错误信息

### 方案 4: 完全重启所有服务

```bash
# 停止所有服务
make down

# 重新构建并启动
make rebuild
```

## 验证步骤

1. 打开浏览器访问：<http://localhost>
2. 打开开发者工具（F12）
3. 查看 Network 标签页，应该能看到：
   - `GET /api/v1/tickets` - 状态码 200
   - `GET /api/v1/tags` - 状态码 200
4. 查看 Console 标签页，不应该有红色错误

## 如果仍然无法显示数据

请检查：

1. **浏览器控制台错误**：
   - 截图 Console 标签页的错误信息
   - 截图 Network 标签页的 API 请求

2. **后端日志**：

   ```bash
   make logs-backend
   ```

3. **前端日志**：

   ```bash
   make logs-frontend
   ```

4. **数据库数据**：

   ```bash
   make shell-db
   # 执行：SELECT COUNT(*) FROM tickets;
   ```

## 常见错误及解决

### 错误: "Failed to fetch"

- **原因**: CORS 或网络问题
- **解决**: 检查后端 CORS 配置，重启后端服务

### 错误: "404 Not Found"

- **原因**: API URL 配置错误
- **解决**: 检查前端构建时的 `VITE_API_URL` 环境变量

### 错误: "Network Error"

- **原因**: 后端服务未启动或无法访问
- **解决**: 检查后端服务状态 `make ps`
