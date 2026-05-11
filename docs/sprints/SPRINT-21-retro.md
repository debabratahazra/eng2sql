# SPRINT-21 Retrospective

**Sprint**: 21 — Query History UX Polish  
**Date**: 2026-05-09  
**Scrum Master**: Scrum Master Agent  
**Velocity**: 3 / 3 pts (100%)  
**Cumulative**: 269 pts across 87 stories in 21 sprints

---

## Sprint Goal

Improve query history UX by storing `db_type` in each history entry for correct
syntax highlighting (US-087) and adding a "Clear History" button (US-088).

---

## Delivered

| Story  | Title                          | Points | Status |
| ------ | ------------------------------ | ------ | ------ |
| US-087 | Store db_type in history entry | 2      | ✅ Done |
| US-088 | Clear History button           | 1      | ✅ Done |

---

## Smoke Test Results

**STR-012**: 26 / 26 tests passed in 3.30 s.  
No failures. Backward compatibility with Sprint 20 history entries confirmed via
`.get("db_type", "MySQL")` defensive default.

---

## What Went Well

- `_db_type_to_lang()` extracted as a pure helper per ADR-007 — immediately testable,
  zero Streamlit dependency.
- Backward compatibility was handled proactively (`.get("db_type", "MySQL")` default
  in `render()`) without needing a migration step.
- US-088 required zero pure helpers — single widget call inside existing pragma block.
- 414 unit tests, 100.00% coverage (964 stmts) maintained with no regressions.
- Pragma audit still at 0 violations after adding new helper.
- Sprint velocity: 3/3 pts in a single pipeline session — fastest sprint yet.

---

## What Could Be Improved

1. **History persistence across sessions**: Query history is lost on Streamlit server
   restart. A lightweight JSON persistence layer (e.g., writing to a user-specific
   `.eng2sql_history.json` file) would improve developer UX.

2. **History filtering/search**: With 10 entries the panel is small, but as users work
   more a search-by-keyword feature would help rediscover past queries quickly.

3. **db_type badge in history panel**: The db_type is now stored but not displayed in
   the history UI. Showing a small badge ("MySQL" / "MongoDB" / "PostgreSQL") next to
   each entry would make the history panel more informative.

---

## Action Items

| #   | Action                                                 | Priority | Target         |
| --- | ------------------------------------------------------ | -------- | -------------- |
| A1  | Add db_type badge display to history panel entries     | Medium   | Sprint 22      |
| A2  | Investigate JSON persistence for cross-session history | Low      | Future Backlog |
| A3  | Add search/filter to history expander when > 5 entries | Low      | Future Backlog |
