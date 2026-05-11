# US-055 — Unit-mock coverage lift for `db_connector.py` PostgreSQL branches

**Sprint**: Sprint 11
**Source**: SPRINT-10-retro.md "What Could Be Improved" §7
**Points**: 2
**Owner**: Tester / Developer

## User Story

As a **CI maintainer running without Docker**, I want unit-level mocks covering the
PostgreSQL engine-creation, list-databases dispatch, and dialect-filter branches in
`src/services/db_connector.py` so coverage on that file rises from **80 % → ≥ 90 %**
without depending on Docker tests being available.

## Acceptance Criteria

1. New tests in `tests/unit/test_db_connector.py` (or a new
   `test_db_connector_postgresql_unit.py`) using `unittest.mock.patch` to cover:
   - `create_engine` happy path with `dialect="postgresql"` and sslmode propagation
   - `list_databases` PostgreSQL dispatch (mock `engine.dialect.name = "postgresql"`,
     verify the `pg_database` query is executed)
   - `_SYSTEM_DATABASES` filter excludes `postgres`, `template0`, `template1`
2. Coverage on `src/services/db_connector.py` reported by `pytest --cov` ≥ 90 % even
   when Docker tests are skipped.
3. No live PostgreSQL connection required (pure mocks).

## Definition of Done

- [x] At least 4 new unit tests added
- [x] `db_connector.py` coverage ≥ 90 % without Docker
- [x] All existing tests still pass
- [x] Test results captured in TR-011

## Status

✅ Done
