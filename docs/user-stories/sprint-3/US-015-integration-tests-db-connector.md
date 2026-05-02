# US-015: Integration Tests — DB Connector

**Epic**: EPIC-004
**Sprint**: Sprint 3
**Points**: 5
**Priority**: Must Have

## User Story

> As a **developer**, I want integration tests for `DBConnector` that run against a
> real in-memory SQLite engine so that engine creation, connection testing, and query
> execution are verified end-to-end without requiring a MySQL server in CI.

## Acceptance Criteria

```gherkin
Feature: Integration Tests — DB Connector

  Scenario: create_engine succeeds with valid SQLite config
    Given a DBConfig pointing to an in-memory SQLite database
    When DBConnector().create_engine(config) is called
    Then a live Engine is returned
    And "SELECT 1" executes successfully against it

  Scenario: create_engine raises DatabaseConnectionError for bad host
    Given a DBConfig with an unreachable MySQL host
    When create_engine(config) is called
    Then DatabaseConnectionError is raised with the host name in the message

  Scenario: test_connection returns True for live engine
    Given an active SQLite engine created via the sqlite_engine fixture
    When test_connection(engine) is called
    Then it returns True

  Scenario: test_connection returns False for disposed engine
    Given an engine that has been disposed
    When test_connection(engine) is called
    Then it returns False (no exception raised)

  Scenario: execute_query returns correct DataFrame
    Given an engine with a "users" table containing 3 rows
    When execute_query(engine, "SELECT * FROM users") is called
    Then a DataFrame with 3 rows and correct column names is returned

  Scenario: execute_query rejects non-SELECT statements
    Given an active engine
    When execute_query(engine, "DELETE FROM users") is called
    Then ValueError is raised: "Only SELECT statements are permitted"

  Scenario: execute_query raises QueryExecutionError on invalid SQL
    Given an active engine
    When execute_query(engine, "SELECT * FROM nonexistent_table") is called
    Then QueryExecutionError is raised
```

## Technical Notes
- Tests live in `tests/integration/test_db_connector.py`
- `sqlite_engine` fixture in `conftest.py` is a **generator** fixture — disposes engine in teardown (BUG-002 fix)
- Use `DBConfig` with `dialect="sqlite"` + `database=":memory:"` for CI-safe tests
- All engines created in tests must be disposed in teardown to prevent `ResourceWarning`
- Use `pytest.raises` with `match=` parameter for precise error message assertions

## Definition of Done
- [x] `tests/integration/test_db_connector.py` covers TC-008 to TC-010 scenarios
- [x] 7 test functions passing
- [x] Branch coverage ≥ 74% for `src/services/db_connector.py`
- [x] No `ResourceWarning: unclosed <...>` in test output (BUG-002 resolved)
- [x] Tests pass without a running MySQL server
- [x] `ruff` + `mypy` clean on test file
- [x] Code review approved (CR-001)

## Status
✅ DONE
