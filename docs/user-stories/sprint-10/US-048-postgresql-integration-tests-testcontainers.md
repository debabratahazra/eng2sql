# US-048: PostgreSQL Integration Tests with testcontainers Fixture

**Epic**: EPIC-009 — PostgreSQL Live Connection Support
**Sprint**: Sprint 10
**Points**: 3
**Priority**: Should Have
**Source**: PostgreSQL evaluation §3 (US-E) — promoted by Retro Analyzer; reuses US-042 pattern

## User Story

> As a **developer**, I want a Docker-based PostgreSQL integration fixture mirroring the
> Sprint 9 `mysql_container` fixture, so that the live PostgreSQL connection branches in
> `db_connector.py` are exercised against a real PostgreSQL 16 container while still
> skipping cleanly on hosts without Docker.

## Acceptance Criteria

```gherkin
Feature: Docker PostgreSQL fixture for integration tests

  Scenario: Fixture starts a PostgreSQL container
    Given Docker is available on the host
    When the postgres_container fixture is requested
    Then a PostgreSQL 16 container is running on a dynamic port
    And a DBConfig (dialect="postgresql") pointing at it is yielded
    And the container is stopped after the session

  Scenario: Fixture skips gracefully when Docker is unavailable
    Given Docker is not running on the host
    When the postgres_container fixture is requested
    Then pytest.skip is called with a clear message
    And no exception propagates

  Scenario: DBConnector.create_engine works against real PostgreSQL
    Given the postgres_container fixture is active
    When DBConnector.create_engine(config) is called
    Then an Engine is returned
    And test_connection(engine) returns True

  Scenario: DBConnector.list_databases returns user databases (PostgreSQL)
    Given an active live PostgreSQL engine
    When list_databases is called
    Then "testdb" is in the result
    And "template0", "template1" are NOT in the result

  Scenario: DBConnector.execute_query returns a DataFrame from PostgreSQL
    Given an active live PostgreSQL engine
    When execute_query(engine, "SELECT 1 AS one, 2 AS two") is called
    Then a 1x2 DataFrame is returned

  Scenario: Bad credentials raise DatabaseConnectionError
    Given the live container's host/port but a bogus user
    When create_engine + test_connection is called
    Then DatabaseConnectionError is raised
```

## Technical Notes

- Add `testcontainers[postgres]>=4.7.0` to dev dependencies in `requirements.txt`.
- Add `postgres_container` session-scoped fixture in `tests/conftest.py`:
  - Image: `postgres:16-alpine`
  - Env: `POSTGRES_USER=testroot`, `POSTGRES_PASSWORD=testroot`, `POSTGRES_DB=testdb`
  - Two-level skip: ImportError → skip; DockerException → skip with message
- Create `tests/integration/test_db_connector_postgres_live.py`:
  - `pytestmark = [pytest.mark.integration, pytest.mark.docker]`
  - 4+ tests mirroring `test_db_connector_live.py` (the MySQL Sprint 9 file)
- Document the new fixture in `docs/guides/developer-guide.md` (alongside the MySQL one).

## Definition of Done

- [x] `testcontainers[postgres]>=4.7.0` added to dev dependencies
- [x] `postgres_container` fixture implemented with graceful skip
- [x] 4+ integration tests added in `tests/integration/test_db_connector_postgres_live.py`
- [x] Tests skip cleanly without Docker (verified locally)
- [x] Code review CR-010 approved
- [x] ITR-002 integration test report authored
- [x] Developer guide updated with fixture usage

## Status

✅ Done
