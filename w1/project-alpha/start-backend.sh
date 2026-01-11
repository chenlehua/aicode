#!/bin/bash

# Start backend server using uv
cd "$(dirname "$0")/backend"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Sync dependencies (creates .venv if needed and installs dependencies)
# Use Tsinghua PyPI mirror for faster downloads in China
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
echo "Syncing dependencies with uv (using Tsinghua mirror)..."
uv sync

# Start server using uv run
echo "Starting backend server on http://localhost:8000"
uv run uvicorn app.main:app --reload --port 8000
