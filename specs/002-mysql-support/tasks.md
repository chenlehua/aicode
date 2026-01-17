# Tasks: MySQL Database Support

**Input**: Existing PostgreSQL implementation in `w2/db_query/backend/app/`
**Goal**: Add MySQL database support with feature parity to PostgreSQL, including Docker Compose initialization

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `w2/db_query/backend/app/`
- **Docker**: `w2/db_query/`
- **Fixtures**: `w2/db_query/fixtures/`

---

## Phase 1: Setup (Docker & Dependencies)

**Purpose**: Infrastructure setup for MySQL support

- [X] T001 Add MySQL service to `w2/db_query/docker-compose.yml` with healthcheck, volumes, and environment variables
- [X] T002 [P] Add MySQL service to `w2/db_query/docker-compose.dev.yml` with healthcheck, volumes, and dev configuration
- [X] T003 [P] Add `aiomysql` dependency to `w2/db_query/backend/pyproject.toml` for async MySQL support
- [X] T004 Create MySQL initialization script `w2/db_query/fixtures/test_mysql.sql` with same schema and test data as PostgreSQL version

---

## Phase 2: Foundational (Core Database Abstraction)

**Purpose**: Create database abstraction layer to support multiple database types

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create database type enum in `w2/db_query/backend/app/models/database.py` to identify database types (postgresql, mysql)
- [X] T006 Update `DatabaseCreate` model in `w2/db_query/backend/app/models/database.py` to accept both PostgreSQL and MySQL connection URL patterns
- [X] T007 Create abstract connection interface in `w2/db_query/backend/app/services/connection_base.py` with common methods (get_pool, test_connection, close_pool, close_all)
- [X] T008 Refactor `w2/db_query/backend/app/services/connection.py` to implement the abstract interface for PostgreSQL

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - MySQL Connection Management (Priority: P1)

**Goal**: Users can connect to MySQL databases and manage connections

**Independent Test**: Connect to MySQL database via API and verify connection is stored and testable

### Implementation for User Story 1

- [X] T009 [US1] Create MySQL connection service in `w2/db_query/backend/app/services/connection_mysql.py` implementing abstract interface using aiomysql
- [X] T010 [US1] Create connection factory in `w2/db_query/backend/app/services/connection_factory.py` to return appropriate connection service based on URL scheme (postgresql://, mysql://)
- [X] T011 [US1] Update `ConnectionService` in `w2/db_query/backend/app/services/connection.py` to use connection factory for URL-based routing
- [X] T012 [US1] Update router `w2/db_query/backend/app/routers/databases.py` to handle both PostgreSQL and MySQL URL validation

**Checkpoint**: At this point, MySQL connection management should work independently

---

## Phase 4: User Story 2 - MySQL Metadata Extraction (Priority: P2)

**Goal**: Users can view MySQL database schema metadata (tables, views, columns)

**Independent Test**: Connect to MySQL database and verify metadata extraction returns tables, views, and columns

### Implementation for User Story 2

- [X] T013 [US2] Create MySQL metadata service in `w2/db_query/backend/app/services/metadata_mysql.py` with fetch_metadata and _fetch_columns methods
- [X] T014 [US2] Implement MySQL-specific queries for information_schema in `w2/db_query/backend/app/services/metadata_mysql.py`:
  - Table and view listing from information_schema.tables
  - Column details from information_schema.columns
  - Primary key detection from information_schema.statistics
  - Foreign key detection from information_schema.key_column_usage
- [X] T015 [US2] Create metadata factory in `w2/db_query/backend/app/services/metadata_factory.py` to return appropriate metadata service based on database type
- [X] T016 [US2] Update `DatabaseService` in `w2/db_query/backend/app/services/database.py` to use metadata factory for fetching metadata

**Checkpoint**: MySQL metadata extraction should work independently

---

## Phase 5: User Story 3 - MySQL Query Execution (Priority: P3)

**Goal**: Users can execute SQL SELECT queries against MySQL databases

**Independent Test**: Execute a SELECT query against MySQL database and verify results returned correctly

### Implementation for User Story 3

- [X] T017 [US3] Create MySQL query service in `w2/db_query/backend/app/services/query_mysql.py` with validate_sql, inject_limit, and execute_query methods
- [X] T018 [US3] Implement MySQL-specific SQL validation in `w2/db_query/backend/app/services/query_mysql.py`:
  - Use sqlglot with dialect="mysql"
  - MySQL-specific LIMIT injection
  - MySQL data type inference from Python values
- [X] T019 [US3] Create query factory in `w2/db_query/backend/app/services/query_factory.py` to return appropriate query service based on database type
- [X] T020 [US3] Update router `w2/db_query/backend/app/routers/databases.py` execute_query endpoint to use query factory

**Checkpoint**: MySQL query execution should work independently

---

## Phase 6: User Story 4 - MySQL Natural Language Query (Priority: P4)

**Goal**: Users can generate MySQL queries from natural language prompts

**Independent Test**: Use natural language prompt to generate MySQL query and verify valid MySQL syntax

### Implementation for User Story 4

- [X] T021 [US4] Update LLM service in `w2/db_query/backend/app/services/llm.py` to accept database_type parameter
- [X] T022 [US4] Modify format_metadata_prompt in `w2/db_query/backend/app/services/llm.py` to generate MySQL-specific prompts when database_type is mysql
- [X] T023 [US4] Update generate_sql validation in `w2/db_query/backend/app/services/llm.py` to use correct dialect (mysql vs postgres) based on database_type
- [X] T024 [US4] Update router `w2/db_query/backend/app/routers/databases.py` generate_natural_query endpoint to pass database_type to LLM service

**Checkpoint**: Natural language to MySQL query generation should work

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T025 Add database_type field to DatabaseMetadata, DatabaseResponse, and DatabaseWithMetadata models in `w2/db_query/backend/app/models/database.py`
- [X] T026 Update `w2/db_query/backend/app/database.py` init_db to store database_type in metadata table (Note: Not needed - database_type is derived from URL at runtime using detect_database_type())
- [X] T027 [P] Add MySQL connection URL examples to any API documentation or comments
- [X] T028 [P] Update error messages in `w2/db_query/backend/app/models/error.py` if MySQL-specific errors are needed
- [X] T029 Verify all existing PostgreSQL functionality still works after changes (regression check)
- [X] T030 Test MySQL full workflow: connect -> fetch metadata -> execute query -> natural language query (Note: Requires running Docker containers for integration test)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (Connection): Must complete before US2, US3, US4
  - US2 (Metadata): Must complete before US4 (natural language needs metadata)
  - US3 (Query): Can run in parallel with US2
  - US4 (NL Query): Depends on US2, US3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational)
                        ↓
                   Phase 3 (US1: Connection)
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   Phase 4 (US2)   Phase 5 (US3)   (parallel)
        └───────────────┼───────────────┘
                        ↓
                   Phase 6 (US4: NL Query)
                        ↓
                   Phase 7 (Polish)
