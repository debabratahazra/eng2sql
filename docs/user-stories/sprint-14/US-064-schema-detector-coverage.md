# US-064 — Increase `schema_detector.py` Unit Coverage to ≥ 80%

**Epic**: EPIC-011 — Dependency Hygiene & Coverage Uplift
**Sprint**: 14
**Points**: 3
**Priority**: Medium
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** `schema_detector.py` to have ≥ 80% unit test coverage (no live DB needed),
> **so that** schema detection logic is exercisable offline and regressions are caught
> without requiring a MySQL or PostgreSQL instance.

---

## Background

`schema_detector.py` currently sits at 62% unit coverage (line 71 and lines 104–140 are
uncovered). These lines contain the SQLAlchemy `inspect()` call paths and error handling.
The existing integration tests cover these paths with a live DB, but they do not run in
the standard `pytest -m 'not integration'` unit suite.

---

## Acceptance Criteria

- [ ] New unit tests use `unittest.mock.patch` to mock `sqlalchemy.inspect()` return values
- [ ] Lines 71, 104–140 in `schema_detector.py` are covered in unit mode
- [ ] `schema_detector.py` coverage ≥ 80% in `pytest tests/unit` run
- [ ] No live database connection required to run the new tests
- [ ] All existing 240+ unit tests continue to pass
- [ ] Overall project coverage remains ≥ 80%

---

## Definition of Done

- [x] Code implemented (new test file `tests/unit/test_schema_detector_extended.py`)
- [x] Unit tests written and passing (coverage gate met — 100%)
- [x] UTR document created
- [x] Code review approved
- [x] Docs updated if needed
