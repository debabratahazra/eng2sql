# EPIC-017 — Query History & Export

**ID**: EPIC-017  
**Status**: 🔲 Planned  
**Sprint**: 20  
**Priority**: Medium

---

## Goal

Allow users to view a history of previously generated SQL/MQL queries within the current
session, copy them to clipboard, and export the most recent result set as a CSV file.

---

## Business Value

Contributors and analysts frequently run variants of the same query. A session history
panel reduces friction by letting users re-run or refine previous queries without
retyping them. CSV export closes the "last mile" gap between query results displayed
in the Streamlit table and downstream tools (Excel, pandas, BI dashboards).

---

## Acceptance Outcomes

1. A "Query History" panel in the Streamlit sidebar or main area shows the last N
   queries generated in the current session, each with a "Re-use" button.
2. The most recent SQL/MQL result set can be downloaded as a CSV file via a
   Streamlit download button.
3. History is session-scoped (cleared on page reload); no persistence is required.
4. All new logic is extracted into pure helpers following ADR-007.

---

## Child User Stories

- [ ] US-085 — Session-scoped query history (sidebar panel, last 10 queries, re-use button)
- [ ] US-086 — CSV export of most recent result set (download button in sql_output.py)

---

## Definition of Done

- [ ] Both child user stories delivered and ✅ Done
- [ ] Coverage gate ≥ 80% maintained
- [ ] ADR-007 extraction pattern applied to any new component logic
- [ ] CR-020 code review approved
- [ ] SPRINT-20-retro.md created
