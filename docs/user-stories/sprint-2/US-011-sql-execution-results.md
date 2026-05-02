# US-011: SQL Execution & Results Table

**Epic**: EPIC-003
**Sprint**: Sprint 2
**Points**: 5
**Priority**: Must Have

## User Story

> As a **user**, I want an "▶ Execute SQL" button that runs the generated SELECT query
> against my connected live database and displays the results in a scrollable dataframe
> so that I can see actual data without leaving the app.

## Acceptance Criteria

```gherkin
Feature: SQL Execution & Results Table

  Scenario: Execute valid SELECT and display results
    Given I am in "Live Database" mode with an active engine
    And a SQL query has been generated and is shown in the output panel
    When I click "▶ Execute SQL"
    Then the query is executed against the live database
    And results are displayed in a st.dataframe below the SQL output
    And the dataframe supports column sorting by clicking headers

  Scenario: Execute SQL with no results
    Given the query returns zero rows
    When I click "▶ Execute SQL"
    Then an empty dataframe is shown (column headers visible, no rows)

  Scenario: Non-SELECT statement blocked
    Given the generated SQL starts with INSERT, UPDATE, DELETE, or DROP
    When execute_query() is called
    Then ValueError is raised: "Only SELECT statements are permitted"
    And the error is shown to the user via st.error()

  Scenario: Query execution failure shows error
    Given the SQL is syntactically invalid or references a dropped table
    When I click "▶ Execute SQL"
    Then a red error banner "❌ Query execution failed: <reason>" is displayed
    And no partial results are shown

  Scenario: Execute button only shown in Live Database mode
    Given the mode is "Static Schema"
    When the app renders
    Then no "▶ Execute SQL" button is visible

  Scenario: Results persist after rerun
    Given I have executed a query and results are shown
    When I scroll the page or interact with the sidebar
    Then the results remain visible (stored in st.session_state["query_result"])
```

## Technical Notes
- `DBConnector.execute_query(engine, sql)` in `src/services/db_connector.py`
- Returns `pd.DataFrame`; results stored in `st.session_state["query_result"]`
- Button shown only when `mode == "Live Database"` and `generated_sql` and `db_engine` are set
- Results rendered via `st.dataframe(result_df, use_container_width=True)`
- Non-SELECT check: `sql.strip().upper().startswith("SELECT")`
- Catches `(QueryExecutionError, SQLAlchemyError)` — displays `st.error()`

## Definition of Done
- [x] `DBConnector.execute_query()` implemented in `src/services/db_connector.py`
- [x] Returns `pd.DataFrame`; raises `ValueError` for non-SELECT; raises `QueryExecutionError` on DB failure
- [x] "▶ Execute SQL" button wired in `src/app.py`
- [x] Results displayed via `st.dataframe(use_container_width=True)`
- [x] Results persisted in `st.session_state["query_result"]`
- [x] Error handling: `QueryExecutionError` and `SQLAlchemyError` → `st.error()`
- [x] Integration tests (TC-008–TC-010) passing via SQLite in-memory engine
- [x] Code review approved (CR-001)

## Status
✅ DONE
