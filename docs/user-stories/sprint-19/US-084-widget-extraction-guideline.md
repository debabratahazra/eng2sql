# US-084 — Widget-Component Pure-Helper Extraction Guideline

**ID**: US-084  
**Epic**: EPIC-016  
**Sprint**: 19  
**Points**: 2  
**Status**: ✅ Done  
**Priority**: Low

---

## User Story

As a **developer**, I want a documented guideline for extracting pure logic from
widget-heavy components (`progress_tracker.py`, `query_input.py`) so that any future
business logic added to these files is automatically unit-testable without Streamlit.

---

## Background

`progress_tracker.py` and `query_input.py` currently contain only Streamlit widget
calls (all excluded via `# pragma: no cover`). If future sprints add business logic
to these files (e.g. input validation, rate limiting, step-count limits), that logic
should follow the Sprint 16 `_validate_*` / `_build_*` extraction pattern to remain
testable.

This story adds a developer-guide section and a simple ADR confirming the pattern.

---

## Acceptance Criteria

- [x] `docs/guides/developer-guide.md` contains a "Widget-Component Extraction
  Guideline" section with a worked example showing how to split widget calls from
  pure logic.
- [x] `docs/architecture/ADR-007-widget-extraction-pattern.md` created confirming
  the decision.
- [x] No production code changes required (guideline only).

---

## Definition of Done

- [x] Developer guide updated
- [x] ADR-007 created
- [x] Code review approved (docs review)
- [x] User story status set to ✅ Done
