# US-066 — Increase `mongo_connector.py` Unit Coverage

**Epic**: EPIC-012 — Coverage Completeness & CI Hardening
**Sprint**: 15
**Points**: 3
**Priority**: Medium
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** `mongo_connector.py` to have ≥ 90% unit test coverage,
> **so that** import-time fallback paths and error branches are exercisable offline.

---

## Background

`mongo_connector.py` sits at 95% coverage with lines 14–15, 232, 341–342, 351–352
uncovered. These are import-time fallback branches and error-handling paths.

---

## Acceptance Criteria

- [x] New unit tests use mocks to cover lines 14–15, 232, 341–342, 351–352
- [x] `mongo_connector.py` coverage ≥ 90% in `pytest tests/unit` run → **100%**
- [x] No live MongoDB required
- [x] All existing 264+ unit tests continue to pass

---

## Definition of Done

- [x] Code implemented (`tests/unit/test_mongo_connector_extended.py`)
- [x] Unit tests written and passing (6/6)
- [x] UTR document created (UTR-010)
- [x] Code review approved (CR-015)
