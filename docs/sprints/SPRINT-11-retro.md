# Sprint 11 Retrospective

**Sprint**: Sprint 11 — Refactor & Hardening
**Date**: 2026-05-07
**Facilitator**: Scrum Master

---

## Sprint Snapshot

| Item       | Detail                                                                                                                                                                                 |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Goal       | Pay down Sprint 10 technical debt: WSL2 helper extraction, sidebar refactor, configurable PG admin-DB, CI Docker matrix, packaging, db_connector coverage lift, sslmode pre-validation |
| Dates      | Post-Sprint-10 close → 2026-05-09                                                                                                                                                      |
| Committed  | 14 pts                                                                                                                                                                                 |
| Delivered  | 11 pts                                                                                                                                                                                 |
| Deferred   | 3 pts (US-051 sidebar mixin, US-054 pyproject optional deps)                                                                                                                           |
| Velocity   | 79 %                                                                                                                                                                                   |
| Smoke Test | ✅ 10/10 pass (STR-002)                                                                                                                                                                 |

---

## What Went Well

- **WSL2 extraction delivered cleanly (US-050)**: `src/utils/network.py` extracted from `mongo_connector.py` in one step with zero regressions; `db_connector.py` now also uses the shared helper, closing the PostgreSQL WSL2 blind spot identified in Sprint 10 retro
- **PG admin-DB made configurable (US-052)**: sidebar text input added with `postgres` default; `pg_admin_db` session key initialised at app start; smoke test scenario 9 confirmed the default is in place on every launch
- **db_connector.py coverage lifted 80 % → 96 % (US-055)**: unit-level mocks for every PostgreSQL dialect branch closed the coverage gap without requiring Docker; the coverage gate (`≥ 80 %`) is now exceeded with headroom to spare
- **sslmode pre-validation shipped (US-056)**: `verify-ca` / `verify-full` selections now check for CA bundle existence before calling `create_engine`; failure surfaces in the sidebar with a clear error message rather than at connection time
- **CI Docker matrix job delivered (US-053)**: `.github/workflows/ci-cd.yml` now includes a `coverage-docker` job that runs `pytest -m docker` when Docker daemon is available; the Sprint 9 / Sprint 10 carry-over action item is finally closed
- **All 238 unit tests pass with 0 regressions** after Sprint 11 changes; coverage 96.32 % overall
- **Smoke tests introduced for the first time (STR-002)**: 10 scenarios covering app launch, DB type switching, MySQL flow, schema viewer, PostgreSQL sslmode, and MongoDB toggle — all green

---

## What Could Be Improved

- **US-051 sidebar mixin deferred (3 pts)**: the `RelationalConnectorSidebar` mixin refactor was identified as high-risk (large footprint change across sidebar.py, 238 tests) and deferred per CR-011; `sidebar.py` remains ~600 LoC with three near-parallel flows — carry over to Sprint 12
- **US-054 pyproject optional deps deferred (1 pt)**: `[project.optional-dependencies]` alignment requires an ADR to decide on the group structure; deferred to Sprint 12 backlog
- **No MQL execution smoke test yet**: Sprint 11 smoke suite does not cover MongoDB query execution (US-060) — that feature ships in Sprint 12 and must be added to Sprint 12's smoke file
- **Smoke test fixture discovery**: the `SchemaColumn` injection pattern for smoke tests was not in the developer guide; tests initially failed because plain strings were injected instead of `SchemaColumn` objects — the AppTest quirks section needs updating (also noted in STR-002 Notes for Retro)
- **Sprint velocity at 79 %** (11/14 pts): two stories deferred reduced the headline; however the deferred work was a deliberate risk-management decision, not a capacity issue

---

## Action Items

| Action                                                            | Owner            | Due                |
| ----------------------------------------------------------------- | ---------------- | ------------------ |
| Carry US-051 (`RelationalConnectorSidebar` mixin) into Sprint 12  | Scrum Master     | Sprint 12 day 1    |
| Carry US-054 (`pyproject.toml` optional deps) into Sprint 12      | Scrum Master     | Sprint 12 day 1    |
| Add Sprint 12 smoke test for MongoDB MQL execution (US-060)       | Smoke Test Agent | Sprint 12 Phase 8c |
| Update developer guide — AppTest `SchemaColumn` injection pattern | Developer        | Sprint 12 day 1    |
| Verify `coverage-docker` CI job runs green on first real PR       | DevOps           | Sprint 12          |

---

## Cumulative Velocity

| Sprint    | Committed | Delivered | Cumulative |
| --------- | --------- | --------- | ---------- |
| Sprint 1  | 21        | 21        | 21         |
| Sprint 2  | 21        | 21        | 42         |
| Sprint 3  | 13        | 13        | 55         |
| Sprint 4  | 16        | 16        | 71         |
| Sprint 5  | 16        | 16        | 87         |
| Sprint 6  | 28        | 28        | 115        |
| Sprint 7  | 15        | 15        | 130        |
| Sprint 8  | 11        | 11        | 141        |
| Sprint 9  | 14        | 14        | 155        |
| Sprint 10 | 13        | 13        | 168        |
| Sprint 11 | 14        | 11        | **179**    |
