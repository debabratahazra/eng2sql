# US-052 — Configurable PostgreSQL Step 1 admin database

**Sprint**: Sprint 11
**Source**: SPRINT-10-retro.md "What Could Be Improved" §3
**Points**: 2
**Owner**: Developer

## User Story

As a **user connecting to a managed PostgreSQL service** (Azure Single Server, certain
hardened RDS images) where the default `postgres` admin database is disabled, I want to
override the Step 1 admin DB name in the sidebar so I can list user databases via a
database I actually have `CONNECT` privilege on.

## Acceptance Criteria

1. Sidebar PostgreSQL Step 1 form has a new optional text input **Admin DB** with
   default value `postgres` and a tooltip explaining "Database used solely to enumerate
   other databases. Override if your provider has disabled `postgres`."
2. Session-state key `pg_admin_db` initialised in `app.py` `_initialise_session_state`.
3. Step 1 `Connect` builds the `DBConfig` with `database=session_state["pg_admin_db"]`
   instead of the hard-coded `"postgres"`.
4. Validation: empty value rejected with the warning "Admin DB cannot be empty."
5. At least 2 new sidebar AppTest tests covering: default `postgres` works as before;
   custom value (`"defaultdb"`) is propagated into `DBConfig.database`.

## Definition of Done

- [x] New `Admin DB` text input rendered in PG Step 1
- [x] `pg_admin_db` session-state key initialised
- [x] Validation rejects empty admin DB
- [x] 2+ AppTest tests added
- [x] User guide updated with new field + use-case example
- [x] CR-011 approved

## Status

✅ Done
