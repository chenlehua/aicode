# Tasks: Natural Language SQL Explorer

**Input**: Design documents from `/specs/001-nl-sql-explorer/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested - test tasks are excluded.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `w2/db_query/backend/app/`
- **Frontend**: `w2/db_query/frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend project structure with uv in w2/db_query/backend/
- [x] T002 Initialize pyproject.toml with dependencies (fastapi, sqlglot, openai, asyncpg, aiosqlite) in w2/db_query/backend/pyproject.toml
- [x] T003 [P] Create frontend project with Vite + React + TypeScript in w2/db_query/frontend/
- [x] T004 [P] Configure package.json with dependencies (@refinedev/core, @refinedev/antd, antd, @monaco-editor/react, tailwindcss) in w2/db_query/frontend/package.json
- [x] T005 [P] Configure TypeScript strict mode in w2/db_query/frontend/tsconfig.json
- [x] T006 [P] Configure Tailwind CSS in w2/db_query/frontend/tailwind.config.js
- [x] T007 [P] Create index.html entry point in w2/db_query/frontend/index.html
- [x] T008 [P] Configure Vite for development in w2/db_query/frontend/vite.config.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T009 Create CamelModel base class with Pydantic config in w2/db_query/backend/app/models/__init__.py
- [x] T010 Implement config module with env vars (DASHSCOPE_API_KEY, DB_PATH) in w2/db_query/backend/app/config.py
- [x] T011 Implement SQLite database initialization and connection in w2/db_query/backend/app/database.py
- [x] T012 [P] Create DatabaseConnection Pydantic models in w2/db_query/backend/app/models/database.py
- [x] T013 [P] Create ErrorResponse Pydantic model in w2/db_query/backend/app/models/error.py
- [x] T014 Create FastAPI app with CORS middleware in w2/db_query/backend/app/main.py
- [x] T015 Setup API router structure in w2/db_query/backend/app/routers/__init__.py

### Frontend Foundation

- [x] T016 Create main.tsx entry point with React root in w2/db_query/frontend/src/main.tsx
- [x] T017 Create App.tsx with Refine provider setup in w2/db_query/frontend/src/App.tsx
- [x] T018 [P] Create TypeScript interfaces for all models in w2/db_query/frontend/src/types/index.ts
- [x] T019 [P] Create API service with base URL config in w2/db_query/frontend/src/services/api.ts
- [x] T020 [P] Setup global CSS with Tailwind imports in w2/db_query/frontend/src/index.css

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add Database Connection (Priority: P1) 🎯 MVP

**Goal**: Users can connect to PostgreSQL databases and view schema metadata (tables, views, columns)

**Independent Test**: Add a connection URL, verify tables and views are displayed with column information

### Backend for User Story 1

- [ ] T021 [P] [US1] Create TableMetadata and ColumnMetadata models in w2/db_query/backend/app/models/database.py
- [ ] T022 [P] [US1] Create DatabaseMetadata aggregation model in w2/db_query/backend/app/models/database.py
- [ ] T023 [US1] Implement connection service with asyncpg pool in w2/db_query/backend/app/services/connection.py
- [ ] T024 [US1] Implement metadata extraction from information_schema in w2/db_query/backend/app/services/metadata.py
- [ ] T025 [US1] Implement database CRUD operations in SQLite in w2/db_query/backend/app/services/database.py
- [ ] T026 [US1] Create GET /api/v1/dbs endpoint in w2/db_query/backend/app/routers/databases.py
- [ ] T027 [US1] Create PUT /api/v1/dbs/{name} endpoint in w2/db_query/backend/app/routers/databases.py
- [ ] T028 [US1] Create GET /api/v1/dbs/{name} endpoint in w2/db_query/backend/app/routers/databases.py
- [ ] T029 [US1] Create DELETE /api/v1/dbs/{name} endpoint in w2/db_query/backend/app/routers/databases.py
- [ ] T030 [US1] Add error handling for connection failures in w2/db_query/backend/app/routers/databases.py

### Frontend for User Story 1

