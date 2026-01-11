# Backend Dockerfile
FROM python:3.11-slim as base

# Configure APT to use Aliyun mirror (for Chinese users)
RUN if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
        sed -i 's|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources; \
    else \
        echo "deb https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib" > /etc/apt/sources.list && \
        echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
        echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib" >> /etc/apt/sources.list; \
    fi

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN chmod +x /usr/local/bin/uv

# Configure uv/pip to use Tsinghua PyPI mirror
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV UV_HTTP_TIMEOUT=300

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install build dependencies first (hatchling) using --system flag
RUN uv pip install --system --index-url https://pypi.tuna.tsinghua.edu.cn/simple hatchling || \
    (echo "Retrying hatchling installation..." && sleep 5 && uv pip install --system --index-url https://pypi.tuna.tsinghua.edu.cn/simple hatchling)

# Install project dependencies
# uv sync will create a virtual environment and install all dependencies
# UV_INDEX_URL environment variable is already set above
RUN uv sync --frozen --index-url https://pypi.tuna.tsinghua.edu.cn/simple || \
    (echo "Retrying uv sync..." && sleep 5 && uv sync --frozen --index-url https://pypi.tuna.tsinghua.edu.cn/simple)

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
