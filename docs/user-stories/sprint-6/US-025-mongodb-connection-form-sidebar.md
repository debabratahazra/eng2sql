# US-025: MongoDB Connection Form in Sidebar

**Epic**: EPIC-007
**Sprint**: Sprint 6
**Points**: 5
**Priority**: Must Have

## User Story

> As a **user**, I want a "Database type" radio button in the sidebar so that I can
> switch between MySQL and MongoDB, and when I choose MongoDB I see a tailored
> connection form (host, port, username, password, auth source, auth mechanism)
> that lets me click **Connect** to reach the MongoDB server.

## Acceptance Criteria

```gherkin
Feature: MongoDB Connection Form in Sidebar

  Scenario: Radio button renders with MySQL as default
    Given the Streamlit app is loaded
    When the sidebar is rendered
    Then a "Database type" radio with options "MySQL" and "MongoDB" is visible
    And "MySQL" is selected by default

  Scenario: Switching to MongoDB renders MongoDB-specific fields
    Given the sidebar shows the MySQL form
    When the user selects "MongoDB" in the radio
    Then the Port field defaults to 27017
    And "Auth Source" (default "admin") and "Auth Mechanism" fields appear
    And the MySQL Port default of 3306 is no longer shown

  Scenario: Switching database type clears downstream state
    Given the user is connected to MySQL with databases listed
    When the user switches the radio to "MongoDB"
    Then all MySQL session-state keys are cleared
    And the database dropdown disappears

  Scenario: MongoDB Connect button appears when form is filled
    Given the user has selected "MongoDB"
    When host, port, username, and password are populated
    Then a "🔗 Connect" button is visible and enabled

  Scenario: No-auth connection form
    Given the user selects "None / No Auth" in Auth Mechanism
    Then the Username and Password fields are still shown but not required
```

## Technical Notes
- Add `st.radio("Database type", ["MySQL", "MongoDB"])` at the top of `SidebarComponent.render()`
- Store selected type in `st.session_state["db_type"]`
- When `db_type` changes, call `_clear_server_state()` plus clear mongo-specific keys
- MongoDB form default port: `27017`; auth mechanism options: `["SCRAM-SHA-256", "SCRAM-SHA-1", "MONGODB-X509", "None / No Auth"]`
- Persist `mongo_host`, `mongo_port`, `mongo_user`, `mongo_auth_source`, `mongo_auth_mechanism` in session state

## Definition of Done
- [x] Code implemented
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated (if needed)

## Status
✅ Done