- [ ] T031 [P] [US1] Create DatabaseList component displaying saved connections in w2/db_query/frontend/src/components/DatabaseList.tsx
- [ ] T032 [P] [US1] Create AddDatabaseForm component for URL input in w2/db_query/frontend/src/components/AddDatabaseForm.tsx
- [ ] T033 [P] [US1] Create SchemaViewer component showing tables/views/columns in w2/db_query/frontend/src/components/SchemaViewer.tsx
- [ ] T034 [US1] Create HomePage with database list and add form in w2/db_query/frontend/src/pages/HomePage.tsx
- [ ] T035 [US1] Create DatabasePage showing selected database metadata in w2/db_query/frontend/src/pages/DatabasePage.tsx
- [ ] T036 [US1] Implement database API hooks (list, create, get, delete) in w2/db_query/frontend/src/hooks/useDatabases.ts
- [ ] T037 [US1] Add routing between HomePage and DatabasePage in w2/db_query/frontend/src/App.tsx

**Checkpoint**: User Story 1 complete - users can connect to databases and view schema

---

## Phase 4: User Story 2 - Execute Manual SQL Query (Priority: P2)

**Goal**: Users can write SQL queries in Monaco editor and see results in a table

**Independent Test**: Connect to database, write SELECT query, verify results display in table format

### Backend for User Story 2

- [ ] T038 [P] [US2] Create QueryRequest and QueryResult models in w2/db_query/backend/app/models/query.py
- [ ] T039 [P] [US2] Create ColumnInfo model for result columns in w2/db_query/backend/app/models/query.py
- [ ] T040 [P] [US2] Create QueryHistory model in w2/db_query/backend/app/models/history.py
- [ ] T041 [US2] Implement SQL validation with sqlglot in w2/db_query/backend/app/services/query.py
- [ ] T042 [US2] Implement SELECT-only enforcement in w2/db_query/backend/app/services/query.py
- [ ] T043 [US2] Implement automatic LIMIT 1000 injection in w2/db_query/backend/app/services/query.py
- [ ] T044 [US2] Implement query execution against PostgreSQL in w2/db_query/backend/app/services/query.py
- [ ] T045 [US2] Implement query history storage in SQLite in w2/db_query/backend/app/services/history.py
- [ ] T046 [US2] Create POST /api/v1/dbs/{name}/query endpoint in w2/db_query/backend/app/routers/databases.py
- [ ] T047 [US2] Create GET /api/v1/dbs/{name}/history endpoint in w2/db_query/backend/app/routers/databases.py
- [ ] T048 [US2] Add error handling for syntax errors and non-SELECT queries in w2/db_query/backend/app/routers/databases.py

### Frontend for User Story 2

- [ ] T049 [P] [US2] Create SqlEditor component with Monaco Editor in w2/db_query/frontend/src/components/SqlEditor.tsx
- [ ] T050 [P] [US2] Create ResultsTable component for query results in w2/db_query/frontend/src/components/ResultsTable.tsx
- [ ] T051 [P] [US2] Create QueryHistory component showing past queries in w2/db_query/frontend/src/components/QueryHistory.tsx
- [ ] T052 [US2] Implement query execution hook in w2/db_query/frontend/src/hooks/useQuery.ts
- [ ] T053 [US2] Integrate SqlEditor and ResultsTable into DatabasePage in w2/db_query/frontend/src/pages/DatabasePage.tsx
- [ ] T054 [US2] Add query execution button and loading states in w2/db_query/frontend/src/pages/DatabasePage.tsx
- [ ] T055 [US2] Display SQL validation errors inline in w2/db_query/frontend/src/components/SqlEditor.tsx

**Checkpoint**: User Story 2 complete - users can execute SQL queries and view results

---

## Phase 5: User Story 3 - Generate SQL from Natural Language (Priority: P3)

**Goal**: Users can describe queries in natural language and get SQL generated by LLM

**Independent Test**: Connect to database, enter natural language prompt, verify valid SQL is generated

### Backend for User Story 3

- [ ] T056 [P] [US3] Create NaturalQueryRequest model in w2/db_query/backend/app/models/query.py
- [ ] T057 [P] [US3] Create GeneratedSQL response model in w2/db_query/backend/app/models/query.py
- [ ] T058 [US3] Implement LLM client with DashScope configuration in w2/db_query/backend/app/services/llm.py
- [ ] T059 [US3] Implement metadata-to-prompt formatting for LLM context in w2/db_query/backend/app/services/llm.py
- [ ] T060 [US3] Implement SQL generation from natural language in w2/db_query/backend/app/services/llm.py
- [ ] T061 [US3] Validate generated SQL with sqlglot in w2/db_query/backend/app/services/llm.py
- [ ] T062 [US3] Create POST /api/v1/dbs/{name}/query/natural endpoint in w2/db_query/backend/app/routers/databases.py
- [ ] T063 [US3] Add error handling for LLM failures in w2/db_query/backend/app/routers/databases.py

