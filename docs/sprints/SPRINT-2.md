# Sprint 2 Plan

**Goal**: Live database connection, auto-detected schema, SQL execution with results display, and error handling
**Duration**: 2026-05-15 → 2026-05-28 (2 weeks)
**Velocity Target**: 21 points

---

## Committed Stories

| Story ID | Title                          | Points | Assignee (Agent) |
| -------- | ------------------------------ | ------ | ---------------- |
| US-008   | Database Connection Form       | 5      | Developer        |
| US-009   | Schema Auto-Detection          | 5      | Developer        |
| US-010   | Schema Viewer Panel            | 3      | Developer        |
| US-011   | SQL Execution & Results Table  | 5      | Developer        |
| US-012   | Error Handling & User Feedback | 3      | Developer        |

**Total**: 21 points

---

## Definition of Done

- [x] Code implemented and committed
- [x] Code review passed (CR-001)
- [x] Unit tests written and passing (≥ 80% coverage)
- [x] Integration tests passing (SQLite in-memory engine; no MySQL server required)
- [x] Documentation updated (user-guide.md, developer-guide.md)
- [x] No critical bugs open

---

## Sprint Risks

| Risk                                        | Likelihood | Impact | Mitigation                                                                |
| ------------------------------------------- | ---------- | ------ | ------------------------------------------------------------------------- |
| MySQL connection timeout blocking CI        | High       | High   | Use SQLite in-memory for all tests; MySQL only in manual testing          |
| `st.session_state` race conditions on rerun | Medium     | Medium | Store engine and schema in session state; guard with `if ... is None`     |
| Schema detection slow on large databases    | Low        | Low    | In-memory cache per session; "Refresh Schema" button for manual refresh   |
| Non-SELECT SQL reaching `execute_query`     | Medium     | High   | Enforce `sql.strip().upper().startswith("SELECT")` guard before execution |

---

## Outcome

**Status**: ✅ DONE
**Actual Velocity**: 21 / 21 points (100%)
**Notes**: All EPIC-003 acceptance criteria met. `SchemaViewerComponent`, `DBConnector.execute_query()`, and sidebar connection form implemented and tested.
