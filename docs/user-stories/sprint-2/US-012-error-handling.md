# US-012: Error Handling & User Feedback

**Epic**: EPIC-001, EPIC-003
**Sprint**: Sprint 2
**Points**: 3
**Priority**: Must Have

## User Story

> As a **user**, I want clear, actionable error messages when OpenAI fails, the database
> connection is refused, or the generated SQL is invalid so that I can understand what
> went wrong and take corrective action without reading log files.

## Acceptance Criteria

```gherkin
Feature: Error Handling & User Feedback

  Scenario: OpenAI API failure shows error message
    Given the OpenAI endpoint is unreachable or returns an error
    When I click "⚡ Generate SQL"
    Then a red error banner "❌ SQL generation failed: <reason>" is displayed
    And the error is logged at ERROR level
    And the app does not crash

  Scenario: Schema detection failure shows error message
    Given the static schema YAML file is missing or malformed
    When I click "⚡ Generate SQL"
    Then a red error banner "❌ Schema detection failed: <reason>" is displayed
    And the progress tracker stops at the failed step

  Scenario: Database connection failure shows error in sidebar
    Given invalid database credentials are entered
    When I click "🔗 Connect"
    Then a red error "❌ Connection failed: <reason>" appears in the sidebar
    And the connection status is set to "error"
    And no engine is stored in session state

  Scenario: SQL execution failure shows error message
    Given a connected Live Database mode
    And the generated SQL contains a syntax error or references a missing table
    When I click "▶ Execute SQL"
    Then a red error banner "❌ Query execution failed: <reason>" is displayed
    And no partial results are shown

  Scenario: Live Database mode without connection shows warning
    Given the mode is "Live Database"
    And no database connection has been made
    When I click "⚡ Generate SQL"
    Then a yellow warning "⚠️ Please connect to a database first using the sidebar." is shown
    And SQL generation is not attempted

  Scenario: Empty connection form fields show validation warning
    Given the database connection form is visible
    When I click "🔗 Connect" with one or more fields empty
    Then a yellow warning "Please fill in all connection fields." is shown
    And no connection attempt is made
```

## Technical Notes
- Exception hierarchy defined in `src/utils/exceptions.py`:
  - `Eng2SQLError` (base)
  - `SQLGenerationError` — OpenAI failure (caught in `app.py`)
  - `SchemaDetectionError` — YAML/SQLAlchemy schema error (caught in `app.py`)
  - `DatabaseConnectionError` — engine creation failure (caught in `sidebar.py`)
  - `QueryExecutionError` — SQL execution failure (caught in `app.py`)
- User-facing messages use `st.error()` (red), `st.warning()` (yellow)
- All errors also logged via `logger.error()` / `logger.warning()` with `exc_info`
- No raw exception tracebacks shown to user

## Definition of Done
- [x] `Eng2SQLError` hierarchy implemented in `src/utils/exceptions.py`
- [x] `SQLGenerationError` caught in `src/app.py` → `st.error()`
- [x] `SchemaDetectionError` caught in `src/app.py` → `st.error()`
- [x] `DatabaseConnectionError` caught in `src/components/sidebar.py` → `st.error()`
- [x] `QueryExecutionError` / `SQLAlchemyError` caught in `src/app.py` → `st.error()`
- [x] Warning shown when Live Database mode has no active connection
- [x] Validation warning shown when connection form fields are empty
- [x] Code review approved (CR-001)

## Status
✅ DONE
