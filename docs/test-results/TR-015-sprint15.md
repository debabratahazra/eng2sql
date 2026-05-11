# TR-015 — Full Test Run Results: Sprint 15

**Sprint**: 15  
**Date**: 2025-07-17  
**Agent**: Tester  
**Command**: `python -m pytest tests/unit --cov=src --cov-report=term-missing -q --tb=short`

---

## Summary

| Metric                                 | Result   |
| -------------------------------------- | -------- |
| Total tests                            | **301**  |
| Passed                                 | **301**  |
| Failed                                 | 0        |
| Errors                                 | 0        |
| Skipped                                | 0        |
| Deselected (integration/smoke markers) | 4        |
| Total coverage                         | **100%** |
| Coverage gate (80%)                    | ✅ PASS   |
| Duration                               | ~88 s    |

---

## Coverage Report

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src\models\__init__.py                      0      0   100%
src\models\config.py                       97      0   100%
src\services\__init__.py                    0      0   100%
src\services\db_connector.py               57      0   100%
src\services\mongo_connector.py           145      0   100%
src\services\mongo_query_executor.py       61      0   100%
src\services\mongo_schema_detector.py      43      0   100%
src\services\schema_detector.py            48      0   100%
src\services\sql_generator.py              58      0   100%
src\utils\__init__.py                       0      0   100%
src\utils\exceptions.py                     7      0   100%
src\utils\logger.py                        15      0   100%
src\utils\network.py                       37      0   100%
---------------------------------------------------------------------
TOTAL                                     568      0   100%
Required test coverage of 80.0% reached. Total coverage: 100.00%
```

---

## Sprint 15 Contribution

| Story     | New Tests | Before                       | After         |
| --------- | --------- | ---------------------------- | ------------- |
| US-066    | 6         | `mongo_connector.py` 95%     | **100%**      |
| US-067    | 9         | `models/config.py` 97%       | **100%**      |
| US-068    | 3         | `utils/network.py` 97%       | **100%**      |
| US-069    | 19        | sidebar (excluded from gate) | 19 tests pass |
| US-070    | 0         | CI job verified              | ✅             |
| **Total** | **37**    | **98.06%**                   | **100%**      |

---

## Regression Status

All 264 pre-Sprint-15 tests continue to pass. No regressions introduced.

---

## Notes

- `src/app.py` and `src/components/*` are excluded from coverage per `pyproject.toml`  
  (exercised by AppTest smoke tests instead).
- 4 tests deselected by `-m 'not integration and not smoke'` filter (integration/smoke markers).
