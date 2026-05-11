# US-038: AppTest-Based Sidebar UI Tests (Mode Toggle & Connection Forms)

**Epic**: EPIC-004
**Sprint**: Sprint 8
**Points**: 5
**Priority**: Should Have
**Source**: Retro — SPRINT-7-retro.md (carried from SPRINT-4, SPRINT-5, SPRINT-6 retros)

## User Story

> As a **developer**, I want Streamlit `AppTest`-based tests for the sidebar's mode toggle
> and connection forms, so that UI widget interactions are validated by the automated test
> suite without needing a running browser.

## Acceptance Criteria

```gherkin
Feature: AppTest sidebar UI coverage

  Scenario: MySQL engine is selected by default
    Given the app is loaded via AppTest
    When no session state is set
    Then the engine radio shows "MySQL" as selected
    And the MySQL connection form fields are visible

  Scenario: Switching engine selector to MongoDB shows MongoDB form
    Given the app is loaded via AppTest
    When the engine radio is set to "MongoDB"
    Then the MongoDB Step 1 form is rendered
    And MySQL-specific fields are no longer visible

  Scenario: MongoDB connection input mode toggle works
    Given the app is in MongoDB mode via AppTest
    When the input mode radio is set to "URI + Credentials"
    Then the URI text input field is rendered
    And the individual host/port/username fields are hidden

  Scenario: MongoDB field mode is default
    Given the app is in MongoDB mode via AppTest
    When the input mode radio is set to "Fields (host / port / auth)"
    Then the host, port, username, and password inputs are rendered
    And the URI text input is hidden

  Scenario: Connect button triggers Step 2 in MySQL mode
    Given the app is loaded via AppTest in MySQL mode
    And host, port, username, password fields are filled
    When the "Connect & List Databases" button is clicked
    Then session state `db_server_engine` is set
    And the Step 2 database selector section renders
```

## Technical Notes
- Use `streamlit.testing.v1.AppTest` (available from Streamlit 1.28+)
- Test file: `tests/unit/test_sidebar_ui.py`
- Mock `DBConnector.list_databases()` and `MongoDBConnector.list_databases()` so no real DB is needed
- The `AppTest` pattern: `at = AppTest.from_file("src/app.py"); at.run()`
- Adjust `PYTHONPATH` in conftest if needed so `src/` modules resolve correctly
- This story was deferred from Sprint 4 (BUG-001), Sprint 5, Sprint 6, and Sprint 7 retros

## Definition of Done
- [x] Code implemented (`tests/unit/test_sidebar_ui.py` created with 9 AppTest-based tests)
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated (`pyproject.toml` coverage omit updated — `src/components/*` removed)

## Status
✅ Done
