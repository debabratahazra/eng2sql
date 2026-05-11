# STR-005 — Sprint 14 Smoke Test Results

**Date**: 2025-07-25
**Sprint**: 14
**Agent**: Smoke Test Agent
**Status**: ✅ PASSED

---

## Execution

```powershell
python -m pytest tests/smoke/test_sprint_14_smoke.py -v --tb=short -m "smoke"
```

---

## Results

| Metric            | Value   |
| ----------------- | ------- |
| Total smoke tests | 12      |
| Passed            | 12      |
| Failed            | 0       |
| Duration          | 14.46 s |

---

## Test-by-Test Results

| Test                                                             | US         | Result |
| ---------------------------------------------------------------- | ---------- | ------ |
| `test_smoke_s14_testcontainers_importable`                       | US-063     | ✅      |
| `test_smoke_s14_pyproject_declares_testcontainers_mongo`         | US-063     | ✅      |
| `test_smoke_s14_requirements_declares_testcontainers_mongo`      | US-063     | ✅      |
| `test_smoke_s14_app_renders_after_schema_detector_uplift`        | US-064     | ✅      |
| `test_smoke_s14_mysql_schema_detected_in_session_state`          | US-064     | ✅      |
| `test_smoke_s14_schema_detector_module_importable`               | US-064     | ✅      |
| `test_smoke_s14_db_connector_module_importable`                  | US-065     | ✅      |
| `test_smoke_s14_mysql_connect_button_present`                    | US-065     | ✅      |
| `test_smoke_s14_postgresql_connect_button_present`               | US-065     | ✅      |
| `test_smoke_s14_all_three_db_types_in_radio`                     | Regression | ✅      |
| `test_smoke_s14_execute_mql_button_present_when_mongo_connected` | Regression | ✅      |
| `test_smoke_s14_sql_generation_pipeline_mysql`                   | Regression | ✅      |

---

## Coverage Areas

| Area                                           | Status |
| ---------------------------------------------- | ------ |
| testcontainers[mongo] installed and declared   | ✅      |
| schema_detector importable (no regressions)    | ✅      |
| db_connector importable (no regressions)       | ✅      |
| All 3 DB types in sidebar radio                | ✅      |
| MySQL connect button present                   | ✅      |
| PostgreSQL connect button present              | ✅      |
| Execute MQL button present (mongo_execute key) | ✅      |
| App launches without exception                 | ✅      |

---

## Summary

All 12 Sprint 14 smoke tests pass. The dependency addition (US-063) is confirmed
installed. The schema_detector and db_connector modules are importable and the app
renders correctly with all three DB types. No regressions detected.
