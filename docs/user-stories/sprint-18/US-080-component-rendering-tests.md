# US-080 — AppTest Tests for progress_tracker, query_input, schema_viewer

**ID**: US-080  
**Epic**: EPIC-015  
**Sprint**: 18  
**Points**: 5  
**Status**: ✅ Descoped — US-079 resolves coverage gap  
**Priority**: Medium

---

## User Story

As a **developer**, I want AppTest-based tests for the three remaining partially-covered
UI components so that the rendering paths are verified and coverage reaches ≥ 99%.

---

## Background

Three components have uncovered rendering paths after Sprint 17:

| Component             | Uncovered Lines | Gap                                       |
| --------------------- | --------------- | ----------------------------------------- |
| `progress_tracker.py` | 14, 22–30       | `reset()` and `update()` widget calls     |
| `query_input.py`      | 32–35           | Empty-input validation after button click |
| `schema_viewer.py`    | 20–21, 26–27    | Empty-schema warning + refresh button     |

If US-079 (pragma annotation) is implemented instead, this story can be descoped.

---

## Acceptance Criteria

- [ ] `tests/unit/test_component_rendering.py` created with tests for all three
  components.
- [ ] `progress_tracker.reset()` and `progress_tracker.update()` paths exercised via
  AppTest or direct invocation.
- [ ] `query_input.py` empty-input validation branch triggered via AppTest button click.
- [ ] `schema_viewer.py` empty-schema warning and refresh button rendered and verified.
- [ ] Coverage on each component reaches ≥ 90% after new tests.
- [ ] All existing 360 unit tests continue to pass.

---

## Definition of Done

- [ ] Code implemented (test file created)
- [ ] Unit tests written and passing
- [ ] Coverage gate (≥ 80%) passes; target components ≥ 90%
- [ ] Code review approved
- [ ] User story status set to ✅ Done
