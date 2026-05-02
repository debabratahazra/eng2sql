# EPIC-003: Dynamic Schema Detection

## Goal
Enable users to connect to a live MySQL database via the Streamlit UI; auto-detect its
tables and columns using SQLAlchemy `inspect()`; and use the live schema as context for
SQL generation and execution.

## Business Value
Eliminates manual YAML schema maintenance — the tool adapts to any database automatically,
making it viable for production databases and rapid prototyping.

## Scope

### In Scope
- Database connection form in Streamlit sidebar (host, port, user, password, database)
- `SchemaDetector.detect_live_schema(engine)` using SQLAlchemy reflection
- Schema viewer panel (collapsible, shows all tables + columns)
- SQL execution against the live database (`DBConnector.execute_query`)
- Results displayed in `st.dataframe`
- Connection status indicator (✅ Connected / ❌ Error)

### Out of Scope
- Support for PostgreSQL, MSSQL, Oracle (MySQL only in v1; SQLite for tests)
- Write operations (INSERT / UPDATE / DELETE) — read-only by design
- Schema caching to disk (in-memory session cache only)

## Acceptance Criteria
- [x] AC-1: User fills in connection form and clicks "Connect" — status shows ✅ Connected
- [x] AC-2: Schema viewer lists every table and its columns after a successful connection
- [x] AC-3: `generate_sql` uses the live detected schema, not the static YAML
- [x] AC-4: "Execute SQL" button runs the generated query and shows results in a dataframe
- [x] AC-5: Invalid credentials show an `st.error` message within 5 seconds
- [x] AC-6: DB connection is closed / returned to pool after each query execution

## Dependencies
- Depends on: EPIC-001, EPIC-002
- Blocks: EPIC-004 (integration tests require this)

## Estimated Size
**T-Shirt Size**: L
**Estimated Sprints**: 1

## Child User Stories
- [x] US-008: Database Connection Form
- [x] US-009: Schema Auto-Detection
- [x] US-010: Schema Viewer Panel
- [x] US-011: SQL Execution & Results Table

## Status
- [x] Draft
- [x] Reviewed
- [x] Accepted
