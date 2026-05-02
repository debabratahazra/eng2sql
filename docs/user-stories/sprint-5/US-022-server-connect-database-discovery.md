# US-022: Step 1 — Server Connect & Database Discovery

**Epic**: EPIC-006
**Sprint**: Sprint 5
**Points**: 5
**Priority**: Must Have

## User Story

> As a **user**, I want to enter MySQL server credentials (host, port, username,
> password) and click **Connect** so that the application connects to the server
> and shows me the list of databases I can access.

## Acceptance Criteria

```gherkin
Feature: Step 1 — Server Connect & Database Discovery

  Scenario: Successful connection shows database list
    Given I have entered valid host, port, username, and password
    When I click "Connect"
    Then the app connects to the MySQL server without specifying a database
    And a success message shows "✅ Connected to <host> — <N> databases found"
    And a database dropdown (Step 2) becomes visible below the credentials form

  Scenario: Invalid credentials show an error
    Given I have entered an incorrect password
    When I click "Connect"
    Then an error message shows "❌ Connection failed: Access denied for user …"
    And no database dropdown is shown
    And session state key "db_server_engine" remains None

  Scenario: Unreachable host shows a timeout error
    Given I have entered a host that cannot be reached
    When I click "Connect"
    Then an error message shows "❌ Connection failed: Could not connect to …"
    And the message appears within 10 seconds (connect_timeout)

  Scenario: Connecting resets previously selected database
    Given I previously selected a database in this session
    When I change the host or username and click "Connect" again
    Then session state keys "available_databases", "selected_database",
      "db_engine", and "detected_schema" are all cleared
    And the database dropdown is repopulated with the new server's databases

  Scenario: Form fields persist non-sensitive values
    Given I have entered host, port, and username and navigated away
    When I return to the sidebar
    Then host, port, and username are pre-filled
    And the password field is empty
```

## Technical Notes
- `DBConfig.database` is passed as `""` (empty) for Step 1 connection
- The `create_engine` call for Step 1 uses URL `mysql+pymysql://user:pass@host:port/`
- Store the Step 1 engine in `st.session_state["db_server_engine"]`
- On successful connect, call `DBConnector.list_databases(server_engine)` to populate
  `st.session_state["available_databases"]`
- Persist `db_host`, `db_port`, `db_user` in session state; do NOT persist `db_password`
- Use `st.spinner("Connecting to server…")` during the connection attempt
- Clear `db_server_engine`, `available_databases`, `selected_database`, `db_engine`,
  `detected_schema` when credential fields change (use `st.session_state` on_change or
  detect change via comparison with previously stored values)

## Definition of Done
- [ ] `src/components/sidebar.py` — Step 1 form implemented
- [ ] `src/services/db_connector.py` — `list_databases()` method added (US-024)
- [ ] Session state keys `db_server_engine` and `available_databases` populated
- [ ] Credential change detection clears downstream state
- [ ] Error messages visible for bad credentials and unreachable hosts
- [ ] `ruff` and `mypy` clean
- [ ] Code review approved

## Status
✅ Done
