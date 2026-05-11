# US-071 — Refactor Sidebar: Extract Pure Logic from Widget Calls

**Epic**: EPIC-013 — Component Refactoring & Full-Stack Coverage  
**Sprint**: 16  
**Points**: 5  
**Priority**: High  
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** `src/components/sidebar.py` to have pure-logic functions separated from
> Streamlit widget calls,
> **so that** sidebar logic can be unit-tested without a live Streamlit runtime.

---

## Background

Currently `src/components/sidebar.py` is excluded from coverage because all business  
logic is interleaved with `st.*` widget calls. Extracting validation, state-transition,  
and connection-building logic into standalone functions would allow measurement and  
testing of those paths.

---

## Acceptance Criteria

- [x] At least 3 pure-logic functions extracted from `_render_relational_step1` / `_render_relational_step2`
- [x] All existing AppTest smoke tests continue to pass
- [x] Extracted functions have full docstrings and type hints
- [x] `src/components/*` can be re-enabled in coverage without dropping below 70%

---

## Definition of Done

- [x] Code implemented
- [x] All existing tests pass (no regressions)
- [x] Code review approved
- [x] Docs updated
