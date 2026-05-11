# EPIC-015 — Final Coverage Perfection

**ID**: EPIC-015  
**Created**: Sprint 17 Retro  
**Target Sprint**: 18  
**Status**: 🟡 In Progress  
**Priority**: Medium

---

## Goal

Raise effective coverage from 98.03% to ≥ 99% by either adding targeted AppTest tests
for the remaining 19 uncovered statements, or applying `# pragma: no cover` to lines
that are architecturally unreachable in the test environment.

---

## Background

Sprint 17 re-enabled component coverage and reached 98.03% (966 stmts, 19 miss). The
remaining gaps fall into two categories:

1. **Architecturally unreachable via AppTest** — `sidebar.py:184` (optional `certifi`
   import branch), `sidebar.py:792` (expired-session guard inside button handler when
   client is `None`).
2. **Pure Streamlit widget calls not yet exercised** — `progress_tracker.py` (lines
   14, 22–30), `query_input.py` (lines 32–35), `schema_viewer.py` (lines 20–21, 26–27).

---

## Acceptance Outcomes

- Reported test coverage ≥ 99% (or all remaining gaps are explicitly `# pragma: no cover`
  annotated with justification comments).
- All existing tests continue to pass (no regressions).
- Developer guide documents the optional-import pragma pattern.
- Sprint 18 user stories close with all DoD checkboxes ticked.

---

## Stories

| Story  | Description                                                    | Points |
| ------ | -------------------------------------------------------------- | ------ |
| US-079 | Apply `# pragma: no cover` to unreachable branches             | 3      |
| US-080 | AppTest tests for progress_tracker, query_input, schema_viewer | 5      |
| US-081 | Document pragma pattern + AppTest isolation guidance           | 2      |

**Total**: 10 story points
