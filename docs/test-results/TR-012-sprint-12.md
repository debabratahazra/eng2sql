# TR-012 — Sprint 12 Tester Run Results

**Sprint**: 12
**Date**: 2026-05-07
**Agent**: Tester
**Phase**: 8

---

## Execution Command

```bash
python -m pytest tests/unit -q --cov=src --cov-report=term-missing
```

---

## Summary

| Metric               | Value                 |
| -------------------- | --------------------- |
| Platform             | win32 — Python 3.14.3 |
| pytest               | 9.0.2                 |
| Collected            | 238                   |
| Deselected (markers) | 4                     |
| **Passed**           | **234 ✅**             |
| Failed               | 0                     |
| Errors               | 0                     |
| Duration             | 78.01 s               |
| **Total coverage**   | **91.55 %**           |
| Coverage gate (80 %) | ✅ PASSED              |

---

## Per-Module Coverage

| Module                                  | Stmts | Miss | Cover     | Notes                              |
| --------------------------------------- | ----- | ---- | --------- | ---------------------------------- |
| `src/models/__init__.py`                | 0     | 0    | 100 %     |                                    |
| `src/models/config.py`                  | 97    | 3    | 97 %      | Lines 79, 177–178                  |
| `src/services/__init__.py`              | 0     | 0    | 100 %     |                                    |
| `src/services/db_connector.py`          | 57    | 19   | 67 %      | Real-DB paths (integration)        |
| `src/services/mongo_connector.py`       | 145   | 7    | 95 %      | Lines 14–15, 232, 341–342, 351–352 |
| `src/services/mongo_query_executor.py`  | 61    | 0    | **100 %** | Sprint 12 new module               |
| `src/services/mongo_schema_detector.py` | 43    | 0    | **100 %** | Sprint 11 module                   |
| `src/services/schema_detector.py`       | 48    | 18   | 62 %      | Real-DB paths (integration)        |
| `src/services/sql_generator.py`         | 58    | 0    | **100 %** | Sprint 12 modified                 |
| `src/utils/__init__.py`                 | 0     | 0    | 100 %     |                                    |
| `src/utils/exceptions.py`               | 7     | 0    | 100 %     |                                    |
| `src/utils/logger.py`                   | 15    | 0    | 100 %     |                                    |
| `src/utils/network.py`                  | 37    | 1    | 97 %      | Line 77                            |

**Total**: 568 stmts / 48 miss / **91.55 %**

---

## Sprint 12 New Module Coverage Gate

| Module                        | Required | Actual | Status |
| ----------------------------- | -------- | ------ | ------ |
| `mongo_query_executor.py`     | ≥ 90 %   | 100 %  | ✅      |
| `sql_generator.py` (modified) | ≥ 90 %   | 100 %  | ✅      |

---

## Test File Breakdown

| Test File                              | Tests   | Passed  |
| -------------------------------------- | ------- | ------- |
| `test_config_postgresql.py`            | 9       | 9       |
| `test_db_connector.py`                 | 8       | 8       |
| `test_db_connector_postgresql.py`      | 3       | 3       |
| `test_db_connector_postgresql_unit.py` | 6       | 6       |
| `test_mongo_connector.py`              | 64      | 64      |
| `test_mongo_query_executor.py`         | 30      | 30      |
| `test_mongo_schema_detector.py`        | 27      | 27      |
| `test_network.py`                      | 12      | 12      |
| `test_schema_detector.py`              | 7       | 7       |
| `test_sidebar_postgresql.py`           | 7       | 7       |
| `test_sidebar_sprint11.py`             | 8       | 8       |
| `test_sidebar_step2.py`                | 8       | 8       |
| `test_sidebar_ui.py`                   | 10      | 10      |
| `test_sql_generator.py`                | 22      | 22      |
| `test_sql_generator_postgresql.py`     | 2       | 2       |
| `test_sql_output_label.py`             | 9       | 9       |
| **TOTAL**                              | **234** | **234** |

---

## Result: ✅ PASSED — Sprint 12 quality gate satisfied
