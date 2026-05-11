# US-051 — Refactor sidebar — `RelationalConnectorSidebar` mixin

**Sprint**: Sprint 13 (carried from Sprint 11 + Sprint 12)
**Source**: SPRINT-10-retro.md "What Could Be Improved" §2 → SPRINT-11-retro.md Action Item → SPRINT-12-retro.md Action Item
**Points**: 3
**Owner**: Developer

## User Story

As a **developer adding the next relational engine** (Oracle, MSSQL, etc.), I want the
MySQL and PostgreSQL sidebar flows to share a `RelationalConnectorSidebar` mixin so I
can add a new dialect by registering ~30 LoC instead of copy-pasting ~150 LoC of
near-identical Step 1 / Step 2 code.

## Acceptance Criteria

1. New helper class or set of methods consolidates the duplicated Step 1 / Step 2 logic
   between `_render_step1`/`_render_step2` (MySQL) and `_render_pg_step1`/`_render_pg_step2`
   (PostgreSQL). The shared core handles: form rendering, `Connect` button click,
   `create_engine` + `list_databases`, `db_select` + `db_confirm`, schema detection,
   password clearing, status display.
2. Per-dialect specifics are passed as a small config object: prefix (`db`/`pg`),
   default port, dialect string, extra kwargs (e.g. `sslmode`).
3. Net `sidebar.py` LoC reduction ≥ 80 lines.
4. **Zero behavioural change** — all existing `tests/unit/test_sidebar_*.py` tests pass
   unchanged (`test_sidebar_step2.py`, `test_sidebar_postgresql.py`, `test_sidebar_ui.py`).
5. MongoDB branch is left untouched (it has its own URI mode + auth-mechanism complexity).

## Definition of Done

- [x] `sidebar.py` LoC reduced by ≥ 80 lines
- [x] All existing sidebar tests pass without modification
- [x] No new public class added to the `components` package public surface
- [x] Developer guide section "Adding a new relational engine" added
- [x] Code review approved (CR-013)
- [x] Code coverage on `sidebar.py` does not drop

## Status

✅ Done
