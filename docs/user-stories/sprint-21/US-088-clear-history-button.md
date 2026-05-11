# US-088 — Clear History Button

**ID**: US-088  
**Epic**: EPIC-018  
**Sprint**: 21  
**Points**: 1  
**Status**: ✅ Done
**Priority**: Low

---

## User Story

As a **user**, I want a "Clear History" button in the query history panel so that I can
reset my session history without reloading the page.

---

## Acceptance Criteria

- [x] A "🗑️ Clear History" button appears at the top of the history expander.
- [x] Clicking the button sets `st.session_state["query_history"] = []` and calls
  `st.rerun()`.
- [x] When history is empty after clearing, the expander is not rendered.

---

## Technical Notes

- No pure helper needed for the button itself (it's a single `st.button` + session
  state write + `st.rerun()` — all widget calls, under `# pragma: no cover`).
- The "history empty → no render" path is already handled by the existing `if not history: return` guard.

---

## Definition of Done

- [x] Code implemented
- [x] Smoke test verifies clear button string is present in query_history.py source
- [x] Code review approved
- [x] User story status set to ✅ Done
