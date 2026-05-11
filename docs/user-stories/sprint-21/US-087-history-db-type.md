# US-087 — Store db_type in History Entry

**ID**: US-087  
**Epic**: EPIC-018  
**Sprint**: 21  
**Points**: 2  
**Status**: ✅ Done
**Priority**: Low

---

## User Story

As a **developer**, I want each query history entry to include the database type so that
the history panel can display correct syntax highlighting without inspecting the SQL
string.

---

## Acceptance Criteria

- [x] `_append_to_history` accepts a `db_type: str` parameter (default `"MySQL"`).
- [x] Each history entry dict has the shape
  `{"question": str, "sql": str, "db_type": str}`.
- [x] `QueryHistoryComponent.render()` uses `entry["db_type"]` to select `language=`
  for `st.code()` instead of inspecting the SQL string.
- [x] `app.py` passes `db_type` when calling `_append_to_history`.
- [x] Existing unit tests updated; no tests break.

---

## Technical Notes

- Update `_append_to_history(history, question, sql, db_type="MySQL", max_entries=10)`.
- Language mapping: `"MongoDB"` → `"json"`, others → `"sql"`.
- Extract `_db_type_to_lang(db_type: str) -> str` as a pure helper per ADR-007.

---

## Definition of Done

- [x] Code implemented
- [x] Pure helper(s) extracted and unit-tested
- [x] Code review approved
- [x] User story status set to ✅ Done
