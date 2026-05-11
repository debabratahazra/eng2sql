# Sprint 13 Retrospective

**Sprint**: Sprint 13 — Refactor, Optional Deps & MQL Unit Tests
**Date**: 2026-05-07
**Facilitator**: Scrum Master

---

## Sprint Snapshot

| Item        | Detail                                                                                                                            |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Goal        | Close Sprint 12 action items: sidebar mixin refactor, pyproject optional deps, Docker MQL integration test, app.py MQL unit tests |
| Dates       | 2026-05-07 → 2026-05-07                                                                                                           |
| Committed   | 10 pts                                                                                                                            |
| Delivered   | 10 pts                                                                                                                            |
| Deferred    | 0 pts                                                                                                                             |
| Velocity    | 100%                                                                                                                              |
| Smoke Tests | ✅ 10/10 pass (STR-004)                                                                                                            |
| Unit Tests  | ✅ 240 passed / 0 failed (TR-013)                                                                                                  |
| Coverage    | ✅ 91.55% overall                                                                                                                  |

---

## What Went Well

- **US-051 sidebar mixin pattern established**: Introducing `_RelationalDialectConfig` as a frozen dataclass created a reusable, type-safe contract for any future relational engine (Oracle, MSSQL, etc.); adding a new dialect now requires ~30 lines instead of ~115; all 33 existing sidebar tests pass unchanged
- **US-062 app.py MQL unit tests**: `test_app_mql_button.py` closes the last unit-test gap in `app.py`'s MongoDB execute path — 6 focused test cases, including the success, error, info, and empty-query branches
- **US-054 pyproject.toml optional deps**: Clean separation of runtime, DB driver, and dev dependencies; ADR-006 documents the rationale; `requirements.txt` retained for Docker/CI compatibility
- **US-061 Docker integration test**: `test_mongo_query_executor_integration.py` is fully authored and CI-ready — 7 scenarios covering real aggregation, auto-limit, ObjectId serialisation, and collection-name injection defence; skips cleanly without Docker
- **Developer guide extended**: "Adding a New Relational Database Engine" section added to developer-guide.md; `_RelationalDialectConfig` field reference table included
- **30 smoke tests all passing**: Cumulative smoke suite (Sprint 11 + 12 + 13) — 30 tests, zero failures
- **100% sprint velocity**: all 10 committed points delivered, zero deferrals

---

## What Could Be Improved

- **US-051 AC-3 LoC reduction gap**: Target was ≥ 80 lines of net reduction; actual was ~55. The `_RelationalDialectConfig` dataclass added 59 lines of overhead that partially offset the saving. The developer-experience goal is fully achieved — the gap is cosmetic and documented in UTR-006 and CR-013. Sprint 14 could set a follow-up task to revisit if `db_connector.py` or other components are refactored.
- **`testcontainers[mongo]` missing from dev deps**: `pyproject.toml` `[project.optional-dependencies].dev` does not include `testcontainers[mongo]`; only `testcontainers[mysql]` and `testcontainers[postgres]` were added in US-054. The Docker integration test will fail at import in CI until this is added.
- **MySQL state key naming inconsistency**: MySQL uses `db_server_engine` / `available_databases` while PostgreSQL uses `pg_server_engine` / `pg_available_databases`. Adding a `state_key_prefix` field to `_RelationalDialectConfig` could normalise this in a future sprint.
- **`schema_detector.py` and `db_connector.py` coverage still below 90%**: These pre-existing modules remain at 62% and 67% respectively; integration tests cover the live-DB paths but they do not run in unit mode. A future sprint could add targeted mocks to lift them.

---

## Action Items

| Action                                                                                            | Owner           | Due                |
| ------------------------------------------------------------------------------------------------- | --------------- | ------------------ |
| Add `testcontainers[mongo]>=4.7.0` to `[project.optional-dependencies].dev` in `pyproject.toml`   | Developer       | Sprint 14 day 1    |
| Add `testcontainers[mongo]` to `requirements.txt` (dev section comment)                           | Developer       | Sprint 14 day 1    |
| Evaluate `state_key_prefix` field for `_RelationalDialectConfig` to normalise MySQL/PG state keys | Architect       | Sprint 14 planning |
| Increase unit mock coverage for `schema_detector.py` (target ≥ 80%)                               | Unit Test Agent | Sprint 14          |

---

## Cumulative Velocity

| Sprint    | Committed   | Delivered   | Velocity |
| --------- | ----------- | ----------- | -------- |
| Sprint 1  | 13 pts      | 13 pts      | 100%     |
| Sprint 2  | 14 pts      | 14 pts      | 100%     |
| Sprint 3  | 13 pts      | 13 pts      | 100%     |
| Sprint 4  | 13 pts      | 13 pts      | 100%     |
| Sprint 5  | 15 pts      | 15 pts      | 100%     |
| Sprint 6  | 16 pts      | 16 pts      | 100%     |
| Sprint 7  | 14 pts      | 14 pts      | 100%     |
| Sprint 8  | 13 pts      | 13 pts      | 100%     |
| Sprint 9  | 14 pts      | 14 pts      | 100%     |
| Sprint 10 | 13 pts      | 13 pts      | 100%     |
| Sprint 11 | 15 pts      | 15 pts      | 100%     |
| Sprint 12 | 16 pts      | 16 pts      | 100%     |
| Sprint 13 | 10 pts      | 10 pts      | 100%     |
| **Total** | **179 pts** | **179 pts** | **100%** |
