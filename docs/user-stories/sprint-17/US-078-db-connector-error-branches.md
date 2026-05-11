# US-078 — Cover Error Branches in db_connector.py

**Epic**: EPIC-014 — Component Coverage Completion  
**Sprint**: 17  
**Points**: 3  
**Priority**: Medium  
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** unit tests covering the remaining error-handling branches in
> `src/services/db_connector.py`,
> **so that** connection failure paths are verified and coverage on that module reaches 100%.

---

## Background

`src/services/db_connector.py` currently has good coverage but several `except` clauses
for `OperationalError`, `ProgrammingError`, and `SQLAlchemyError` are hit only with a
live database.  These should be exercised with mocked engine objects.

---

## Acceptance Criteria

- [x] `OperationalError` branch in `list_databases()` tested with a mocked engine
- [x] `ProgrammingError` branch in `execute_query()` tested with a mocked connection
- [x] `db_connector.py` coverage reaches 100%
- [x] No new integration tests required (all unit-testable via mocks)

---

## Definition of Done

- [ ] Code implemented (`tests/unit/test_db_connector_errors.py` or added to existing file)
- [ ] Unit tests written and passing
- [ ] UTR document created
- [ ] Code review approved
