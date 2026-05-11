# CR-014 — Code Review: Sprint 14 Coverage Uplift (US-063, US-064, US-065)

**Date**: 2025-07-25
**Sprint**: 14
**Reviewer**: Code Reviewer Agent
**Status**: ✅ APPROVED

---

## Scope

This review covers all changes introduced in Sprint 14:

| User Story | Change                                         | Files                                         |
| ---------- | ---------------------------------------------- | --------------------------------------------- |
| US-063     | Add `testcontainers[mongo]>=4.7.0` to dev deps | `pyproject.toml`, `requirements.txt`          |
| US-064     | Mock-based unit tests for `schema_detector.py` | `tests/unit/test_schema_detector_extended.py` |
| US-065     | Mock-based unit tests for `db_connector.py`    | `tests/unit/test_db_connector_extended.py`    |

---

## Review Findings

### US-063 — Dependency Config (`pyproject.toml`, `requirements.txt`)

| Check                      | Result | Notes                                           |
| -------------------------- | ------ | ----------------------------------------------- |
| Correct optional-dep group | ✅      | Added to `[project.optional-dependencies].dev`  |
| Version pin consistent     | ✅      | `>=4.7.0` matches mysql and postgres entries    |
| requirements.txt comment   | ✅      | Comment references US-061/US-063 (Sprint 13/14) |
| No secrets introduced      | ✅      | N/A                                             |

**Verdict**: ✅ APPROVED — no concerns.

---

### US-064 — `tests/unit/test_schema_detector_extended.py`

| Check                                 | Result | Notes                                                             |
| ------------------------------------- | ------ | ----------------------------------------------------------------- |
| `from __future__ import annotations`  | ✅      | Present                                                           |
| Type hints on all functions           | ✅      | `-> None` on all test methods                                     |
| Mock isolation (no live DB)           | ✅      | `patch("services.schema_detector.inspect", ...)`                  |
| `SchemaColumn` objects used correctly | ✅      | `SchemaColumn` dataclass instantiated properly                    |
| Error path coverage                   | ✅      | `get_table_names` and `get_columns` raise `SchemaDetectionError`  |
| Edge cases covered                    | ✅      | Empty DB, multiple tables, PK detection, default values, nullable |
| No hardcoded credentials              | ✅      | No secrets                                                        |
| Test isolation                        | ✅      | Each test sets up its own mock inspector                          |
| Naming convention                     | ✅      | `test_<behaviour>` pattern                                        |

**Verdict**: ✅ APPROVED — comprehensive coverage; clean mock patterns.

---

### US-065 — `tests/unit/test_db_connector_extended.py`

| Check                                | Result | Notes                                                                |
| ------------------------------------ | ------ | -------------------------------------------------------------------- |
| `from __future__ import annotations` | ✅      | Present                                                              |
| Type hints on all functions          | ✅      | `-> None` on all test methods                                        |
| Mock isolation (no live DB)          | ✅      | `patch("services.db_connector.create_engine", ...)`                  |
| OperationalError constructor         | ✅      | `OperationalError("msg", None, None)` — correct SQLAlchemy signature |
| ValueError for non-SELECT            | ✅      | Covers DROP, INSERT branches                                         |
| QueryExecutionError wrapping         | ✅      | Correct exception type from `utils.exceptions`                       |
| DataFrame assertions                 | ✅      | Column names, row counts, cell values verified                       |
| Helper functions                     | ✅      | `_mysql_config()` and `_mock_engine_ok()` avoid duplication          |
| Context manager mocks                | ✅      | `__enter__`/`__exit__` correctly configured                          |
| No hardcoded credentials             | ✅      | Password is `"s3cr3t"` — test-only, not a real secret                |

**Verdict**: ✅ APPROVED — robust exception coverage; correct pandas assertions.

---

## Security Review

- No SQL injected without parameterisation (test-only helper strings, no injection surface)
- No real credentials in test files
- `json.loads()` not touched — MQL executor unchanged
- OWASP Top 10: N/A for mock-only test files

---

## Quality Metrics

| Metric                        | Sprint 14 Result |
| ----------------------------- | ---------------- |
| Unit tests added              | 24 (12 + 12)     |
| `schema_detector.py` coverage | 100%             |
| `db_connector.py` coverage    | 100%             |
| Overall coverage              | 98.06%           |
| Total unit tests              | 264 passing      |
| Failing tests                 | 0                |

---

## Summary

All Sprint 14 changes are **APPROVED**. The dependency addition is clean and consistent.
Both new test files follow project conventions (type hints, Google-style docstrings,
mock isolation), achieve 100% coverage on their target modules, and introduce no regressions.

**Next Agent**: Test Case Writer (TC-076+)
