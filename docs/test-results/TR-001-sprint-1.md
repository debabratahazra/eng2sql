# Test Results TR-001 — Sprint 1

**Date**: 2026-05-01
**Branch**: main
**Python**: 3.14.3
**pytest**: 9.0.2
**Tester Agent**: Tester

---

## Summary

| Category    | Total  | Passed | Failed | Skipped | Warnings |
| ----------- | ------ | ------ | ------ | ------- | -------- |
| Unit        | 31     | 31     | 0      | 0       | 1        |
| Integration | 7      | 7      | 0      | 0       | 0        |
| **TOTAL**   | **38** | **38** | **0**  | **0**   | **1**    |

**Coverage (unit only)**: 38% ❌ (target: ≥ 80%)
**Coverage (unit + integration)**: 45% ❌ (target: ≥ 80%)

> The coverage gate (`--cov-fail-under=80`) fails when running unit tests alone
> because `db_connector.py` is only exercised by integration tests. Running the
> full suite (`tests/`) brings `db_connector.py` to 74% but the Streamlit
> `app.py` and all five `components/` modules remain at 0%, dragging the total to
> 45%. See BUG-001 for the formal report.

---

## Failed Tests

_No test failures._ All 38 tests passed.

---

## Warnings

| #   | File                                 | Warning                                                                                                                                                      | Severity |
| --- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| 1   | `tests/unit/test_schema_detector.py` | `ResourceWarning: unclosed database in <sqlite3.Connection>` — SQLite connection not explicitly closed after `sqlite_engine` session-scoped fixture teardown | Low      |

> **Root cause**: The `sqlite_engine` fixture in `conftest.py` uses `scope="session"`
> and creates an in-memory SQLite engine but never calls `engine.dispose()` on
> teardown. Python 3.14 GC emits a `ResourceWarning` when the connection is
> garbage-collected.
>
> **Recommended fix**: Add an explicit `engine.dispose()` teardown to the
> `sqlite_engine` fixture (see BUG-002).

---

## Coverage Report (unit + integration combined)

| Module                               | Stmts   | Missed  | Cover      | Missing Lines                                              |
| ------------------------------------ | ------- | ------- | ---------- | ---------------------------------------------------------- |
| `src/app.py`                         | 89      | 89      | **0%** ❌   | 6–168 (entire file)                                        |
| `src/components/progress_tracker.py` | 15      | 15      | **0%** ❌   | 2–30                                                       |
| `src/components/query_input.py`      | 17      | 17      | **0%** ❌   | 2–37                                                       |
| `src/components/schema_viewer.py`    | 18      | 18      | **0%** ❌   | 2–40                                                       |
| `src/components/sidebar.py`          | 57      | 57      | **0%** ❌   | 2–100                                                      |
| `src/components/sql_output.py`       | 16      | 16      | **0%** ❌   | 2–29                                                       |
| `src/models/config.py`               | 42      | 4       | 90% ✅      | 22, 28, 46–47 (`__repr__` branches)                        |
| `src/services/db_connector.py`       | 39      | 10      | 74% ⚠️      | 33–60 (`create_engine` success + `SQLAlchemyError` branch) |
| `src/services/schema_detector.py`    | 48      | 5       | 90% ✅      | 71, 107–108, 118–119                                       |
| `src/services/sql_generator.py`      | 57      | 0       | **100%** ✅ | —                                                          |
| `src/utils/exceptions.py`            | 7       | 0       | **100%** ✅ | —                                                          |
| `src/utils/logger.py`                | 15      | 0       | **100%** ✅ | —                                                          |
| **TOTAL**                            | **420** | **231** | **45%** ❌  | —                                                          |

---

## Linting Results

> `ruff` is not installed in the active Python 3.14 environment (not in `PATH`).
> `mypy` was not run for the same reason.
> Both tools are listed in `requirements.txt` and should be available in the
> project's virtual environment. Recommend running via:
> ```
> .venv\Scripts\activate
> ruff check src/ tests/
> mypy src/
> ```

---

## Linked Bug Reports

| Bug     | Title                                                       | Severity | Status |
| ------- | ----------------------------------------------------------- | -------- | ------ |
| BUG-001 | Coverage below 80% gate — UI components untested            | High     | 🔴 Open |
| BUG-002 | ResourceWarning: unclosed SQLite connection in test fixture | Low      | 🔴 Open |

---

## Verdict

**Sprint 1 tests: PASS** — all 38 tests pass with zero failures.
**Coverage gate: FAIL** — 45% total (target ≥ 80%).
Streamlit UI components (`app.py`, `components/`) have 0% coverage and account for
the entire shortfall. This requires Streamlit `AppTest` harness tests (Sprint 3 scope).

**Next Agent**: Developer (to fix BUG-002) then Deployment Agent when Sprint 1 stories
are accepted. Coverage gate remediation is tracked in Sprint 3.