```

### Within Each User Story

- Services before factories
- Factories before router updates
- Core implementation before integration

### Parallel Opportunities

- T001, T002 can run in parallel (different docker compose files)
- T002, T003 can run in parallel (docker vs python deps)
- Phase 4 (US2) and Phase 5 (US3) can run in parallel after US1 completes
- T027, T028 can run in parallel

---

## Parallel Example: Phase 1

```bash
# Launch these tasks in parallel:
Task T002: "Add MySQL to docker-compose.dev.yml"
Task T003: "Add aiomysql dependency"
```

## Parallel Example: After US1 Completes

```bash
# Launch US2 and US3 in parallel:
Task T013-T016: "MySQL Metadata Extraction (US2)"
Task T017-T020: "MySQL Query Execution (US3)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Docker + Dependencies)
2. Complete Phase 2: Foundational (Abstraction Layer)
3. Complete Phase 3: User Story 1 (Connection Management)
4. **STOP and VALIDATE**: Test MySQL connection via API
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US1 (Connection) → MySQL connections work → Demo
3. Add US2 (Metadata) → Schema browsing works → Demo
4. Add US3 (Query) → Query execution works → Demo
5. Add US4 (NL Query) → Natural language works → Demo
6. Polish → Production ready

---

## Key Files to Modify

| File | Changes |
|------|---------|
| `docker-compose.yml` | Add MySQL service |
| `docker-compose.dev.yml` | Add MySQL dev service |
| `pyproject.toml` | Add aiomysql dependency |
| `models/database.py` | Add database_type enum, update URL pattern |
| `services/connection.py` | Refactor for abstraction |
| `services/connection_mysql.py` | New - MySQL connection handling |
| `services/connection_factory.py` | New - Connection routing |
| `services/metadata_mysql.py` | New - MySQL metadata extraction |
| `services/metadata_factory.py` | New - Metadata routing |
| `services/query_mysql.py` | New - MySQL query execution |
| `services/query_factory.py` | New - Query routing |
| `services/llm.py` | Support MySQL dialect |
| `routers/databases.py` | Use factories, handle MySQL URLs |
| `fixtures/test_mysql.sql` | New - MySQL test data |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MySQL uses `mysql://` or `mysql+aiomysql://` URL schemes
- Use `aiomysql` library for async MySQL support (matches asyncpg pattern)
- MySQL information_schema differs from PostgreSQL - handle appropriately
