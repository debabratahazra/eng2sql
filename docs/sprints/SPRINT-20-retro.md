# Sprint 20 Retrospective

**Sprint**: 20  
**Date**: 2026-05-09  
**Velocity**: 8 points (US-085: 5pt, US-086: 3pt)  
**Cumulative Velocity**: 266 points  
**Status**: ✅ Complete

---

## What Went Well

- **Both stories delivered fully** within the sprint. The ADR-007 pure-helper extraction
  pattern was applied from the start — `_append_to_history`, `_truncate`,
  `_result_to_csv`, and `_export_filename` were designed as pure helpers before the
  widget classes were written. This made unit testing trivial and kept coverage at
  100.00%.
- **Re-use button** works seamlessly using the `key="query_text"` pattern on the
  Streamlit text_area. The one-line change to `query_input.py` required no new test file
  because the existing mocks already cover the component's logic.
- **CSV export** uses pandas `to_csv()` — a library call with no new infrastructure.
  The pure helper approach meant no mocking was needed; tests use real DataFrames.
- All 26 Sprint 20 smoke tests pass in 3.42 s. Full suite: 151 smoke tests.
- Coverage remains at **100.00%** (962 stmts, 0 miss) — unchanged from Sprint 19.
- Pragma audit continues to pass (23 files, 0 violations) after adding two new
  `# pragma: no cover` annotations.
- The sprint was highly efficient: 8 points of user-facing features with minimal
  technical debt.

---

## What Could Be Improved

- **History persistence**: The query history is session-scoped (cleared on reload).
  Users who close and reopen the app lose their history. A lightweight local-storage
  approach (e.g. `st.experimental_get_query_params` or browser `localStorage` via a
  Streamlit component) could persist history across sessions without a backend.
- **History lang detection**: The SQL vs MQL language detection in `QueryHistoryComponent`
  uses a heuristic (`entry["sql"].startswith("{")`) that could misidentify multi-line
  MQL. A more robust approach would store the `db_type` alongside `question` and `sql`
  in the history dict.
- **CSV export date format**: The filename uses `datetime.date.today()` which reflects
  the server date, not the user's local date. For international deployments, the user's
  timezone should be considered. Deferred to Future Backlog.
- **No "Clear history" button**: Users cannot manually clear the history without
  reloading the page. A clear button would improve UX. Deferred to a future sprint.

---

## Action Items

1. **Store `db_type` in history entry** — update `_append_to_history` signature to
   include `db_type: str` and update the history dict schema. This eliminates the
   MQL-detection heuristic in `QueryHistoryComponent`. Low effort.
2. **"Clear history" button** — add a button to `QueryHistoryComponent` that sets
   `st.session_state["query_history"] = []`. Very low effort; good UX improvement.
3. **History lang in smoke tests** — once `db_type` is stored, add a smoke test that
   verifies MQL history entries show `language="json"`.

---

## Sprint 21 Seeds (from Action Items)

Action items 1 and 2 are small, self-contained improvements. They can be bundled into
a Sprint 21 focused on UX polish (history improvements + any other user-facing tweaks).

---

## Metrics

| Metric                 | Sprint 20                   | Cumulative |
| ---------------------- | --------------------------- | ---------- |
| Story points delivered | 8                           | 266        |
| User stories completed | 2 (US-085, US-086)          | 85         |
| New unit tests added   | 29 (15 history + 14 CSV)    | ~877       |
| New smoke tests added  | 26                          | 151        |
| Bugs filed             | 0                           | 8          |
| Bugs resolved          | 0                           | 8          |
| Coverage               | 100.00% (962 stmts, 0 miss) | —          |
