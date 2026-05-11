# UTR-021 — Unit Test Result: US-077 AppTest Fixture Sharing Investigation

**User Story**: US-077 — Investigate AppTest Fixture Sharing  
**Sprint**: 17  
**Date**: 2025-08-01  
**Agent**: Unit Test Agent  
**Status**: ✅ PASSED (investigation complete — not viable for interactive tests)

---

## Summary

Investigated whether Streamlit `AppTest` instances can safely be shared across tests
using module/session-scoped pytest fixtures, with the goal of reducing the ~1–5 s
per-test cold-start overhead.

**Verdict**: Module-scoped fixtures are **NOT safe** for interactive tests (those that
mutate widget state or `session_state`). A limited module-scoped `initial_app_state`
fixture was added to `tests/conftest.py` for read-only initial-state checks only.

---

## Investigation Test File

`tests/unit/test_apptest_fixture_investigation.py` — **8 tests**

| Class                                      | Tests | Purpose                                             |
| ------------------------------------------ | ----- | --------------------------------------------------- |
| `TestInitialAppStateFixture`               | 5     | Validate module-scoped read-only fixture            |
| `TestInteractiveTestsRequireFunctionScope` | 2     | Confirm isolation requirement for interactive tests |
| `TestAppTestStartupTiming`                 | 1     | Measure cold-start overhead                         |

---

## Benchmark Results

| Metric                                 | Measurement                  |
| -------------------------------------- | ---------------------------- |
| AppTest cold-start range               | 1.0 – 4.7 s per test         |
| Smoke suite total (71 tests)           | 44.6 s                       |
| Unit suite total (352 tests)           | ~116 s                       |
| Savings from module-scoped (read-only) | ~1–5 s per module (marginal) |

---

## Finding: Why Module Scope Is Unsafe for Interactive Tests

`AppTest` instances are **stateful** — `session_state` and widget state persist between
`at.run()` calls on the same instance. When a test calls
`at.radio[0].set_value("MongoDB")`, the next test on the same instance sees
`db_type = "MongoDB"` instead of the default `"MySQL"`. This causes order-dependent
test failures — the worst category of test flakiness.

With pytest-xdist `-n auto`, tests within a module run sequentially on one worker
(each file is assigned to one worker). This means module-scoped fixtures don't introduce
cross-worker races. However, the in-module ordering risk remains: test B fails if it
depends on clean state that test A dirtied.

---

## Deliverables

1. **`tests/conftest.py`**: Added `initial_app_state` module-scoped fixture (read-only).
2. **`tests/unit/test_apptest_fixture_investigation.py`**: 8 verification/benchmark tests.
3. **`docs/guides/developer-guide.md`**: "AppTest Fixture Scoping" section added.

---

## Test Execution

**Command**: `pytest tests/unit/test_apptest_fixture_investigation.py -v --tb=short`  
**Result**: 8 passed — 6.34 s

---

## Recommendation

- **Interactive tests**: always create a fresh `AppTest` per test function.
- **Read-only initial-state checks**: may use `initial_app_state` from `conftest.py`.
- Close story as **"investigated — partial adoption"** (not full refactor, marginal gain).
