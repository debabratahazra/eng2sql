# US-024: `DBConnector.list_databases()` Service Method & Unit Tests

**Epic**: EPIC-006
**Sprint**: Sprint 5
**Points**: 3
**Priority**: Must Have

## User Story

> As a **developer**, I want a `DBConnector.list_databases(engine)` method that
> returns the non-system databases available on a connected MySQL server so that
> the sidebar can populate the database selection dropdown reliably and safely.

## Acceptance Criteria

```gherkin
Feature: DBConnector.list_databases() Service Method

  Scenario: Returns only non-system databases
    Given a MySQL server with databases:
      information_schema, performance_schema, mysql, sys, myapp_db, analytics_db
    When list_databases(engine) is called
    Then the return value is ["myapp_db", "analytics_db"] (order may vary)
    And information_schema, performance_schema, mysql, and sys are excluded

  Scenario: Returns empty list when no user databases exist
    Given a MySQL server where the user can only see system databases
    When list_databases(engine) is called
    Then an empty list [] is returned
    And no exception is raised

  Scenario: SQLAlchemy error is wrapped as DatabaseConnectionError
    Given a mock engine whose connect() raises SQLAlchemyError
    When list_databases(engine) is called
    Then DatabaseConnectionError is raised
    And the error message contains "Failed to list databases"

  Scenario: Method is unit-testable via SQLite mock
    Given a mock engine that returns rows [("mydb",), ("information_schema",)]
    When list_databases(engine) is called with the mock
    Then the return value is ["mydb"]
    And "information_schema" is filtered out

  Scenario: Method signature and docstring comply with project standards
    Given the implemented method
    Then it has full type hints: (engine: Engine) -> list[str]
    And a Google-style docstring with Args, Returns, and Raises sections
    And "from __future__ import annotations" is at the top of the module
```

## Technical Notes

Implementation to add to `src/services/db_connector.py`:

```python
_SYSTEM_DATABASES: frozenset[str] = frozenset(
    {"information_schema", "performance_schema", "mysql", "sys"}
)

def list_databases(self, engine: Engine) -> list[str]:
    """Return non-system database names visible to the connected MySQL user.

    Executes ``SHOW DATABASES`` and filters out the four MySQL system schemas.

    Args:
        engine: A connected SQLAlchemy engine (server-level, no database selected).

    Returns:
        Sorted list of user-accessible database names, excluding system databases.

    Raises:
        DatabaseConnectionError: If the query fails due to a connection or
            permission error.
    """
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("SHOW DATABASES")).fetchall()
    except SQLAlchemyError as exc:
        raise DatabaseConnectionError(
            f"Failed to list databases: {exc}"
        ) from exc
    return sorted(
        row[0] for row in rows if row[0] not in _SYSTEM_DATABASES
    )
```

- Unit tests in `tests/unit/test_db_connector.py` (new file) using a mock engine
- Existing integration tests in `tests/integration/test_db_connector.py` remain
  unchanged (SQLite doesn't support `SHOW DATABASES`; mock used in unit tests)

## Definition of Done
- [x] `src/services/db_connector.py` — `list_databases()` implemented
- [x] `tests/unit/test_db_connector.py` — unit tests covering all AC scenarios
- [x] 100% branch coverage on `list_databases()`
- [x] `ruff` and `mypy` clean on both source and test file
- [x] Code review approved

## Status
✅ Done
