# US-081 — Document Optional-Import Pragma Pattern and AppTest Isolation Guidance

**ID**: US-081  
**Epic**: EPIC-015  
**Sprint**: 18  
**Points**: 2  
**Status**: ✅ Done  
**Priority**: Low

---

## User Story

As a **developer**, I want the optional-import `# pragma: no cover` pattern and
AppTest parallel-isolation constraints documented in the developer guide so that
contributors understand why certain lines are excluded from coverage and how to
write safe AppTest tests.

---

## Background

Two documentation gaps identified in Sprint 17:

1. **Optional-import pattern** — `sidebar.py:184` uses `if certifi:` to guard a call
   to `certifi.where()`. This is an optional dependency; the `if certifi:` guard cannot
   be triggered unless `certifi` is installed AND the test explicitly exercises that
   path. The pragma annotation and its rationale should be documented.
2. **xdist + AppTest isolation** — rendering tests (US-076) cannot run safely under
   `pytest-xdist` because AppTest workers share Streamlit process-level state. This
   constraint is not yet documented; contributors may unknowingly re-enable `-n auto`
   for the rendering test file.

---

## Acceptance Criteria

- [x] `docs/guides/developer-guide.md` contains a "Optional-Import `# pragma: no cover`
  Pattern" section explaining the `if certifi:` guard, why it cannot be tested, and
  the approved annotation format.
- [x] Developer guide contains an "AppTest + pytest-xdist Compatibility" section
  documenting the isolation constraint and the `--override-ini="addopts=..."` workaround.
- [x] No code changes required (documentation-only story).

---

## Definition of Done

- [x] Developer guide updated with both sections
- [x] Code review approved (docs review)
- [x] User story status set to ✅ Done
