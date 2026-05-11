# UTR-027 — US-085: Session-Scoped Query History

**Document**: UTR-027  
**Story**: US-085 — Session-Scoped Query History  
**Sprint**: 20  
**Date**: 2026-05-09  
**Agent**: Unit Test Agent  
**Status**: ✅ PASSED

---

## Summary

| Metric             | Value                              |
| ------------------ | ---------------------------------- |
| Test file          | `tests/unit/test_query_history.py` |
| Tests in file      | 15                                 |
| Tests total (unit) | 407                                |
| Duration           | 121.73 s (full suite, -n auto)     |
| Coverage (total)   | **100.00%** (962 stmts, 0 miss)    |
| Coverage gate      | ≥ 80% ✅                            |

---

## Tests Written

### `TestAppendToHistory` (9 tests)

| Test                                        | Description                                   | Result |
| ------------------------------------------- | --------------------------------------------- | ------ |
| `test_empty_history_gets_first_entry`       | Appending to empty list returns single item   | ✅      |
| `test_new_entry_prepended_at_index_zero`    | Most-recent entry at index 0                  | ✅      |
| `test_duplicate_question_is_deduplicated`   | Re-submitting same question removes old entry | ✅      |
| `test_list_capped_at_max_entries`           | History capped at 10 (default)                | ✅      |
| `test_custom_max_entries_respected`         | Custom max_entries param limits list          | ✅      |
| `test_max_entries_one_returns_only_latest`  | max_entries=1 keeps only newest               | ✅      |
| `test_original_history_not_mutated`         | Input list not modified in place              | ✅      |
| `test_returns_list_of_dicts`                | Return type has question and sql keys         | ✅      |
| `test_order_preserved_for_existing_entries` | Relative order of older entries preserved     | ✅      |

### `TestTruncate` (6 tests)

| Test                                       | Description                          | Result |
| ------------------------------------------ | ------------------------------------ | ------ |
| `test_short_string_unchanged`              | Short strings returned as-is         | ✅      |
| `test_exact_length_unchanged`              | Exact-length strings not truncated   | ✅      |
| `test_long_string_truncated_with_ellipsis` | Long strings cut + ellipsis appended | ✅      |
| `test_custom_max_len`                      | Custom max_len parameter respected   | ✅      |
| `test_empty_string_unchanged`              | Empty string returned as-is          | ✅      |
| `test_unicode_content_truncated_correctly` | Unicode by char count, not bytes     | ✅      |

---

## Coverage for `src/components/query_history.py`

| Stmts | Miss | Cover |
| ----- | ---- | ----- |
| 13    | 0    | 100%  |

The `render()` method is under `# pragma: no cover` (widget-only; Excluded from
coverage — all statements are `st.` calls requiring a live Streamlit render context).
`pragma_audit.py` reports 0 violations.

---

## DoD Checklist

- [x] Pure helper(s) extracted and unit-tested
- [x] All 15 tests pass
- [x] Coverage gate ≥ 80% maintained (100.00%)
- [x] `pragma_audit.py` passes (0 violations)
