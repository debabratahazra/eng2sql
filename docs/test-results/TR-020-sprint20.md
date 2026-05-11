# TR-020 — Sprint 20 Test Results

**Document**: TR-020  
**Sprint**: 20  
**Date**: 2026-05-09  
**Agent**: Tester  
**Status**: ✅ ALL TESTS PASS

---

## Unit Test Run

| Metric           | Value                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| Command          | `pytest tests/unit/ --tb=short --override-ini="addopts=--tb=short -m 'not integration and not smoke'"` |
| Tests collected  | 411 (407 pass, 4 deselected)                                                                           |
| Tests passed     | **407**                                                                                                |
| Tests failed     | 0                                                                                                      |
| Tests skipped    | 0                                                                                                      |
| Duration         | 133.22 s                                                                                               |
| Coverage (total) | **100.00%** (962 stmts, 0 miss)                                                                        |
| Coverage gate    | ≥ 80% ✅                                                                                                |

### Coverage by File (Sprint 20 additions)

| File                              | Stmts   | Miss  | Cover       |
| --------------------------------- | ------- | ----- | ----------- |
| `src/components/query_history.py` | 13      | 0     | 100%        |
| `src/components/csv_export.py`    | 8       | 0     | 100%        |
| `src/components/query_input.py`   | 12      | 0     | 100%        |
| All other `src/` files            | 929     | 0     | 100%        |
| **TOTAL**                         | **962** | **0** | **100.00%** |

---

## New Tests (Sprint 20)

| Test File                          | Tests  | All Pass |
| ---------------------------------- | ------ | -------- |
| `tests/unit/test_query_history.py` | 15     | ✅        |
| `tests/unit/test_csv_export.py`    | 14     | ✅        |
| **Sprint 20 new total**            | **29** | ✅        |

---

## Bug Reports

None filed. All 407 tests pass with no failures.

---

## Pragma Audit

```
Pragma audit passed — 23 file(s) checked, 0 violations.
```

---

## Summary

Sprint 20 added 29 new unit tests (15 for US-085 query history, 14 for US-086 CSV
export). All pure helpers follow the ADR-007 extraction pattern. Coverage remains at
100.00% (962 stmts, 0 miss), up from 941 stmts at Sprint 19 end (21 new testable
statements from the two new component files).
