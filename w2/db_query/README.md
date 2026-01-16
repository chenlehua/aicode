# Natural Language SQL Explorer

A web-based tool for exploring PostgreSQL databases with natural language query generation.

## Features

- 🔌 Connect to PostgreSQL databases
- 📊 View database schema (tables, views, columns)
- ✍️ Execute SQL queries with syntax validation
- 🤖 Generate SQL from natural language using Alibaba Qwen LLM
- 📜 Query history tracking
- 🎨 Modern web UI with Monaco Editor

## Quick Start with Docker Compose

### Prerequisites

- Docker and Docker Compose installed
- DashScope API key (for natural language queries)

### Production Mode

1. **Set environment variables**:

```bash
export DASHSCOPE_API_KEY="your-api-key-here"
```

2. **Start all services**:

```bash
docker-compose up -d
```

3. **Access the application**:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Development Mode

1. **Start development services**:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

2. **Access the application**:

- Frontend: http://localhost:5173 (with hot reload)
- Backend API: http://localhost:8000 (with auto-reload)
- PostgreSQL: localhost:5432

### Using Makefile

```bash
# Start production services
make docker-up

# Start development services
make docker-dev-up

# View logs
make docker-logs
# or
make docker-dev-logs

# Stop services
make docker-down
# or
make docker-dev-down

# Clean everything
make docker-clean
```

## Local Development (without Docker)

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md) for detailed setup instructions.

## PostgreSQL Test Database

The docker-compose setup includes a PostgreSQL instance with:

- **Host**: `postgres` (in Docker network) or `localhost` (from host)
- **Port**: `5432`
- **User**: `postgres`
- **Password**: `postgres`
- **Database**: `testdb`

### Connect from Host

```bash
psql -h localhost -U postgres -d testdb
# Password: postgres
```

### Example Connection URL

```
postgres://postgres:postgres@localhost:5432/testdb
```

## Project Structure

```
w2/db_query/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   ├── Dockerfile   # Production Docker image
│   └── pyproject.toml
├── frontend/        # React frontend
│   ├── src/         # Source code
│   ├── Dockerfile   # Production Docker image
│   ├── Dockerfile.dev  # Development Docker image
│   └── package.json
├── docker-compose.yml      # Production compose
├── docker-compose.dev.yml  # Development compose
└── Makefile         # Common tasks
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Configuration
DASHSCOPE_API_KEY=your-dashscope-api-key-here

# Optional: Database path (defaults to ~/.db_query/db_query.db)
# DB_PATH=/app/data/db_query.db

# Optional: API configuration
# API_V1_PREFIX=/api/v1
# CORS_ORIGINS=["*"]
```

## API Endpoints

- `GET /api/v1/dbs` - List all databases
- `PUT /api/v1/dbs/{name}` - Add/update database connection
- `GET /api/v1/dbs/{name}` - Get database with metadata
- `DELETE /api/v1/dbs/{name}` - Delete database connection
- `POST /api/v1/dbs/{name}/query` - Execute SQL query
- `POST /api/v1/dbs/{name}/query/natural` - Generate SQL from natural language
- `GET /api/v1/dbs/{name}/history` - Get query history

See [OpenAPI docs](http://localhost:8000/docs) for full API documentation.

## Troubleshooting

### Backend won't start

- Check if port 8000 is already in use
- Verify DASHSCOPE_API_KEY is set (optional, only needed for NL queries)
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend

- Ensure backend is running and healthy
- Check CORS configuration
- Verify API_BASE_URL in frontend environment

### PostgreSQL connection issues

- Verify PostgreSQL container is running: `docker-compose ps`
- Check PostgreSQL logs: `docker-compose logs postgres`
- Ensure connection URL format is correct: `postgres://user:password@host:port/database`

## License

MIT
