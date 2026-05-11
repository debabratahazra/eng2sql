# EPIC-014 — Component Coverage Completion

**Status**: 🔲 Backlog  
**Priority**: High  
**Target Sprint**: 17  

---

## Goal

Re-enable `src/components/*` in coverage measurement, add rendering-method tests for
the paths that cannot be covered by pure-function extraction alone, and investigate
AppTest fixture sharing to reduce smoke test startup overhead.

---

## Background

Sprint 16 (EPIC-013) extracted 6 pure-logic helpers from `src/components/sidebar.py`
and added 34 unit tests. However, the `src/components/*` modules are still excluded
from the coverage gate via `pyproject.toml` `omit`. Sprint 17 will complete coverage
for the component layer.

---

## Acceptance Outcomes

1. `src/components/*` removed from coverage `omit` list; overall gate ≥ 80%.
2. `_render_relational_step2`, `_render_mongo_step1_uri_mode`, and
   `_render_mongo_step2` have AppTest-level tests.
3. Error branches in `src/services/db_connector.py` are covered.
4. Smoke test startup time documented; fixture-sharing approach evaluated.

---

## User Stories

| ID     | Title                                            | Points |
| ------ | ------------------------------------------------ | ------ |
| US-075 | Re-enable component coverage; hold ≥ 80% gate    | 5      |
| US-076 | AppTest rendering-method tests (step2, URI mode) | 3      |
| US-077 | Investigate AppTest fixture sharing              | 2      |
| US-078 | Cover error branches in db_connector.py          | 3      |

**Total**: 13 points
