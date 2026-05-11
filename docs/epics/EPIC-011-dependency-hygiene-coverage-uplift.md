# EPIC-011 — Dependency Hygiene & Coverage Uplift

**ID**: EPIC-011
**Created**: 2026-05-07 (seeded by Retro Analyzer from SPRINT-13-retro.md)
**Status**: 🟡 Planned (Sprint 14)

---

## Goal

Ensure all developer tooling dependencies are consistently declared across `pyproject.toml`
and `requirements.txt`, and raise unit-test coverage on pre-existing services that are
currently below the 90% new-module target.

---

## Problem Statement

Sprint 13 revealed two systemic gaps:

1. `testcontainers[mongo]` is missing from `[project.optional-dependencies].dev` in
   `pyproject.toml`. The Docker integration test for `MongoQueryExecutor` will fail at
   import in any CI pipeline until this is fixed.

2. `schema_detector.py` (62%) and `db_connector.py` (67%) have been below the 90%
   individual-module target for several sprints. They are covered only by integration tests
   (which require a live DB or Docker) and are excluded from the standard `pytest` run.
   Adding targeted unit mocks will make these modules fully exercisable offline.

---

## Acceptance Outcomes

1. `pyproject.toml` `[project.optional-dependencies].dev` includes `testcontainers[mongo]>=4.7.0`.
2. `requirements.txt` documents the `testcontainers[mongo]` requirement (dev comment).
3. `schema_detector.py` unit coverage ≥ 80% when run with standard `-m 'not integration'`.
4. `db_connector.py` unit coverage ≥ 75% when run with standard `-m 'not integration'`.
5. Overall coverage gate remains ≥ 80% (currently 91.55%).
6. All 240+ unit tests continue to pass.

---

## Out of Scope

- Adding new features to `schema_detector.py` or `db_connector.py`.
- Changing `requirements.txt` structure (pin format must be preserved).

---

## Related Stories

- US-063 — Add `testcontainers[mongo]` to dev dependencies
- US-064 — Increase `schema_detector.py` unit coverage to ≥ 80%
- US-065 — Increase `db_connector.py` unit coverage to ≥ 75%
