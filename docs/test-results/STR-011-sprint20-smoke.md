# STR-011 — Sprint 20 Smoke Test Results

**Document**: STR-011  
**Sprint**: 20  
**Date**: 2026-05-09  
**Agent**: Smoke Test Agent  
**Status**: ✅ ALL SMOKE TESTS PASS

---

## Summary

| Metric          | Value                                 |
| --------------- | ------------------------------------- |
| Smoke test file | `tests/smoke/test_sprint_20_smoke.py` |
| Sprint 20 tests | **26**                                |
| Duration        | 3.42 s                                |
| Failures        | 0                                     |
| Full suite size | **151** (125 prior + 26 new)          |

---

## Sprint 20 Smoke Test Results

### `TestQueryHistoryUS085` (11 tests)

| Test                                          | Result |
| --------------------------------------------- | ------ |
| `test_query_history_module_exists`            | ✅      |
| `test_append_to_history_is_importable`        | ✅      |
| `test_truncate_is_importable`                 | ✅      |
| `test_query_history_component_class_exists`   | ✅      |
| `test_append_to_history_empty_list`           | ✅      |
| `test_append_to_history_caps_at_ten`          | ✅      |
| `test_truncate_long_string`                   | ✅      |
| `test_app_py_imports_query_history`           | ✅      |
| `test_app_py_initialises_query_history_state` | ✅      |
| `test_query_input_uses_query_text_key`        | ✅      |
| `test_utr_027_exists`                         | ✅      |

### `TestCSVExportUS086` (10 tests)

| Test                                     | Result |
| ---------------------------------------- | ------ |
| `test_csv_export_module_exists`          | ✅      |
| `test_result_to_csv_importable`          | ✅      |
| `test_export_filename_importable`        | ✅      |
| `test_csv_export_component_class_exists` | ✅      |
| `test_result_to_csv_returns_bytes`       | ✅      |
| `test_result_to_csv_utf8_decodable`      | ✅      |
| `test_export_filename_format`            | ✅      |
| `test_app_py_imports_csv_export`         | ✅      |
| `test_app_py_renders_csv_export`         | ✅      |
| `test_utr_028_exists`                    | ✅      |

### `TestGeneralRegressionSprint20` (5 tests)

| Test                                            | Result |
| ----------------------------------------------- | ------ |
| `test_sprint_19_smoke_still_passes`             | ✅      |
| `test_pragma_audit_still_passes_on_src`         | ✅      |
| `test_tr_020_exists`                            | ✅      |
| `test_cr_020_exists`                            | ✅      |
| `test_coverage_100_percent_referenced_in_tr020` | ✅      |

---

## Verdict

All 26 Sprint 20 smoke tests pass in 3.42 s. Pragma audit confirms 23 files checked,
0 violations. Sprint 19 smoke suite regression is intact. The sprint-end smoke gate is
**cleared** — Sprint 20 retro may proceed.
