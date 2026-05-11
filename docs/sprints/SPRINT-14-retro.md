# Sprint 14 Retrospective

**Sprint**: 14
**Date**: 2025-07-25
**Facilitator**: Retro Analyzer Agent
**Velocity**: 7 / 7 pts (100%)

---

## Sprint Goal

> Bring `schema_detector.py` and `db_connector.py` to ≥ 80% / ≥ 75% offline unit coverage
> and declare `testcontainers[mongo]` in dev dependencies.

**Outcome**: ✅ Achieved — both modules reach 100% coverage; overall project at 98.06%.

---

## Sprint Board

| Story  | Title                                   | Pts | Status |
| ------ | --------------------------------------- | --- | ------ |
| US-063 | Add `testcontainers[mongo]` to dev deps | 1   | ✅ Done |
| US-064 | `schema_detector.py` coverage uplift    | 3   | ✅ Done |
| US-065 | `db_connector.py` coverage uplift       | 3   | ✅ Done |

---

## What Went Well

- **Zero live-DB dependency**: All new tests run offline via `unittest.mock.patch`,
  making the unit suite completely self-contained.
- **100% coverage on both targets**: Both `schema_detector.py` and `db_connector.py`
  exceeded their targets (80%/75%) by reaching 100%.
- **Overall coverage 98.06%**: Highest sprint-end coverage to date.
- **Mock patterns documented**: `patch("services.schema_detector.inspect", ...)` and
  `patch("services.db_connector.create_engine", ...)` patterns are now proven reference
  implementations for future test authors.
- **testcontainers[mongo] unblocked**: Sprint 13 MongoDB Docker integration test
  (`US-061`) can now run without `ModuleNotFoundError` on any developer machine.
- **Smoke suite passes cleanly**: 12/12 smoke tests pass, confirming no regressions.

---

## What Could Be Improved

- **`app.py` has zero direct unit tests**: The Streamlit app entry point is only
  exercised via AppTest smoke/integration tests. Component-level unit tests for
  `src/components/` functions would isolate failures more precisely.
- **`mongo_connector.py` at 95% (7 lines uncovered)**: Lines 14–15, 232, 341–342,
  351–352 remain uncovered. These appear to be import-time fallback paths and rarely
  exercised error branches.
- **`models/config.py` at 97%**: Lines 79, 177–178 remain uncovered — validation
  branches not yet exercised in unit tests.
- **`utils/network.py` at 97%**: Line 77 (WSL2 helper error branch) uncovered.
- **CI matrix still deferred**: The `coverage-docker` CI matrix job (US-053) was
  planned but not yet verified end-to-end with GitHub Actions.

---

## Action Items (seeds for Sprint 15)

| #    | Action                                                                   | Priority | Type  |
| ---- | ------------------------------------------------------------------------ | -------- | ----- |
| AI-1 | Write unit tests for `mongo_connector.py` uncovered lines (232, 341–352) | Medium   | Story |
| AI-2 | Write unit tests for `models/config.py` lines 79, 177–178                | Low      | Story |
| AI-3 | Write unit tests for `utils/network.py` line 77 error branch             | Low      | Story |
| AI-4 | Add component-level unit tests for `src/components/sidebar.py`           | Medium   | Story |
| AI-5 | Verify CI `coverage-docker` matrix job runs correctly on GitHub Actions  | High     | Story |

---

## Metrics

| Metric               | Sprint 13 | Sprint 14 | Δ    |
| -------------------- | --------- | --------- | ---- |
| Unit tests           | 240       | 264       | +24  |
| Overall coverage     | ~97%      | 98.06%    | +~1% |
| `schema_detector.py` | 62%       | 100%      | +38% |
| `db_connector.py`    | 67%       | 100%      | +33% |
| Smoke tests          | 10        | 12        | +2   |
| Velocity             | 10/10     | 7/7       | 100% |

---

## Next Sprint

**Sprint 15** — Coverage completeness: `mongo_connector.py`, `config.py`, sidebar
component tests, and CI matrix verification.

**Next Agent**: Orchestrator → Sprint 15 planning (Scrum Master)