### Frontend for User Story 3

- [ ] T064 [P] [US3] Create NaturalLanguageInput component with prompt textarea in w2/db_query/frontend/src/components/NaturalLanguageInput.tsx
- [ ] T065 [P] [US3] Create GeneratedSqlPreview component showing generated SQL in w2/db_query/frontend/src/components/GeneratedSqlPreview.tsx
- [ ] T066 [US3] Implement natural language API hook in w2/db_query/frontend/src/hooks/useNaturalQuery.ts
- [ ] T067 [US3] Integrate NL input with SqlEditor for edit-before-execute flow in w2/db_query/frontend/src/pages/DatabasePage.tsx
- [ ] T068 [US3] Add tab switching between SQL Editor and Natural Language modes in w2/db_query/frontend/src/pages/DatabasePage.tsx
- [ ] T069 [US3] Display LLM explanation alongside generated SQL in w2/db_query/frontend/src/components/GeneratedSqlPreview.tsx

**Checkpoint**: All user stories complete - full feature is functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T070 [P] Add loading spinners and skeleton states in w2/db_query/frontend/src/components/
- [ ] T071 [P] Add toast notifications for success/error feedback in w2/db_query/frontend/src/
- [ ] T072 [P] Style all components with consistent Tailwind/Ant Design theme in w2/db_query/frontend/src/
- [ ] T073 [P] Add keyboard shortcuts (Ctrl+Enter to execute) in w2/db_query/frontend/src/components/SqlEditor.tsx
- [ ] T074 Add metadata refresh button to update cached schema in w2/db_query/frontend/src/pages/DatabasePage.tsx
- [ ] T075 Add empty state handling (no databases, no results) in w2/db_query/frontend/src/
- [ ] T076 Validate quickstart.md workflow end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - MVP milestone
- **User Story 2 (Phase 4)**: Depends on Foundational - Can start after US1 or in parallel
- **User Story 3 (Phase 5)**: Depends on Foundational - Can start after US1 or in parallel
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - No dependencies on other stories
- **User Story 2 (P2)**: Foundation + uses connection from US1 (but independently testable)
- **User Story 3 (P3)**: Foundation + uses metadata from US1 + can execute via US2 (but independently testable)

### Within Each User Story

- Models before services
- Services before routers/endpoints
- Backend complete before frontend integration
- Core implementation before polish

### Parallel Opportunities

**Phase 1 (Setup):**
- T003, T004, T005, T006, T007, T008 can all run in parallel

**Phase 2 (Foundational):**
- T012, T013 can run in parallel (models)
- T016, T017, T018, T019, T020 can run in parallel (frontend setup)

**Phase 3 (US1):**
- T021, T022 (backend models) in parallel
- T031, T032, T033 (frontend components) in parallel

**Phase 4 (US2):**
- T038, T039, T040 (models) in parallel
- T049, T050, T051 (frontend components) in parallel

**Phase 5 (US3):**
- T056, T057 (models) in parallel
- T064, T065 (frontend components) in parallel

---

## Parallel Example: User Story 1

```bash
# Backend models in parallel:
Task: T021 "Create TableMetadata and ColumnMetadata models"
Task: T022 "Create DatabaseMetadata aggregation model"

# Frontend components in parallel:
Task: T031 "Create DatabaseList component"
Task: T032 "Create AddDatabaseForm component"
Task: T033 "Create SchemaViewer component"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Database Connection & Schema Viewing
4. **STOP and VALIDATE**: Test connecting to a real PostgreSQL database
5. Deploy/demo if ready - users can already explore database schemas!

### Incremental Delivery

1. **Setup + Foundational** → Project structure ready
2. **+ User Story 1** → MVP: Connect and view schemas ✅
3. **+ User Story 2** → Add: Execute SQL queries ✅
4. **+ User Story 3** → Add: Natural language queries ✅
5. **+ Polish** → Production-ready experience

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Backend for all user stories
   - Developer B: Frontend for all user stories
   - OR split by user story if preferred
3. Stories integrate at API contract boundary

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 76
