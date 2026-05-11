# Sprint 8 Retrospective

**Sprint**: Sprint 8 — Quality Hardening
**Date**: 2026-05-06
**Facilitator**: Scrum Master

---

## What Went Well

- All 4 stories delivered at 11/11 points — velocity target met
- US-036 was resolved pre-sprint: investigation confirmed `urllib.parse` was already at module level; closed with documentation update rather than code churn
- `AppTest`-based sidebar tests (US-038) finally delivered after 4 sprint deferrals — 10 new UI tests covering MySQL/MongoDB mode switching, URI toggle, and empty-credential validation
- `_db_password` security fix (US-039) was surgical: one `st.session_state.pop()` call in the correct place; retry path intentionally preserved password for UX consistency
- Two new `TestMongoConfig` tests (US-037) closed the `__repr__` and `_connection_uri_from_raw` else-branch coverage gaps with zero risk to existing behaviour
- Coverage rose from 92.68% → 93.84% (+1.16 pp); 134 tests all green
- AppTest `at.session_state["key"]` vs `.get()` API discoverability issue fixed quickly — no regression; test suite robust
- All 8 epics now at 100% completion — EPIC-003, EPIC-004, EPIC-006, EPIC-008 all closed this sprint
- Milestone M9 achieved on schedule

## What Could Be Improved

- `src/components/*` and `src/app.py` still excluded from coverage measurement — AppTest exercises widget-level paths but live-DB code paths (Step 2, spinner, engine disposal) remain unmeasured without mock-patched integration tests
- `TestSidebarDBTypeSwitching` needed two rewrites before passing — AppTest `set_value().run()` chaining is not supported and session-state access via `.get()` raises `AttributeError` instead of returning `None`; these quirks should be documented
- `src/services/db_connector.py` lines 37–64 (live MySQL connect branch) still at 79% — below the service-level 90% aspiration; requires a Docker-based MySQL fixture or more comprehensive mocking
- Sprint 8 was lighter (11 pts) than Sprint 7 (15 pts); could have pulled a roadmap backlog item if stories had been estimated higher or if the urllib pre-resolution had been detected earlier in planning

## Action Items

| Action                                                                                               | Owner                  | Due               |
| ---------------------------------------------------------------------------------------------------- | ---------------------- | ----------------- |
| Add mock-patched AppTest tests for `_render_step2` success / failure paths (Step 2 coverage)         | Developer              | Sprint 9 planning |
| Document AppTest quirks: no chained `.run()`, no `.get()` on session_state, `default_timeout` needed | Developer              | Sprint 9 planning |
| Add Docker-based MySQL integration fixture to raise `db_connector.py` coverage above 90%             | Developer / DevOps     | Sprint 9 planning |
| Evaluate PostgreSQL live connection epic for Sprint 9                                                | Product / Scrum Master | Sprint 9 planning |

---

## Cumulative Velocity

| Sprint   | Committed | Delivered | Cumulative |
| -------- | --------- | --------- | ---------- |
| Sprint 1 | 21        | 21        | 21         |
| Sprint 2 | 21        | 21        | 42         |
| Sprint 3 | 13        | 13        | 55         |
| Sprint 4 | 16        | 16        | 71         |
| Sprint 5 | 16        | 16        | 87         |
| Sprint 6 | 28        | 28        | 115        |
| Sprint 7 | 15        | 15        | 130        |
| Sprint 8 | 11        | 11        | 141        |

**Total delivered**: 141 story points across 39 stories in 8 sprints
