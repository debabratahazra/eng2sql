# US-067 — Increase `models/config.py` Unit Coverage

**Epic**: EPIC-012 — Coverage Completeness & CI Hardening
**Sprint**: 15
**Points**: 2
**Priority**: Low
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** `models/config.py` to have ≥ 99% unit test coverage,
> **so that** config validation branches are exercised in the offline unit suite.

---

## Background

`models/config.py` sits at 97% with lines 79, 177–178 uncovered. These are validation
branches in `DBConfig` and related dataclasses.

---

## Acceptance Criteria

- [x] New unit tests cover lines 79, 177–178
- [x] `models/config.py` coverage ≥ 99% in `pytest tests/unit` run → **100%**
- [x] No live DB required
- [x] All existing 264+ unit tests continue to pass

---

## Definition of Done

- [x] Code implemented (`tests/unit/test_config_extended.py`)
- [x] Unit tests written and passing (9/9)
- [x] UTR document created (UTR-011)
- [x] Code review approved (CR-015)
