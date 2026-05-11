# US-085 — Session-Scoped Query History

**ID**: US-085  
**Epic**: EPIC-017  
**Sprint**: 20  
**Points**: 5  
**Status**: ✅ Done  
**Priority**: Medium

---

## User Story

As a **power user**, I want to see a history of queries I have generated in the current
session so that I can quickly re-use or refine previous queries without retyping them.

---

## Acceptance Criteria

- [ ] The sidebar (or a main-area expander) shows the last 10 queries generated in the
  current Streamlit session.
- [ ] Each history entry shows the plain-English question and the generated SQL/MQL
  (truncated to 80 chars if long).
- [ ] A "Re-use" button next to each entry re-populates the query input with that text.
- [ ] History is cleared on page reload (session-scoped only).
- [ ] The history list is stored in `st.session_state["query_history"]` as a list of
  dicts `{"question": str, "sql": str}`.

---

## Technical Notes

- Extract the history-append logic into a pure helper
  `_append_to_history(history, question, sql, max_entries=10) -> list[dict]`
  following ADR-007 (testable without Streamlit).
- The rendering code that calls `st.expander`, `st.text`, `st.button` stays under
  `# pragma: no cover` (widget-only calls).

---

## Definition of Done

- [x] Code implemented
- [x] Pure helper(s) extracted and unit-tested (≥ 80% coverage, gate continues to pass)
- [x] Code review approved
- [x] User story status set to ✅ Done
