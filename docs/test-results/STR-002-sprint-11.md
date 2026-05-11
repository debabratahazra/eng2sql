# STR-002 — Sprint 11 Smoke Test Result

**Sprint**: Sprint 11 — Refactor & Hardening
**Date**: 2026-05-07
**Agent**: Smoke Test Agent
**Test file**: `tests/smoke/test_sprint_11_smoke.py`
**Run command**: `python -m pytest tests/smoke/test_sprint_11_smoke.py -v -m smoke`

---

## Summary

| Metric                          | Value      |
| ------------------------------- | ---------- |
| Total smoke tests               | 10         |
| Passed                          | 10 ✅       |
| Failed                          | 0          |
| Errors                          | 0          |
| Duration                        | ~18 s      |
| Baseline unit tests (pre-smoke) | 238 passed |

**Overall result: ✅ ALL SMOKE TESTS PASSED**

---

## Test Results

| #   | Test                                                  | Result | Notes                                                             |
| --- | ----------------------------------------------------- | ------ | ----------------------------------------------------------------- |
| 1   | `test_smoke_app_launches_without_error`               | ✅ PASS | App initialises cleanly                                           |
| 2   | `test_smoke_sidebar_renders_db_selector`              | ✅ PASS | Radio with MySQL / PostgreSQL / MongoDB                           |
| 3   | `test_smoke_mysql_sql_generation_with_mock`           | ✅ PASS | OpenAI mocked; schema injected with proper `SchemaColumn` objects |
| 4   | `test_smoke_empty_query_does_not_crash`               | ✅ PASS | No exception on empty input                                       |
| 5   | `test_smoke_schema_viewer_appears_after_schema_load`  | ✅ PASS | Expander renders with 1-table schema                              |
| 6   | `test_smoke_sql_output_panel_renders`                 | ✅ PASS | Output panel (placeholder) renders                                |
| 7   | `test_smoke_progress_tracker_present`                 | ✅ PASS | Progress tracker wired in `main()`                                |
| 8   | `test_smoke_postgresql_form_renders_sslmode_selector` | ✅ PASS | sslmode selectbox present after switching to PostgreSQL           |
| 9   | `test_smoke_pg_admin_db_session_key_initialised`      | ✅ PASS | `pg_admin_db` defaults to `'postgres'` (US-052)                   |
| 10  | `test_smoke_mongodb_uri_mode_toggle_renders`          | ✅ PASS | MongoDB mode switch renders without error                         |

---

## Inline Fix Applied

**Issue detected during development**: Tests 3 and 5 initially failed with
`AttributeError: 'str' object has no attribute 'name'` because the test fixtures
injected `detected_schema` as `dict[str, list[str]]` (plain column-name strings)
while `schema_viewer.py` expects `dict[str, list[SchemaColumn]]` objects.

**Fix**: Updated the smoke test fixtures to inject `SchemaColumn` dataclass instances
with `name`, `type`, `nullable`, `primary_key` fields matching the live schema format.
No production code was changed.

---

## Sprint-11-Specific Coverage

| Story  | Feature                                     | Smoke scenario                                      |
| ------ | ------------------------------------------- | --------------------------------------------------- |
| US-050 | WSL2 helper extracted to `utils/network.py` | App launches without error (scenario 1)             |
| US-052 | Configurable PG admin-DB                    | `pg_admin_db` defaults to `'postgres'` (scenario 9) |
| US-056 | sslmode `verify-*` pre-validation           | sslmode selectbox present (scenario 8)              |
| US-053 | CI Docker matrix                            | Not applicable to smoke scope (CI artefact)         |
| US-055 | db_connector.py coverage lift               | Not applicable to smoke scope (unit coverage)       |

---

## Notes for Retro

- **Positive**: All 10 smoke scenarios pass cleanly; app launch, DB type switching, MySQL flow, schema viewer, and PostgreSQL form all healthy.
- **Positive**: Sprint-11 changes (WSL2 extraction, PG admin-DB, sslmode selector) do not break any smoke journeys.
- **Observation**: Smoke test fixtures must inject `SchemaColumn` objects (not plain strings) — add this pattern to the developer guide's AppTest quirks section.
- **Observation**: No MongoDB MQL execution smoke test yet — this is Sprint-12 scope (US-060).
- **Observation**: `pyproject.toml` `addopts` now excludes both `integration` and `smoke` by default — developer guide should reflect this.
