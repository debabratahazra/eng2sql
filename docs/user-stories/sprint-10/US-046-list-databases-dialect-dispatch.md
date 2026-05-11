# US-046: `DBConnector.list_databases` Dialect Dispatch for PostgreSQL

**Epic**: EPIC-009 — PostgreSQL Live Connection Support
**Sprint**: Sprint 10
**Points**: 2
**Priority**: Must Have
**Source**: PostgreSQL evaluation §3 (US-C) — promoted by Retro Analyzer

## User Story

> As a **developer**, I want `DBConnector.list_databases(engine)` to dispatch on the
> SQLAlchemy dialect name so that a single method call works for both MySQL and
> PostgreSQL engines without callers needing to know the dialect.

## Acceptance Criteria

```gherkin
Feature: list_databases dialect dispatch

  Scenario: MySQL engine still uses SHOW DATABASES (backward compatibility)
    Given an engine with engine.dialect.name == "mysql"
    When list_databases(engine) is called
    Then "SHOW DATABASES" is executed
    And system DBs ("mysql", "information_schema", "performance_schema", "sys") are filtered

  Scenario: PostgreSQL engine uses pg_database query
    Given an engine with engine.dialect.name == "postgresql"
    When list_databases(engine) is called
    Then "SELECT datname FROM pg_database WHERE datistemplate = false" is executed
    And system DBs ("postgres", "template0", "template1") are filtered

  Scenario: Unknown dialect raises clear error
    Given an engine with engine.dialect.name == "sqlite"
    When list_databases(engine) is called
    Then a NotImplementedError or DatabaseConnectionError is raised mentioning "sqlite"

  Scenario: WSL2 fail-fast pattern reused for PostgreSQL localhost
    Given dialect="postgresql", host="localhost" on a WSL2 host with no PostgreSQL listening
    When create_engine + test_connection is called
    Then DatabaseConnectionError is raised within ~1 second
    And the message contains a WSL2-specific hint
```

## Technical Notes

- Update `src/services/db_connector.py`:
  - Replace the inline MySQL `SHOW DATABASES` query with a small dispatcher:
    ```python
    _LIST_DB_QUERIES = {
        "mysql": "SHOW DATABASES",
        "postgresql": "SELECT datname FROM pg_database WHERE datistemplate = false",
    }
    ```
  - Extend `_SYSTEM_DATABASES` set to include `postgres`, `template0`, `template1`
    (keep existing MySQL entries).
  - Reuse the BUG-006 WSL2 fail-fast logic (currently only in `mongo_connector.py`)
    by extracting it into `src/utils/network.py` and calling from both connectors.
- Update unit tests in `tests/unit/test_db_connector.py` with both dialects mocked.

## Definition of Done

- [x] `_LIST_DB_QUERIES` dispatcher added
- [x] `_SYSTEM_DATABASES` extended with PostgreSQL system DBs
- [x] WSL2 fail-fast pattern extracted to `src/utils/network.py` and reused
- [x] Unit tests in `tests/unit/test_db_connector.py` cover both dialect branches
- [x] Unit test for unknown dialect error path
- [x] Existing MySQL tests still pass
- [x] Code review CR-010 approved
- [x] Coverage on `db_connector.py` ≥ 85 % (unit-only); ≥ 95 % with US-048 Docker tests

## Status

✅ Done
