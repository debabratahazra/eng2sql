# EPIC-018 — Query History UX Polish

**ID**: EPIC-018  
**Status**: 🔲 Planned  
**Sprint**: 21  
**Priority**: Low

---

## Goal

Improve the Sprint 20 query history feature with two small but impactful UX changes:
(1) store the database type alongside each history entry to eliminate the MQL-detection
heuristic, and (2) add a "Clear history" button so users can reset the list without
reloading the page.

---

## Business Value

These changes increase reliability of the history panel (correct syntax highlighting for
MQL history entries) and give users control over their session state without a disruptive
page reload.

---

## Acceptance Outcomes

1. Each history entry stores `{"question": str, "sql": str, "db_type": str}`.
2. `QueryHistoryComponent` uses the stored `db_type` for language detection instead of
   inspecting the SQL string.
3. A "🗑️ Clear History" button in the history panel sets `query_history = []` and reruns.
4. All new logic follows ADR-007 (pure helper extraction + widget pragma).

---

## Child User Stories

- [ ] US-087 — Store db_type in history entry and use it for lang detection
- [ ] US-088 — Clear history button in QueryHistoryComponent

---

## Definition of Done

- [ ] Both child user stories delivered and ✅ Done
- [ ] Coverage gate ≥ 80% maintained
- [ ] ADR-007 extraction pattern applied to any changed logic
- [ ] CR-021 code review approved
- [ ] SPRINT-21-retro.md created
