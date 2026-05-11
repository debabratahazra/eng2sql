# US-021: Remove Static Schema Mode & MySQL-Only Sidebar

**Epic**: EPIC-006
**Sprint**: Sprint 5
**Points**: 3
**Priority**: Must Have

## User Story

> As a **user**, I want the sidebar to show only the MySQL Live Database connection
> option so that the interface is simpler and I am never confused about which schema
> mode is active.

## Acceptance Criteria

```gherkin
Feature: Remove Static Schema Mode

  Scenario: Static Schema radio option is gone
    Given the Streamlit application is running
    When I open the sidebar
    Then I do not see a "Static Schema" option
    And I do not see a mode-selection radio button at all
    And the sidebar immediately shows the MySQL connection form

  Scenario: No YAML schema loading on page load
    Given the application starts
    When the main page renders
    Then no YAML file is read from disk
    And the schema viewer is empty until a database is selected

  Scenario: session_state "mode" key is no longer used
    Given the application is running
    When I inspect session state
    Then the key "mode" is absent from st.session_state
    And all conditional logic based on "mode" is removed

  Scenario: Sidebar header reflects the single mode
    Given the sidebar is rendered
    Then the connection type label reads "🔌 MySQL Live Database"
    And there is no radio button or toggle for switching modes
```

## Technical Notes
- Delete the `st.radio("Schema Mode", ...)` call and all branches depending on it
  in `src/components/sidebar.py`
- Remove the `_render_static_info()` / static `st.info()` block in `sidebar.py`
- Remove any `static_schema_path` loading logic from `src/app.py`
- Remove `"mode"` from `_initialise_session_state()` defaults in `app.py`
- `SidebarComponent.render()` now always calls `_render_db_form()` — no conditional

## Definition of Done
- [x] `src/components/sidebar.py` — radio and static branch removed
- [x] `src/app.py` — static schema loading removed; `mode` session-state key removed
- [x] All existing tests still pass
- [x] `ruff` and `mypy` clean
- [x] Code review approved

## Status
✅ Done
