#!/bin/bash
# Setup script for pre-commit hooks

set -e

echo "Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    if command -v uv &> /dev/null; then
        uv pip install pre-commit
    elif command -v pip3 &> /dev/null; then
        pip3 install pre-commit
    elif command -v pip &> /dev/null; then
        pip install pre-commit
    else
        echo "Error: Neither uv, pip3, nor pip found. Please install pre-commit manually."
        exit 1
    fi
fi

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Install frontend dependencies (for prettier/eslint)
if [ -d "w1/project-alpha/frontend" ]; then
    echo "Installing frontend dependencies..."
    cd w1/project-alpha/frontend
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
    cd ../../..
fi

echo ""
echo "Pre-commit setup completed!"
echo ""
echo "To test the hooks, run:"
echo "  pre-commit run --all-files"
echo ""
echo "To format code, run:"
echo "  cd w1/project-alpha && make format"
