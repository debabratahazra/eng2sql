# Sprint 5 Retrospective

**Sprint**: Sprint 5 — Live DB Database Selector
**Date**: 2026-07-14
**Facilitator**: Scrum Master

---

## What Went Well

- All 4 stories delivered at 16/16 points — velocity target hit exactly
- Two-step MySQL connection flow works cleanly; state isolation between Step 1 and Step 2 is correct
- `DBConnector.list_databases()` implemented with 100% branch coverage on first pass
- Removing static schema mode simplified the sidebar considerably — less dead code
- Session-state key naming convention (`db_server_engine`, `available_databases`, `selected_database`) is consistent and well-documented in developer guide
- No regressions — all pre-Sprint 5 tests continued to pass after sidebar refactor
- Integration tests run against SQLite in-memory; mocked unit tests cover MySQL-specific paths cleanly

## What Could Be Improved

- `SHOW DATABASES` filtering for system databases (information_schema, mysql, performance_schema, sys) was added reactively rather than proactively designed
- `_db_password` stored in session state is a compromise; a more robust solution would be a short-lived credential token — deferred to future security hardening sprint
- Sprint 5 introduced the first two-engine concept (MySQL only, but prepared the ground for MongoDB) — could have been designed with multi-engine extensibility in mind from the start, avoiding later rework
- `ruff check` and `mypy` exit-0 items in the Sprint 5 DoD were not validated by CI automatically at the time — fixed in the existing pipeline

## Action Items

| Action                                                                        | Owner                      | Due                          |
| ----------------------------------------------------------------------------- | -------------------------- | ---------------------------- |
| Plan MongoDB support as next major epic (EPIC-007)                            | Scrum Master / Epic Writer | Sprint 6 planning            |
| Review `_db_password` in session state — consider short-lived encrypted token | Developer                  | Sprint 7+ security hardening |
| Add SRV / replica-set awareness to roadmap backlog                            | Product                    | Sprint 6 planning            |

---

## Cumulative Velocity

| Sprint   | Committed | Delivered | Cumulative |
| -------- | --------- | --------- | ---------- |
| Sprint 1 | 21        | 21        | 21         |
| Sprint 2 | 21        | 21        | 42         |
| Sprint 3 | 13        | 13        | 55         |
| Sprint 4 | 16        | 16        | 71         |
| Sprint 5 | 16        | 16        | 87         |

**Total delivered**: 87 story points across 24 stories in 5 sprints
