# US-045: Sidebar — PostgreSQL Connect Form with sslmode Selector

**Epic**: EPIC-009 — PostgreSQL Live Connection Support
**Sprint**: Sprint 10
**Points**: 3
**Priority**: Must Have
**Source**: PostgreSQL evaluation §3 (US-B) — promoted by Retro Analyzer

## User Story

> As a **user**, I want to pick "PostgreSQL" from the sidebar database-type radio and
> see a familiar two-step connect form (Step 1 connect → Step 2 select database), so
> that I can connect to my PostgreSQL server without learning a new UI.

## Acceptance Criteria

```gherkin
Feature: PostgreSQL sidebar connect form

  Scenario: Radio includes PostgreSQL between MySQL and MongoDB
    Given the user opens the app
    When the sidebar Configuration section is rendered
    Then the db_type radio shows ["MySQL", "PostgreSQL", "MongoDB"]

  Scenario: Selecting PostgreSQL renders the PostgreSQL form
    Given the user picks "PostgreSQL"
    Then the form shows fields: Host, Port (default 5432), User, Password, sslmode
    And the sslmode selectbox defaults to "prefer"
    And no MySQL-specific fields are visible

  Scenario: Switching db_type clears downstream session state
    Given the user previously connected with MySQL (session has db_engine, detected_schema)
    When the user switches the radio to PostgreSQL
    Then db_engine, detected_schema, and selected_database are cleared from session_state

  Scenario: Step 1 Connect succeeds and populates pg_available_databases
    Given valid PostgreSQL credentials
    When the user clicks Connect
    Then DBConnector.create_engine is called with dialect="postgresql"
    And session_state["pg_available_databases"] contains the user databases
    And system DBs ("postgres", "template0", "template1") are filtered out

  Scenario: Step 2 Select Database stores db_engine and triggers schema detection
    Given Step 1 succeeded
    When the user picks a database and clicks Select Database
    Then session_state["db_engine"] is the live PostgreSQL engine
    And session_state["detected_schema"] is populated by SchemaDetector
    And session_state["_pg_password"] is removed

  Scenario: Connect failure surfaces error
    Given invalid credentials
    When the user clicks Connect
    Then step1_status is ("error", message)
    And no engine is stored
```

## Technical Notes

- New methods in `src/components/sidebar.py`:
  - `_render_pg_step1()` — mirrors `_render_step1` for PostgreSQL.
  - `_render_pg_step2()` — mirrors `_render_step2` for PostgreSQL.
- New session state keys (per SPRINT-10.md):
  - `pg_host`, `pg_port`, `pg_user`, `_pg_password`, `pg_sslmode`,
    `pg_server_engine`, `pg_available_databases`, `pg_selected_database`
- Reuse the existing `DBConnector` (from US-046) — sidebar should not branch on dialect
  except for form rendering.
- App wiring (`src/app.py`): when `db_type == "PostgreSQL"`, behave the same as MySQL
  (forwarded to `SQLGenerator` with dialect="PostgreSQL" — see US-047).
- AppTest coverage: add mock-patched tests in `tests/unit/test_sidebar_postgresql.py`
  mirroring the US-040 `test_sidebar_step2.py` pattern.

## Definition of Done

- [x] `_render_pg_step1` and `_render_pg_step2` implemented
- [x] `db_type` radio includes "PostgreSQL"
- [x] All 6 new session state keys initialised in `app.py` startup
- [x] Switching radio clears downstream state (no leakage between dialects)
- [x] 6+ AppTest tests in `tests/unit/test_sidebar_postgresql.py` covering the scenarios
- [x] Existing MySQL + MongoDB AppTest suites still pass (zero regressions)
- [x] Code review CR-010 approved
- [x] User-guide screenshot or walkthrough updated (US-049)

## Status

✅ Done
