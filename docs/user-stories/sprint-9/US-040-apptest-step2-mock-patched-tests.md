# US-040: Mock-Patched AppTest Tests for `_render_step2` Success and Failure Paths

**Epic**: EPIC-004 — Quality Assurance
**Sprint**: Sprint 9
**Points**: 5
**Priority**: Must Have
**Source**: Retro — SPRINT-8-retro.md Action Item 1

## User Story

> As a **developer**, I want mock-patched Streamlit AppTest tests covering `_render_step2`
> success and failure paths, so that the live-DB connection code branches in the sidebar
> are measurably exercised without requiring a real database.

## Acceptance Criteria

```gherkin
Feature: AppTest coverage for sidebar Step 2

  Scenario: Successful MySQL engine creation
    Given the app is rendered with valid Step 1 credentials in session state
    When create_engine() and detect_live_schema() are mocked to succeed
    And the user has already completed Step 1 connection
    Then the Step 2 panel is rendered without error
    And session_state["detected_schema"] is populated
    And session_state["_db_password"] is cleared after engine creation

  Scenario: Failed MySQL engine creation
    Given the app is rendered with credentials in session state
    When create_engine() is mocked to raise an OperationalError
    Then an error banner is shown in the UI
    And session_state["detected_schema"] is empty or absent

  Scenario: Spinner text during connection
    Given the app is rendered at the Step 2 stage
    When the schema detection mock takes > 0 ms
    Then the spinner component is present in the rendered output
```

## Technical Notes

- Use `unittest.mock.patch` to mock `src.services.db_connector.DBConnector.connect` and
  `src.services.schema_detector.SchemaDetector.detect_live_schema` at the module level.
- Patch target must match the import path used inside `sidebar.py`
  (e.g. `src.components.sidebar.DBConnector`).
- Set `default_timeout=10` on `AppTest.from_file()` to avoid the 3-second default timeout.
- Use `at.session_state["key"]` (not `.get()`) for session state assertions.
- Do NOT chain `.set_value()` and `.run()` — call them as separate statements.
- Test file: `tests/unit/test_sidebar_step2.py`

## Definition of Done

- [x] Code implemented
- [x] Unit tests written and passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Coverage gate ≥ 80% (target: raise `src/components/sidebar.py` measurable branches)
- [x] Docs updated

## Status

✅ Done
