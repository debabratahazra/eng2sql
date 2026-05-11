# US-026: MongoDB Database Discovery & Selection

**Epic**: EPIC-007
**Sprint**: Sprint 6
**Points**: 5
**Priority**: Must Have

## User Story

> As a **user**, after connecting to a MongoDB server I want to see a dropdown of all
> available databases (excluding system databases) so that I can select one and
> finalise the connection, triggering schema detection on the chosen database.

## Acceptance Criteria

```gherkin
Feature: MongoDB Database Discovery & Selection

  Scenario: Successful connect shows database dropdown
    Given the user has selected "MongoDB" and filled in valid credentials
    When the user clicks "Connect"
    Then a success message shows "✅ Connected to <host> — <N> databases found"
    And a database dropdown lists all non-system databases

  Scenario: System databases are excluded from dropdown
    Given the MongoDB server has databases: admin, local, config, mydb, analytics
    When the user successfully connects
    Then only "mydb" and "analytics" appear in the dropdown
    And "admin", "local", "config" are excluded

  Scenario: Selecting a database detects its schema
    Given the database dropdown is visible
    When the user selects "mydb" and clicks "✅ Select Database"
    Then the app connects to that database
    And schema detection runs against all collections
    And a success message shows "✅ mydb selected — <N> collections detected"
    And st.session_state["detected_schema"] is populated

  Scenario: Connection failure shows error
    Given the user provides invalid MongoDB credentials
    When the user clicks "Connect"
    Then an error message is displayed
    And no database dropdown appears
    And st.session_state["mongo_client"] remains None

  Scenario: No accessible databases shows warning
    Given the MongoDB user has no accessible non-system databases
    When the user connects
    Then a warning "⚠️ No accessible databases found" is displayed
```

## Technical Notes
- Step 1 stores `MongoClient` in `st.session_state["mongo_client"]`
- Step 1 stores database list in `st.session_state["mongo_available_databases"]`
- Step 2 stores selected name in `st.session_state["mongo_selected_database"]`
- Step 2 stores `pymongo.database.Database` in `st.session_state["mongo_db"]`
- Step 2 stores detected schema in `st.session_state["detected_schema"]` (shared key with MySQL)
- System databases to exclude: `{"admin", "local", "config"}`

## Definition of Done
- [x] Code implemented
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated (if needed)

## Status
✅ Done
