# DB Query Backend

Natural Language SQL Explorer - Backend API

## Description

FastAPI-based backend for the DB Query tool that enables users to connect to PostgreSQL databases, explore schema metadata, execute SQL queries, and generate SQL from natural language using Alibaba's Qwen LLM.

## Features

- PostgreSQL database connection management
- Schema metadata extraction and caching
- SQL query execution with validation
- Natural language to SQL generation
- Query history tracking

## Requirements

- Python 3.12+
- uv package manager

## Installation

```bash
uv sync
```

## Configuration

Set the following environment variable:

- `DASHSCOPE_API_KEY`: Alibaba DashScope API key for Qwen LLM

## Running

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
