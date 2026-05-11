# US-063 — Add `testcontainers[mongo]` to Dev Dependencies

**Epic**: EPIC-011 — Dependency Hygiene & Coverage Uplift
**Sprint**: 14
**Points**: 1
**Priority**: High (blocks CI Docker integration tests)
**Status**: ✅ Done

---

## User Story

> **As a** CI/CD pipeline,
> **I want** `testcontainers[mongo]` to be declared in dev dependencies,
> **so that** the `test_mongo_query_executor_integration.py` Docker tests can import and
> run without missing-package errors on any developer machine or CI runner.

---

## Acceptance Criteria

- [ ] `pyproject.toml` `[project.optional-dependencies].dev` includes `testcontainers[mongo]>=4.7.0`
- [ ] `requirements.txt` includes `testcontainers[mongo]>=4.7.0` (alongside the existing `testcontainers` entries)
- [ ] `pip install -e ".[dev,db]"` succeeds after the change
- [ ] Running `pytest tests/integration/test_mongo_query_executor_integration.py -m docker -v` no longer produces `ModuleNotFoundError` (skips cleanly or runs if Docker available)

---

## Definition of Done

- [x] Code implemented (pyproject.toml + requirements.txt updated)
- [x] Unit tests written and passing (no new unit tests needed — config change only)
- [x] Code review approved
- [x] No new failing tests
- [x] Docs updated if setup instructions changed
