# Sprint 12 Retrospective

**Sprint**: Sprint 12 — MQL Query Execution & Dynamic Label
**Date**: 2026-05-07
**Facilitator**: Scrum Master

---

## Sprint Snapshot

| Item       | Detail                                                                                                                                  |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Goal       | Deliver end-to-end MQL query execution from the Streamlit UI — MongoDB gets the same execute→results experience as MySQL and PostgreSQL |
| Dates      | 2026-05-07 → 2026-05-07                                                                                                                 |
| Committed  | 16 pts                                                                                                                                  |
| Delivered  | 16 pts                                                                                                                                  |
| Deferred   | 0 pts                                                                                                                                   |
| Velocity   | 100 %                                                                                                                                   |
| Smoke Test | ✅ 10/10 pass (STR-003)                                                                                                                  |
| Unit Tests | ✅ 234 passed / 0 failed (TR-012)                                                                                                        |
| Coverage   | ✅ 91.55 % overall                                                                                                                       |

---

## What Went Well

- **MongoQueryExecutor delivered with 100 % coverage (US-059)**: The new service module achieved 100 % line coverage (30 tests); security contract (no `eval()`, collection-name regex, auto-limit guard) fully documented in module docstring
- **Dynamic MQL/SQL label shipped cleanly (US-057)**: `SQLOutputComponent.render()` extended with `db_type` parameter while preserving full backward compatibility — all MySQL and PostgreSQL callers are unchanged; 9 unit tests confirm every label branch
- **MongoDB LLM system prompt structured output (US-058)**: `sql_generator.py` now includes JSON-object instructions for the MongoDB dialect, with an explicit prohibition on JS shell syntax; verified by existing `test_sql_generator.py` assertions
- **Execute MQL button wired end-to-end (US-060)**: `app.py` routes MongoDB executions through `MongoQueryExecutor` — button visible when `mongo_db is not None`, info-box shown otherwise; smoke test scenario 5/6/7 all green
- **BUG-007 multi-host URI fix**: `_is_multi_host()` now correctly strips credentials from netloc before scanning for commas — replica-set seed-list URIs no longer raise `ValueError`
- **BUG-008 system.profile auth guard**: two-layer defence (pre-filter `system.` + per-collection `OperationFailure` guard) prevents schema detection from aborting when the user lacks `dbAdmin`
- **Sprint 12 smoke test suite (STR-003)**: 10 scenarios covering all new US-057–060 paths plus Sprint 11 regressions; "Generated MQL" label, Execute MQL info-box path, and button click scenario all confirmed
- **100 % sprint velocity**: all 16 committed points delivered, zero deferrals

---

## What Could Be Improved

- **No live-MongoDB integration test for `MongoQueryExecutor`**: Sprint 12 had 100 % unit mock coverage but no live-DB integration test; the `execute()` path against a real `mongod` has never been exercised in CI — deferred to Sprint 13 as a Docker integration test
- **US-051 sidebar mixin still deferred (carry from Sprint 11)**: `sidebar.py` remains ~600 LoC; the `RelationalConnectorSidebar` mixin refactor was not included in Sprint 12 because it was already a full 16-pt sprint — must ship in Sprint 13
- **US-054 pyproject optional deps still deferred (carry from Sprint 11)**: Optional deps group structure still needs an ADR; carry to Sprint 13
- **Developer guide missing AppTest `SchemaColumn` injection pattern**: sprint 11 retro identified this action item; it was not completed during Sprint 12 — still needed before next developer onboards
- **`app.py` not fully unit-tested**: `app.py` business logic (the Execute MQL wiring) is covered only by smoke tests, not by isolated unit tests; a dedicated `test_app_mql_button.py` would increase confidence and close the last gap in direct unit coverage

---

## Action Items

| Action                                                                             | Owner                  | Due             |
| ---------------------------------------------------------------------------------- | ---------------------- | --------------- |
| Add live-MongoDB Docker integration test for `MongoQueryExecutor`                  | Integration Test Agent | Sprint 13       |
| Carry US-051 (`RelationalConnectorSidebar` mixin — 3 pts) into Sprint 13           | Scrum Master           | Sprint 13 day 1 |
| Carry US-054 (`pyproject.toml` optional deps — 1 pt) into Sprint 13                | Scrum Master           | Sprint 13 day 1 |
| Update `docs/guides/developer-guide.md` — AppTest `SchemaColumn` injection pattern | Developer              | Sprint 13 day 1 |
| Add `test_app_mql_button.py` unit tests for `app.py` Execute MQL paths             | Unit Test Agent        | Sprint 13       |

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
| Sprint 11 | 14        | 11        | 179        |
| Sprint 12 | 16        | 16        | **195**    |
