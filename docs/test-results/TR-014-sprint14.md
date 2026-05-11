# TR-014 — Sprint 14 Full Test Run Results

**Date**: 2025-07-25
**Sprint**: 14
**Agent**: Tester Agent
**Status**: ✅ PASSED

---

## Test Execution

### Command

```powershell
python -m pytest tests/unit --cov=src --cov-report=term-missing -q --tb=short
```

### Results

| Metric                         | Value   |
| ------------------------------ | ------- |
| Total tests                    | 264     |
| Passed                         | 264     |
| Failed                         | 0       |
| Errors                         | 0       |
| Deselected (integration/smoke) | 4       |
| Duration                       | 83.56 s |
| Python version                 | 3.14.3  |
| pytest version                 | 9.0.2   |

---

## Coverage Report

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src\models\__init__.py                      0      0   100%
src\models\config.py                       97      3    97%   79, 177-178
src\services\__init__.py                    0      0   100%
src\services\db_connector.py               57      0   100%
src\services\mongo_connector.py           145      7    95%   14-15, 232, 341-342, 351-352
src\services\mongo_query_executor.py       61      0   100%
src\services\mongo_schema_detector.py      43      0   100%
src\services\schema_detector.py            48      0   100%
src\services\sql_generator.py              58      0   100%
src\utils\__init__.py                      0      0   100%
src\utils\exceptions.py                    7      0   100%
src\utils\logger.py                       15      0   100%
src\utils\network.py                      37      1    97%   77
---------------------------------------------------------------------
TOTAL                                     568     11    98%
Required test coverage of 80.0% reached. Total coverage: 98.06%
```

---

## Coverage vs Sprint 14 Targets

| File                 | Target | Actual | Status |
| -------------------- | ------ | ------ | ------ |
| `schema_detector.py` | ≥ 80%  | 100%   | ✅      |
| `db_connector.py`    | ≥ 75%  | 100%   | ✅      |
| Overall              | ≥ 80%  | 98.06% | ✅      |

---

## Sprint 14 Test Additions

| File                                          | Tests Added | All Pass |
| --------------------------------------------- | ----------- | -------- |
| `tests/unit/test_schema_detector_extended.py` | 12          | ✅        |
| `tests/unit/test_db_connector_extended.py`    | 12          | ✅        |
| **Total new**                                 | **24**      | ✅        |

---

## Bug Reports

None — all tests pass, no regressions detected.

---

## Summary

Sprint 14 delivers a 24-test uplift covering previously uncovered exception and happy-path
branches in `schema_detector.py` and `db_connector.py`. Both modules reach 100% unit
coverage. Overall project coverage is 98.06%, comfortably above the 80% gate.
