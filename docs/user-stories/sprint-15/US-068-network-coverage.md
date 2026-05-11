# US-068 — Increase `utils/network.py` Unit Coverage

**Epic**: EPIC-012 — Coverage Completeness & CI Hardening
**Sprint**: 15
**Points**: 1
**Priority**: Low
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** `utils/network.py` to have 100% unit test coverage,
> **so that** the WSL2 error branch is exercised offline.

---

## Background

`utils/network.py` sits at 97% with line 77 (WSL2 helper error branch) uncovered.

---

## Acceptance Criteria

- [x] New unit test covers line 77 error branch via mock
- [x] `utils/network.py` coverage = 100% in `pytest tests/unit` run → **100%**
- [x] No live network required
- [x] All existing tests continue to pass

---

## Definition of Done

- [x] Code implemented (`tests/unit/test_network_extended.py`)
- [x] Unit tests written and passing (3/3)
- [x] UTR document created (UTR-012)
- [x] Code review approved (CR-015)
