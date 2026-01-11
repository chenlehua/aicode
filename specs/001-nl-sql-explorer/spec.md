# Feature Specification: Natural Language SQL Explorer

**Feature Branch**: `001-nl-sql-explorer`  
**Created**: 2026-01-11  
**Status**: Draft  
**Input**: User description: "Database query tool with natural language SQL generation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Database Connection (Priority: P1)

A user wants to connect to their PostgreSQL database to explore its structure and run queries. They
enter their database connection URL, and the system connects, retrieves the database metadata
(tables and views), and displays the schema information.

**Why this priority**: This is the foundational capability - without database connectivity, no other
features can function. Users need to see their database structure before they can query it.

**Independent Test**: Can be fully tested by adding a connection URL and verifying that tables and
views are displayed. Delivers immediate value by showing database structure.

**Acceptance Scenarios**:

1. **Given** the user is on the home page, **When** they enter a valid PostgreSQL connection URL
   and submit, **Then** the system connects to the database and displays a list of tables and views
   with their column information.

2. **Given** the user enters an invalid connection URL, **When** they submit, **Then** the system
   displays a clear error message explaining the connection failure.

3. **Given** the user has previously connected to a database, **When** they return to the
   application, **Then** their connection and cached metadata are available without re-fetching.

---

### User Story 2 - Execute Manual SQL Query (Priority: P2)

A user wants to run a custom SQL query against their connected database. They type SQL in the
editor, submit it, and see the results displayed in a table format.

**Why this priority**: Direct SQL querying is the core value proposition for database professionals.
Once connected, users expect to execute queries immediately.

**Independent Test**: Can be tested by connecting to a database and executing a SELECT query,
verifying results appear in tabular format.

**Acceptance Scenarios**:

1. **Given** the user is connected to a database, **When** they enter a valid SELECT query and
   execute it, **Then** the results are displayed in a table format.

2. **Given** the user enters a query without a LIMIT clause, **When** they execute it, **Then**
   the system automatically adds `LIMIT 1000` and displays up to 1000 rows.

3. **Given** the user enters a query with syntax errors, **When** they execute it, **Then** the
   system displays a clear error message indicating the syntax problem.

4. **Given** the user enters a non-SELECT query (INSERT, UPDATE, DELETE), **When** they attempt
   to execute it, **Then** the system rejects the query with a message explaining only SELECT
   queries are allowed.

---

### User Story 3 - Generate SQL from Natural Language (Priority: P3)

A user who is not fluent in SQL wants to query the database using plain language. They describe
what data they want in natural language, and the system generates the corresponding SQL query,
which they can review, edit, and execute.

**Why this priority**: This differentiates the tool from standard SQL clients by making database
querying accessible to non-technical users. Requires P1 (metadata for context) and benefits from
P2 (query execution infrastructure).

**Independent Test**: Can be tested by connecting to a database and asking a natural language
question like "show me all customers from New York", verifying a valid SQL query is generated.

**Acceptance Scenarios**:

1. **Given** the user is connected to a database with metadata loaded, **When** they enter a
   natural language description like "show all orders from last month", **Then** the system
   generates a valid SQL query using the actual table and column names from the database.

2. **Given** the system generates a SQL query, **When** the user views it, **Then** they can
   edit the query before execution.

3. **Given** the user's natural language request is ambiguous, **When** the system cannot
   determine the intent, **Then** it asks clarifying questions or suggests multiple possible
   interpretations.

---

### Edge Cases

- What happens when the database connection times out during query execution?
  - System displays timeout error and suggests checking network/database availability

- What happens when the user's query returns zero rows?
  - System displays an empty table with column headers and a "No results found" message

- What happens when the database schema changes after metadata was cached?
  - User can manually refresh metadata; stale cache may cause query errors which prompt refresh

- What happens when the LLM service is unavailable?
  - Natural language feature shows an error; manual SQL query remains functional

- What happens when query results exceed the display limit?
  - Results are truncated at 1000 rows with a message indicating more rows exist

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a PostgreSQL connection URL and establish a connection
- **FR-002**: System MUST retrieve and display database metadata (tables, views, columns, data types)
- **FR-003**: System MUST persist connection URLs and metadata locally for reuse across sessions
- **FR-004**: System MUST provide a SQL editor for users to input queries
- **FR-005**: System MUST validate all SQL queries for correct syntax before execution
- **FR-006**: System MUST reject non-SELECT queries (INSERT, UPDATE, DELETE, DROP, etc.)
- **FR-007**: System MUST automatically append `LIMIT 1000` to queries without a LIMIT clause
- **FR-008**: System MUST display query results in a tabular format
- **FR-009**: System MUST accept natural language descriptions and generate corresponding SQL queries
- **FR-010**: System MUST use database metadata as context when generating SQL from natural language
- **FR-011**: System MUST allow users to edit generated SQL before execution
- **FR-012**: System MUST display clear error messages for connection failures, syntax errors, and
  execution errors

### Key Entities

- **DatabaseConnection**: Represents a saved database connection with URL, display name, and
  connection status. Users can have multiple saved connections.

- **DatabaseMetadata**: Cached schema information for a connected database, including tables, views,
  columns, data types, and relationships. Associated with a DatabaseConnection.

- **Table/View**: Individual database objects with name, type (table/view), and list of columns
  with their data types.

- **Query**: A SQL query (either manually entered or generated) with its text, execution status,
  and associated results.

- **QueryResult**: The output of an executed query, containing column definitions and row data in
  structured format for table display.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can connect to a database and view its structure within 10 seconds of entering
  the connection URL (excluding network latency)

- **SC-002**: Users can execute a simple SELECT query and see results within 5 seconds (excluding
  database query time)

- **SC-003**: 90% of natural language queries for common operations (select, filter, sort, count)
  generate valid, executable SQL on the first attempt

- **SC-004**: Users with no SQL knowledge can retrieve data from a database using natural language
  in under 2 minutes

- **SC-005**: All syntax errors in user-entered SQL are detected before execution, with error
  messages clear enough for users to understand what needs to be fixed

- **SC-006**: Query results display correctly in tabular format for up to 1000 rows and 50 columns
  without performance degradation

## Assumptions

- Users have valid PostgreSQL database credentials and network access to their database
- The LLM service (OpenAI) is available and has sufficient quota for natural language processing
- Databases being queried have reasonable schema sizes (up to ~500 tables/views)
- Users are comfortable with viewing data in JSON/tabular format
- Network latency to user databases is reasonable (under 1 second for metadata queries)
