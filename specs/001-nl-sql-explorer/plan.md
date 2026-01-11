# Implementation Plan: Natural Language SQL Explorer

**Branch**: `001-nl-sql-explorer` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-nl-sql-explorer/spec.md`

## Summary

A database query tool that enables users to connect to PostgreSQL databases, explore schema metadata,
execute SQL queries with syntax validation, and generate SQL from natural language using Alibaba's
Qwen LLM. The tool features a web interface with a Monaco-based SQL editor and displays results in
tabular format.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript strict mode (frontend)  
**Primary Dependencies**:
- Backend: FastAPI, sqlglot, openai SDK (DashScope-compatible), asyncpg, aiosqlite
- Frontend: React 18, Refine 5, Ant Design 5, Tailwind CSS, Monaco Editor  

**Storage**:
- Local metadata: SQLite at `~/.db_query/db_query.db`
- User databases: PostgreSQL (connected via URL)

**Testing**: pytest (backend), vitest (frontend)  
**Target Platform**: Web application (browser-based)  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: Query results within 5 seconds, metadata fetch within 10 seconds  
**Constraints**: CORS enabled for all origins, no authentication required  
**Scale/Scope**: Single-user local tool, ~500 tables/views per database

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Ergonomic Python & TypeScript | ✅ Pass | Backend in Python, frontend in TypeScript |
| II. Strict Type Safety | ✅ Pass | Python type hints, TypeScript strict mode |
| III. Pydantic Data Models | ✅ Pass | All API schemas use Pydantic BaseModel |
| IV. camelCase JSON Output | ✅ Pass | Pydantic alias_generator configured |
| V. Open Access | ✅ Pass | No authentication implemented |

**All gates passed** - proceeding with implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-nl-sql-explorer/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Getting started guide
├── contracts/           # Phase 1: API contracts
│   └── openapi.yaml
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
w2/db_query/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Configuration (env vars, paths)
│   │   ├── database.py       # SQLite connection management
│   │   ├── models/           # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── database.py   # DatabaseConnection, Metadata models
│   │   │   └── query.py      # Query, QueryResult models
│   │   ├── services/         # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── connection.py # Database connection handling
│   │   │   ├── metadata.py   # Schema introspection
│   │   │   ├── query.py      # SQL execution & validation
│   │   │   └── llm.py        # Natural language to SQL
│   │   └── routers/          # API endpoints
│   │       ├── __init__.py
│   │       └── databases.py  # /api/v1/dbs routes
│   ├── pyproject.toml
│   └── tests/
│       ├── conftest.py
│       └── test_*.py
│
└── frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── main.tsx
    │   ├── vite-env.d.ts
    │   ├── components/
    │   │   ├── DatabaseList.tsx
    │   │   ├── SchemaViewer.tsx
    │   │   ├── SqlEditor.tsx
    │   │   └── ResultsTable.tsx
    │   ├── pages/
    │   │   ├── HomePage.tsx
    │   │   └── DatabasePage.tsx
    │   └── services/
    │       └── api.ts
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── vite.config.ts
    └── index.html
```

**Structure Decision**: Web application structure selected because this feature requires both a
Python backend (FastAPI for API, sqlglot for parsing, LLM integration) and a React frontend
(Monaco editor, interactive UI).
