# US-008: Database Connection Form

**Epic**: EPIC-003
**Sprint**: Sprint 2
**Points**: 5
**Priority**: Must Have

## User Story

> As a **user**, I want to enter host, port, user, password, and database name in the
> sidebar and click "Connect" so that the tool uses my live database schema instead of
> the static YAML.

## Acceptance Criteria

```gherkin
Feature: Database Connection Form

  Scenario: Successful connection
    Given I have selected "Live Database" mode in the sidebar
    And I enter valid MySQL connection details
    When I click "Connect"
    Then the status shows "✅ Connected to <database>"
    And the Schema Viewer panel becomes visible

  Scenario: Invalid credentials
    Given I enter incorrect username or password
    When I click "Connect"
    Then the status shows "❌ Connection failed: Access denied"
    And no schema is loaded

  Scenario: Unreachable host
    Given I enter a host that is not reachable
    When I click "Connect"
    Then the status shows "❌ Connection failed: Could not connect to server"
    And the error appears within 5 seconds (connection timeout)

  Scenario: Form remembers values
    Given I have entered connection details and navigated away
    When I return to the sidebar
    Then my previously entered host, port, and database are still shown
    But the password field is cleared
```

## Technical Notes
- Use `st.session_state` to persist form values (except password)
- Password field: `st.text_input(..., type="password")`
- Connection timeout: 5 seconds
- Store engine in `st.session_state["db_engine"]` on success

## Definition of Done
- [x] `src/components/sidebar.py` updated with connection form
- [x] `src/services/db_connector.py` `create_engine()` implemented
- [x] Connection status shown in sidebar
- [x] Unit tests for `DBConnector` passing
- [x] Code review approved (CR-001)

## Status
✅ DONE
