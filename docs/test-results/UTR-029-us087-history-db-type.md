# UTR-029 — Unit Test Results: US-087 Store db_type in History Entry

**Story**: US-087 — Store db_type in History Entry  
**Sprint**: 21  
**Agent**: Unit Test Agent  
**Date**: 2026-05-09  
**Status**: ✅ PASSED

---

## Test File

`tests/unit/test_query_history.py`

---

## New Tests Added (US-087)

| #   | Test                            | Class                 | Result |
| --- | ------------------------------- | --------------------- | ------ |
| 1   | `test_db_type_default_is_mysql` | `TestAppendToHistory` | ✅ PASS |
| 2   | `test_db_type_mongodb_stored`   | `TestAppendToHistory` | ✅ PASS |
| 3   | `test_mongodb_returns_json`     | `TestDbTypeToLang`    | ✅ PASS |
| 4   | `test_mysql_returns_sql`        | `TestDbTypeToLang`    | ✅ PASS |
| 5   | `test_postgresql_returns_sql`   | `TestDbTypeToLang`    | ✅ PASS |
| 6   | `test_unknown_returns_sql`      | `TestDbTypeToLang`    | ✅ PASS |
| 7   | `test_empty_string_returns_sql` | `TestDbTypeToLang`    | ✅ PASS |

**7 new tests** across `TestAppendToHistory` (2 new) and `TestDbTypeToLang` (5 new).

---

## Updated Tests (dict shape now includes db_type key)

| Test                                        | Change                                         |
| ------------------------------------------- | ---------------------------------------------- |
| `test_empty_history_gets_first_entry`       | Added `"db_type": "MySQL"` to expected dict    |
| `test_new_entry_prepended_at_index_zero`    | Pass `db_type="PostgreSQL"`, assert in result  |
| `test_duplicate_question_is_deduplicated`   | History entries include `"db_type"`            |
| `test_list_capped_at_max_entries`           | History entries include `"db_type"`            |
| `test_custom_max_entries_respected`         | History entries include `"db_type"`            |
| `test_max_entries_one_returns_only_latest`  | Entry includes `"db_type"`                     |
| `test_original_history_not_mutated`         | Entry includes `"db_type"`                     |
| `test_returns_list_of_dicts`                | Asserts `"db_type"` key present, value correct |
| `test_order_preserved_for_existing_entries` | History entries include `"db_type"`            |

---

## Full Suite Summary

```
tests/unit/test_query_history.py — 22 passed in 0.97s
```

**Total unit tests**: 414 passed, 4 deselected  
**Coverage**: 100.00% (964 stmts, 0 miss)  
**Pragma audit**: 23 files checked, 0 violations

---

## Coverage: query_history.py

| File                              | Stmts | Miss | Cover    |
| --------------------------------- | ----- | ---- | -------- |
| `src/components/query_history.py` | 15    | 0    | **100%** |

`_db_type_to_lang` contributes 2 new executable statements (both covered).  
`_append_to_history` updated with `db_type` parameter (no new stmts, parameter default).  
`render()` remains under `# pragma: no cover`.
