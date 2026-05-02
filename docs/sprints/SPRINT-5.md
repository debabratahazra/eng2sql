# Sprint 5 Plan

**Goal**: Replace static-vs-live schema mode with a two-step MySQL-only connection flow — connect to server, discover databases, select database, auto-detect schema
**Duration**: 2026-07-01 → 2026-07-14 (2 weeks)
**Velocity Target**: 16 points
**Epic**: EPIC-006 — Live DB Connection: Database Discovery & Selector

---

## Committed Stories

| Story ID | Title                                                 | Points | Assignee (Agent) |
| -------- | ----------------------------------------------------- | ------ | ---------------- |
| US-021   | Remove Static Schema Mode & MySQL-Only Sidebar        | 3      | Developer        |
| US-022   | Step 1 — Server Connect & Database Discovery          | 5      | Developer        |
| US-023   | Step 2 — Database Selector & Engine Activation        | 5      | Developer        |
| US-024   | `DBConnector.list_databases()` Service Method & Tests | 3      | Developer        |

**Total**: 16 points

---

## Definition of Done

- [x] Static schema radio option and all related code removed from `sidebar.py` and `app.py`
- [x] Step 1: host/port/user/password form + Connect button → `SHOW DATABASES` result
- [x] Step 2: database dropdown + Select Database button → engine activated, schema detected
- [x] `DBConnector.list_databases()` implemented with unit tests, 100% branch coverage
- [x] All 40+ existing tests still pass (no regressions)
- [x] New unit tests for `list_databases()` in `tests/unit/test_db_connector.py`
- [ ] `ruff check` and `mypy src/` both exit 0
- [ ] `pytest --cov=src --cov-fail-under=80` passes
- [ ] `docs/guides/user-guide.md` updated to reflect two-step flow
- [ ] `docs/guides/developer-guide.md` updated with new session-state keys and service method
- [ ] `README.md` updated — static schema references removed
- [ ] Code review completed (CR-005)

---

## Sprint Risks

| Risk                                                           | Likelihood | Impact | Mitigation                                                                                    |
| -------------------------------------------------------------- | ---------- | ------ | --------------------------------------------------------------------------------------------- |
| `SHOW DATABASES` returns no results for restricted MySQL user  | Medium     | Medium | Show `st.warning("⚠️ No accessible databases found")` gracefully; no crash                     |
| Engine reconnection for Step 2 causes duplicate pool entries   | Low        | Medium | Call `db_server_engine.dispose()` before creating the Step 2 engine; or reuse and switch URL  |
| Streamlit re-run loop causes double Connect clicks             | Medium     | Low    | Guard with `if st.session_state.get("db_server_engine") is None` before connecting            |
| Removing static mode breaks existing unit tests that mock it   | Low        | Low    | All existing mocks target services, not the sidebar mode; no breakage expected                |
| `SHOW DATABASES` is MySQL-specific; SQLite tests cannot use it | High       | Low    | Use `unittest.mock.MagicMock` in unit tests; integration tests use SQLite without this method |

---

## Session State Changes

### Added in Sprint 5

| Key                   | Type             | Set By                          | Description                          |
| --------------------- | ---------------- | ------------------------------- | ------------------------------------ |
| `db_server_engine`    | `Engine \| None` | US-022 — Step 1 Connect click   | Server-level engine (no DB selected) |
| `available_databases` | `list[str]`      | US-022 — after list_databases() | Non-system databases on the server   |
| `selected_database`   | `str`            | US-023 — Step 2 Select click    | Database name chosen in dropdown     |

### Removed in Sprint 5

| Key    | Removed By | Reason                                      |
| ------ | ---------- | ------------------------------------------- |
| `mode` | US-021     | No longer needed — only one connection mode |

### Unchanged

| Key               | Used By                                         |
| ----------------- | ----------------------------------------------- |
| `db_engine`       | US-023, app.py — full DB engine (Step 2 result) |
| `detected_schema` | US-023, schema viewer, SQL generator            |
| `generated_sql`   | app.py                                          |
| `query_result`    | app.py                                          |

---

## Outcome

**Status**: ✅ DONE
**Actual Velocity**: 16 / 16 points
**Notes**: All 4 stories delivered. 48 tests pass (8 new unit tests for `list_databases()`). 91% coverage. Code review CR-005 approved. Static schema mode fully removed. Two-step MySQL connection flow operational.
