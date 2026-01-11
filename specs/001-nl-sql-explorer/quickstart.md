# Quickstart: Natural Language SQL Explorer

## Prerequisites

- Python 3.12+
- Node.js 18+
- uv (Python package manager)
- A PostgreSQL database to connect to
- DashScope API key (for natural language queries)

## Environment Setup

1. **Set environment variable** for LLM access:

```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

2. **Ensure SQLite storage directory exists**:

```bash
mkdir -p ~/.db_query
```

## Backend Setup

```bash
# Navigate to backend directory
cd w2/db_query/backend

# Install dependencies with uv
uv sync

# Start the development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Verify Backend

```bash
# Check API is running
curl http://localhost:8000/api/v1/dbs

# Expected: []
```

## Frontend Setup

```bash
# Navigate to frontend directory
cd w2/db_query/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## Basic Usage

### 1. Add a Database Connection

```bash
curl -X PUT http://localhost:8000/api/v1/dbs/mydb \
  -H "Content-Type: application/json" \
  -d '{"url": "postgres://user:password@localhost:5432/mydb"}'
```

**Response**: Database metadata including all tables and columns.

### 2. Execute a SQL Query

```bash
curl -X POST http://localhost:8000/api/v1/dbs/mydb/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users"}'
```

**Response**: Query results with columns and rows.

### 3. Generate SQL from Natural Language

```bash
curl -X POST http://localhost:8000/api/v1/dbs/mydb/query/natural \
  -H "Content-Type: application/json" \
  -d '{"prompt": "查询所有活跃用户的邮箱"}'
```

**Response**: Generated SQL query ready to execute.

## Frontend Workflow

1. **Home Page**: View all saved database connections
2. **Add Database**: Click "Add Database", enter name and connection URL
3. **View Schema**: Click on a database to see tables and columns
4. **Query**: Use the SQL editor or natural language input
5. **Results**: View query results in a table format

## Common Issues

### Connection Failed

- Verify PostgreSQL is running and accessible
- Check the connection URL format: `postgres://user:password@host:port/database`
- Ensure network access to the database server

### LLM Not Working

- Verify `DASHSCOPE_API_KEY` is set correctly
- Check DashScope API quota and status
- Manual SQL queries still work when LLM is unavailable

### CORS Errors

- Backend automatically allows all origins
- If issues persist, check browser console for specific errors

## Development Tips

### Backend

```bash
# Run with auto-reload
uv run uvicorn app.main:app --reload

# Run type checks
uv run mypy app/

# Run tests
uv run pytest
```

### Frontend

```bash
# Development server
npm run dev

# Type check
npm run typecheck

# Build for production
npm run build
```

## API Documentation

Once the backend is running, access the interactive API docs at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
