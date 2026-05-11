# US-089 — Display db_type Badge in History Entry

**ID**: US-089  
**Epic**: EPIC-019  
**Sprint**: 22  
**Points**: 2  
**Status**: ✅ Done  
**Priority**: Medium  
**Source**: SPRINT-21-retro.md → Action Item A1

---

## User Story

As a **user**, I want each entry in the query history panel to display a small database-type
badge so that I can immediately identify whether a past query was for MySQL, PostgreSQL,
or MongoDB without expanding the SQL snippet.

---

## Acceptance Criteria

- [x] Each history entry shows `entry["db_type"]` as a label/badge in the UI.
- [x] The label is rendered via a pure helper `_db_type_badge(db_type: str) -> str` that
  returns a short display string (e.g. `"🐬 MySQL"`, `"🐘 PostgreSQL"`, `"🍃 MongoDB"`).
- [x] The badge uses `st.caption()` or similar — widget-only call, under `# pragma: no cover`.
- [x] `_db_type_badge` is unit-tested for all three known types and an unknown fallback.

---

## Technical Notes

- Extract `_db_type_badge(db_type: str) -> str` as a pure helper per ADR-007.
- Suggested mapping: `"MySQL"` → `"🐬 MySQL"`, `"PostgreSQL"` → `"🐘 PostgreSQL"`,
  `"MongoDB"` → `"🍃 MongoDB"`, others → `db_type`.
- Badge rendered in `col_text` column, above or below the question caption.

---

## Definition of Done

- [x] Code implemented
- [x] Pure helper extracted and unit-tested (≥ 4 tests)
- [x] Code review approved
- [x] User story status set to ✅ Done
