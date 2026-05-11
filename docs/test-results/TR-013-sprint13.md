# TR-013 — Sprint 13 Full Test Run Results

**Date**: 2026-05-07
**Sprint**: 13
**Agent**: Tester
**Test Runner**: pytest 9.0.2 / pytest-cov 7.0.0
**Python**: 3.14.3

---

## Summary

| Metric                                 | Value                       |
| -------------------------------------- | --------------------------- |
| Total unit tests                       | **240**                     |
| Passed                                 | **240**                     |
| Failed                                 | 0                           |
| Deselected (integration/smoke markers) | 4                           |
| Coverage (overall)                     | **91.55%**                  |
| Coverage gate                          | 80% — ✅ PASSED              |
| Smoke tests (Sprint 13)                | **10 / 10**                 |
| Integration tests                      | 7 skip (Docker unavailable) |

**Verdict**: ✅ All gates passed — Sprint 13 approved for retro.

---

## Unit Test Run

**Command**:
```
python -m pytest tests/unit --cov=src --cov-report=term-missing -q --tb=short
```

**Result**: 240 passed, 4 deselected in 74.53s

### Coverage Report

| Module                                  | Stmts   | Miss   | Cover      | Missing Lines                |
| --------------------------------------- | ------- | ------ | ---------- | ---------------------------- |
| `src/models/__init__.py`                | 0       | 0      | 100%       | —                            |
| `src/models/config.py`                  | 97      | 3      | 97%        | 79, 177–178                  |
| `src/services/__init__.py`              | 0       | 0      | 100%       | —                            |
| `src/services/db_connector.py`          | 57      | 19     | 67%        | 84, 88, 110–115, 133–147     |
| `src/services/mongo_connector.py`       | 145     | 7      | 95%        | 14–15, 232, 341–342, 351–352 |
| `src/services/mongo_query_executor.py`  | 61      | 0      | **100%**   | —                            |
| `src/services/mongo_schema_detector.py` | 43      | 0      | **100%**   | —                            |
| `src/services/schema_detector.py`       | 48      | 18     | 62%        | 71, 104–140                  |
| `src/services/sql_generator.py`         | 58      | 0      | **100%**   | —                            |
| `src/utils/__init__.py`                 | 0       | 0      | 100%       | —                            |
| `src/utils/exceptions.py`               | 7       | 0      | **100%**   | —                            |
| `src/utils/logger.py`                   | 15      | 0      | **100%**   | —                            |
| `src/utils/network.py`                  | 37      | 1      | 97%        | 77                           |
| **TOTAL**                               | **568** | **48** | **91.55%** | —                            |

> **Note**: `db_connector.py` (67%) and `schema_detector.py` (62%) are below the 90% target
> for new modules but were not added this sprint; they are pre-existing modules. Overall gate
> of 80% is met. No new Sprint 13 modules fall below 90%.

---

## Smoke Test Run (Sprint 13)

**Command**:
```
python -m pytest tests/smoke/test_sprint_13_smoke.py -m smoke -v
```

**Result**: 10 passed in 18.66s

| Test                                                             | Result |
| ---------------------------------------------------------------- | ------ |
| `test_smoke_s13_mysql_step1_renders_after_refactor`              | ✅ PASS |
| `test_smoke_s13_postgresql_step1_renders_after_refactor`         | ✅ PASS |
| `test_smoke_s13_mysql_step2_renders_with_seeded_state`           | ✅ PASS |
| `test_smoke_s13_postgresql_step2_renders_with_seeded_state`      | ✅ PASS |
| `test_smoke_s13_admin_db_field_renders_for_postgresql`           | ✅ PASS |
| `test_smoke_s13_execute_mql_button_present_when_mongo_connected` | ✅ PASS |
| `test_smoke_s13_execute_mql_info_when_no_db_connected`           | ✅ PASS |
| `test_smoke_s13_execute_mql_success_click`                       | ✅ PASS |
| `test_smoke_s13_app_launches_without_error`                      | ✅ PASS |
| `test_smoke_s13_db_type_radio_has_all_three_options`             | ✅ PASS |

---

## Integration Tests (skipped — Docker unavailable)

7 Docker integration tests in `tests/integration/test_mongo_query_executor_integration.py`
skip cleanly with `@pytest.mark.docker` and `@pytest.mark.integration` markers.

Full details in **ITR-005**.

---

## Known Coverage Gaps (pre-existing)

| Module               | Cover | Reason                                                          |
| -------------------- | ----- | --------------------------------------------------------------- |
| `db_connector.py`    | 67%   | Live MySQL/PostgreSQL connections; tested via integration suite |
| `schema_detector.py` | 62%   | Live DB introspection paths; SQLAlchemy `inspect()` calls       |

These modules have not changed in Sprint 13 and are covered by integration tests in CI.

---

## Next Agent

**Smoke Test Agent** → create STR-004 (completed inline with this run).
**Retro Analyzer** → create SPRINT-13-retro.md.
