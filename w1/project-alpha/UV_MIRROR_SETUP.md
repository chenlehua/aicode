# UV 国内镜像源配置指南

## 概述

为了加速 Python 包的下载，项目已配置使用清华大学 PyPI 镜像源。

## 配置方式

### 1. 环境变量（推荐）

在 shell 中设置环境变量：

```bash
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```

永久设置（添加到 `~/.zshrc` 或 `~/.bashrc`）：

```bash
echo 'export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple' >> ~/.zshrc
echo 'export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple' >> ~/.zshrc
source ~/.zshrc
```

### 2. Docker 环境

Dockerfile 中已自动配置：

```dockerfile
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV UV_HTTP_TIMEOUT=300
```

### 3. 命令行参数

在命令中直接指定：

```bash
uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple
uv pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple package-name
```

## 已配置的文件

- ✅ `backend/Dockerfile` - Docker 构建时自动使用国内源
- ✅ `start-backend.sh` - 本地开发脚本自动设置环境变量
- ✅ `Makefile` - format 和 format-check 命令使用国内源

## 可用的国内镜像源

1. **清华大学**（推荐）：`https://pypi.tuna.tsinghua.edu.cn/simple`
2. **阿里云**：`https://mirrors.aliyun.com/pypi/simple/`
3. **中科大**：`https://pypi.mirrors.ustc.edu.cn/simple/`
4. **豆瓣**：`https://pypi.douban.com/simple/`

## 验证配置

检查当前使用的源：

```bash
# 查看环境变量
echo $UV_INDEX_URL

# 测试下载速度
time uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 故障排查

如果遇到下载失败：

1. 检查网络连接
2. 尝试其他镜像源
3. 增加超时时间：`export UV_HTTP_TIMEOUT=300`
4. 检查防火墙设置

## 注意事项

- 镜像源可能偶尔不可用，建议配置多个备用源
- 某些包可能只在官方源可用
- 定期更新镜像源地址
