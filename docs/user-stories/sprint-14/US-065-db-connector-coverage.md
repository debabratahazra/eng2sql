# US-065 — Increase `db_connector.py` Unit Coverage to ≥ 75%

**Epic**: EPIC-011 — Dependency Hygiene & Coverage Uplift
**Sprint**: 14
**Points**: 3
**Priority**: Medium
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** `db_connector.py` to have ≥ 75% unit test coverage (no live DB needed),
> **so that** connection logic, error handling, and engine creation branches are
> exercisable offline and regressions surface in the standard unit test run.

---

## Background

`db_connector.py` currently sits at 67% unit coverage. Lines 84, 88, 110–115, and 133–147
are uncovered. These include the SQLAlchemy engine connection paths and exception handling
branches. The existing integration tests cover these with a live DB, but they do not run
in the standard `pytest -m 'not integration'` unit suite.

---

## Acceptance Criteria

- [ ] New unit tests use `unittest.mock.patch` to mock `sqlalchemy.create_engine()` and connection calls
- [ ] Lines 84, 88, 110–115, 133–147 in `db_connector.py` are covered (or reduced by ≥ 50%)
- [ ] `db_connector.py` coverage ≥ 75% in `pytest tests/unit` run
- [ ] No live database connection required to run the new tests
- [ ] All existing 240+ unit tests continue to pass
- [ ] Overall project coverage remains ≥ 80%

---

## Definition of Done

- [x] Code implemented (new test file `tests/unit/test_db_connector_extended.py`)
- [x] Unit tests written and passing (coverage = 100%)
- [x] UTR document created
- [x] Code review approved
- [x] Docs updated if needed
