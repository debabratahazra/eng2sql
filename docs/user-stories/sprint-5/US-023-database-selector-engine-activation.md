# US-023: Step 2 — Database Selector & Engine Activation

**Epic**: EPIC-006
**Sprint**: Sprint 5
**Points**: 5
**Priority**: Must Have

## User Story

> As a **user**, after the server connection is established, I want to select a
> database from a dropdown and click **Select Database** so that the tool connects
> to that specific database and I can start generating SQL against its live schema.

## Acceptance Criteria

```gherkin
Feature: Step 2 — Database Selector & Engine Activation

  Scenario: Dropdown shows discovered databases
    Given Step 1 connected successfully and found databases ["myapp_db", "analytics_db"]
    When the sidebar renders Step 2
    Then a selectbox appears with options ["myapp_db", "analytics_db"]
    And a "Select Database" button appears below the dropdown

  Scenario: Selecting a database activates the engine
    Given the database dropdown shows available databases
    When I choose "myapp_db" and click "Select Database"
    Then a new SQLAlchemy engine is created for "mysql+pymysql://…/myapp_db"
    And "db_engine" in session state is set to the new engine
    And "selected_database" in session state is set to "myapp_db"
    And the schema is auto-detected and stored in "detected_schema"
    And a success status shows "✅ Using database: myapp_db"

  Scenario: Schema viewer reflects the selected database
    Given I have selected a database and the schema was auto-detected
    When the main page renders
    Then the Schema Viewer panel shows tables from "myapp_db"
    And the SQL generator uses the live schema from "myapp_db"

  Scenario: Changing the selected database re-detects schema
    Given I am already using "myapp_db"
    When I select "analytics_db" and click "Select Database"
    Then a new engine is created for "analytics_db"
    And "detected_schema" is refreshed to reflect "analytics_db" tables
    And the schema viewer updates accordingly

  Scenario: Step 2 is hidden until Step 1 succeeds
    Given Step 1 has not been completed or has failed
    When the sidebar renders
    Then the database dropdown and "Select Database" button are not visible

  Scenario: No accessible databases shows a warning
    Given the MySQL user has SHOW DATABASES privilege but all results are system databases
    When Step 1 completes
    Then a warning shows "⚠️ No accessible databases found for this user"
    And the "Select Database" button is absent
```

## Technical Notes
- Render the Step 2 block only when `st.session_state.get("available_databases")` is
  a non-empty list
- Use `st.selectbox("Select a database", options=available_databases)` for the dropdown
- On "Select Database" click: call `DBConnector.create_engine(config_with_db)` with
  the chosen database name, then `SchemaDetector.detect_live_schema(engine)`
- Store results: `st.session_state["db_engine"]`, `st.session_state["selected_database"]`,
  `st.session_state["detected_schema"]`
- The main window (`app.py`) reads `st.session_state["db_engine"]` and
  `st.session_state["detected_schema"]`; if both are set, enable the Generate SQL flow
- Show `st.warning("⚠️ No accessible databases found for this user")` when
  `available_databases` is an empty list

## Definition of Done
- [ ] `src/components/sidebar.py` — Step 2 block implemented
- [ ] `src/app.py` — SQL generation gated on `db_engine` and `detected_schema` being set
- [ ] Schema viewer populates from `detected_schema` after database selection
- [ ] Changing database triggers schema refresh
- [ ] `ruff` and `mypy` clean
- [ ] Code review approved

## Status
✅ Done
