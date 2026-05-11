# EPIC-019 — History Panel Display Polish

**ID**: EPIC-019  
**Sprint**: 22  
**Status**: 🔲 Not Started  
**Source**: SPRINT-21-retro.md → Action Item A1

---

## Goal

Enhance the query history panel's visual presentation so users can immediately identify
which database type each entry relates to, without expanding the SQL snippet.

---

## Background

Sprint 21 stored `db_type` in each history entry for syntax-highlighting correctness
(US-087). The value is now available in the entry dict but is not surfaced in the UI.
A small badge or label next to each entry would make the panel more informative.

---

## Acceptance Outcomes

- Each history entry in the expander shows a visible database-type indicator.
- The indicator is derived from `entry["db_type"]` — no heuristic needed.
- No breaking changes to the history entry schema.

---

## Child User Stories

- [ ] US-089 — Display db_type badge in history entry (Sprint 22, 2 pt)
