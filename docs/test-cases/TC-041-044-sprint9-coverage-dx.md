# TC-041 to TC-044 — Sprint 9 (Coverage Completeness & DX)

| TC ID  | Story  | Type        | Automated test                                                                                                    | Status                                      |
| ------ | ------ | ----------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| TC-041 | US-040 | Unit (UI)   | `tests/unit/test_sidebar_step2.py::*` (8 tests)                                                                   | ✅ Passing                                   |
| TC-042 | US-041 | Doc-only    | Manual review of [docs/guides/developer-guide.md](../guides/developer-guide.md) AppTest section                   | ✅ Passing                                   |
| TC-043 | US-042 | Integration | `tests/integration/test_db_connector_live.py::*` (4 tests)                                                        | ⏭ Skipped (Docker unavailable on test host) |
| TC-044 | US-043 | Doc-only    | Manual review of [docs/architecture/postgresql-epic-evaluation.md](../architecture/postgresql-epic-evaluation.md) | ✅ Passing                                   |

---

## TC-041 — `_render_step2` AppTest coverage (US-040)

```gherkin
Feature: Mock-patched AppTest tests for sidebar Step 2

  Scenario: Step 2 panel renders after Step 1 success
    Given Step 1 session state is pre-seeded
    When the app is rendered
    Then the 'mysql_db_select' selectbox is present

  Scenario: Successful Select Database populates session state
    Given Step 1 session state is pre-seeded
    And DBConnector.create_engine and SchemaDetector.detect_live_schema are mocked to succeed
    When the user clicks 'Select Database'
    Then session_state['detected_schema'] equals the mocked schema
    And session_state['db_engine'] is the mocked engine
    And session_state['_db_password'] is removed
    And step2_status is ('success', ...)

  Scenario: create_engine failure surfaces as error status
    Given DBConnector.create_engine is mocked to raise DatabaseConnectionError
    When the user clicks 'Select Database'
    Then step2_status is ('error', ...)
    And session_state['detected_schema'] is falsy

  Scenario: Missing _db_password yields a warning
    Given Step 1 session state is pre-seeded but _db_password is deleted
    When the user clicks 'Select Database'
    Then step2_status is ('warning', ...) mentioning 'reconnect' or 'expired'

  Scenario: Empty available_databases shows a warning, not a dropdown
    Given Step 1 succeeded but no databases are accessible
    When the app is rendered
    Then no 'mysql_db_select' selectbox is present
    And at least one warning element is present
```

**Tests** (8): see `tests/unit/test_sidebar_step2.py`.

**Definition of Done**:
- [x] All 8 scenarios automated
- [x] All 8 tests passing
- [x] No source code changes (test-only story)

---

## TC-042 — Developer guide AppTest quirks (US-041)

```gherkin
Feature: AppTest documentation in developer guide

  Scenario: Chaining restriction documented
    Then docs/guides/developer-guide.md contains a "Streamlit AppTest Known Quirks" section
    And the section warns set_value/run MUST NOT be chained
    And shows correct + broken examples

  Scenario: session_state quirks documented
    Then the section explains SafeSessionState raises AttributeError on .get and .pop
    And shows the correct `del at.session_state["k"]` pattern

  Scenario: default_timeout documented
    Then the section recommends default_timeout=10 for the first run

  Scenario: Widget tree instability documented
    Then the section recommends key=… lookups over positional indices
    And recommends one-state-per-test to avoid widget tree round-trips

  Scenario: Mock target documented
    Then the section explains mocking at the import-source path (services.X) not consumer path (components.Y)
```

**Verification**: manual review (no automated test for documentation). Reviewer confirmed
all 5 scenarios are present in the new section.

**Definition of Done**:
- [x] All 5 scenarios documented
- [x] Code review approved (CR-009)

---

## TC-043 — Docker-based MySQL integration fixture (US-042)

```gherkin
Feature: Docker MySQL fixture for live DBConnector tests

  Scenario: mysql_container fixture starts a real MySQL 8.0 container
    Given Docker is available on the host
    When the mysql_container fixture is requested
    Then a MySQL 8.0 container is running on a dynamic port
    And a DBConfig pointing at it is yielded
    And the container is stopped after the session

  Scenario: Fixture skips gracefully when Docker is unavailable
    Given Docker is not running on the host
    When the mysql_container fixture is requested
    Then pytest.skip is called with a clear message
    And no exception propagates

  Scenario: DBConnector.create_engine works against real MySQL
    Given the mysql_container fixture is active
    When DBConnector.create_engine(config) is called
    Then an Engine is returned
    And test_connection(engine) returns True

  Scenario: DBConnector.list_databases returns system databases
    Given an active live engine
    When list_databases is called
    Then 'information_schema' is in the result
    And the user-created 'testdb' is in the result

  Scenario: DBConnector.execute_query returns a DataFrame
    Given an active live engine
    When execute_query(engine, 'SELECT 1 AS one, 2 AS two') is called
    Then a 1x2 DataFrame is returned with the correct values

  Scenario: Bad credentials raise DatabaseConnectionError
    Given the live container's host/port but a bogus user
    When create_engine + test_connection is called
    Then DatabaseConnectionError is raised
```

**Tests** (4 + fixture): see `tests/integration/test_db_connector_live.py` and
the `mysql_container` fixture in `tests/conftest.py`.

**Definition of Done**:
- [x] Fixture implemented with graceful skip
- [x] 4 integration tests added
- [x] Tests skip cleanly without Docker (verified: 4 skipped on this host)
- [x] `docker` pytest marker registered

---

## TC-044 — PostgreSQL epic evaluation (US-043)

```gherkin
Feature: PostgreSQL epic evaluation document

  Scenario: Evaluation file exists
    Then docs/architecture/postgresql-epic-evaluation.md exists
    And it covers: codebase audit, driver choice, effort estimate, risks, Go/No-Go

  Scenario: Roadmap is updated
    Then docs/roadmap.md "Future Backlog" section references the evaluation
    And the EPIC-009 line item shows the Go decision

  Scenario: EPIC-009 file deferred per recommendation
    Then docs/epics/EPIC-009-postgresql-support.md does NOT exist (intentional)
    And the deferral is documented in the evaluation §5
```

**Verification**: manual review.

**Definition of Done**:
- [x] Evaluation document exists and is structured per template
- [x] Go/No-Go decision documented
- [x] Roadmap updated
- [x] EPIC-009 deferral documented inline
