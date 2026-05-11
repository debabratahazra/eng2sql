# TC-051..057 — Sprint 11 BDD Test Cases

**Sprint**: Sprint 11 — Refactor & Hardening
**Author**: Test Case Writer
**Date**: 2026-05-09

---

## TC-051 — `LOOPBACK_HOSTS` exposes the canonical loopback set (US-050)

```gherkin
Feature: Shared network helpers

  Scenario: LOOPBACK_HOSTS contains the four loopback names
    Given the module utils.network is imported
    Then LOOPBACK_HOSTS contains "localhost"
    And LOOPBACK_HOSTS contains "127.0.0.1"
    And LOOPBACK_HOSTS contains "::1"
    And LOOPBACK_HOSTS contains "0.0.0.0"
    And LOOPBACK_HOSTS is a frozenset
```

Implemented by: `tests/unit/test_network.py::TestLoopbackHosts`

---

## TC-052 — `is_wsl2()` detects WSL2 and caches its result (US-050)

```gherkin
  Scenario: is_wsl2 returns True when /proc/version contains "microsoft"
    Given /proc/version contains the string "microsoft"
    When is_wsl2() is called
    Then it returns True

  Scenario: is_wsl2 returns False when /proc/version is unavailable
    Given pathlib.Path.read_text raises OSError
    When is_wsl2() is called
    Then it returns False

  Scenario: is_wsl2 caches the result
    Given /proc/version contains the string "microsoft"
    When is_wsl2() is called three times
    Then read_text is invoked exactly once
```

Implemented by: `tests/unit/test_network.py::TestIsWsl2`

---

## TC-053 — `probe_reachable_host` returns the first reachable address (US-050)

```gherkin
  Scenario: probe returns the second address when the first refuses
    Given getaddrinfo returns [127.0.0.1, ::1] for localhost:9999
    And the IPv4 socket connection raises OSError
    And the IPv6 socket connection succeeds
    When probe_reachable_host("localhost", 9999) is called
    Then it returns "::1"

  Scenario: probe returns input host on DNS failure
    Given getaddrinfo raises OSError
    When probe_reachable_host("nonexistent.host.invalid", 1234) is called
    Then it returns "nonexistent.host.invalid"

  Scenario: probe returns input host when no address answers
    Given all addresses raise OSError on connect
    When probe_reachable_host("localhost", 65000) is called
    Then it returns "localhost"
```

Implemented by: `tests/unit/test_network.py::TestProbeReachableHost`

---

## TC-054 — `db_connector.create_engine` raises clearly when WSL2 cannot reach loopback (US-050)

```gherkin
  Scenario: WSL2 + loopback host + unreachable port raises DatabaseConnectionError
    Given DBConfig.host == "localhost" and DBConfig.dialect == "postgresql"
    And is_wsl2() returns True
    And probe_reachable_host returns the input host unchanged
    When DBConnector().create_engine(config) is called
    Then DatabaseConnectionError is raised
    And the message contains the word "WSL2"

  Scenario: WSL2 guard skipped for non-loopback hosts
    Given DBConfig.host == "pg.example.com"
    When DBConnector().create_engine(config) is called
    Then is_wsl2() is never called

  Scenario: WSL2 guard skipped when not running under WSL2
    Given DBConfig.host == "localhost"
    And is_wsl2() returns False
    When DBConnector().create_engine(config) is called
    Then probe_reachable_host is never called
```

Implemented by: `tests/unit/test_db_connector_postgresql_unit.py::TestPostgreSQLCreateEngine`

---

## TC-055 — PostgreSQL `create_engine` builds the right URL with sslmode (US-055)

```gherkin
  Scenario: PostgreSQL URL contains psycopg driver and sslmode=prefer
    Given DBConfig with dialect="postgresql" and sslmode="prefer"
    When DBConnector().create_engine(config) is called
    Then the URL passed to sqlalchemy.create_engine starts with "postgresql+psycopg://"
    And the URL contains "sslmode=prefer"

  Scenario: PostgreSQL URL preserves sslmode=disable
    Given DBConfig with sslmode="disable"
    When DBConnector().create_engine(config) is called
    Then the URL passed to sqlalchemy.create_engine contains "sslmode=disable"
```

Implemented by: `tests/unit/test_db_connector_postgresql_unit.py`

---

## TC-056 — Configurable PostgreSQL admin DB (US-052)

```gherkin
  Scenario: Admin DB defaults to "postgres"
    Given the Streamlit app starts with no prior session
    When db_type is switched to "PostgreSQL"
    Then session_state["pg_admin_db"] equals "postgres"

  Scenario: Custom admin DB propagates into DBConfig.database
    Given the user enters "defaultdb" in the Admin DB input
    When the Connect button is clicked
    Then DBConnector.create_engine receives a DBConfig where database == "defaultdb"
    And the DBConfig.dialect == "postgresql"

  Scenario: Empty admin DB rejected
    Given the user clears the Admin DB input
    When the Connect button is clicked
    Then session_state["pg_step1_status"] is ("warning", "Admin DB cannot be empty.")
```

Implemented by: `tests/unit/test_sidebar_sprint11.py::TestConfigurableAdminDb`

---

## TC-057 — Sslmode `verify-*` pre-validation (US-056)

```gherkin
  Scenario: Warning shown when verify-ca selected and no CA bundle
    Given pg_sslmode == "verify-ca"
    And _ca_bundle_available() returns False
    When the sidebar renders
    Then a warning containing "CA bundle" is shown

  Scenario: No warning for non-verify sslmode
    Given pg_sslmode == "prefer"
    When the sidebar renders
    Then no CA-bundle warning is shown

  Scenario: No warning when CA bundle is available
    Given pg_sslmode == "verify-full"
    And _ca_bundle_available() returns True
    When the sidebar renders
    Then no CA-bundle warning is shown

  Scenario: PGSSLROOTCERT env var pointing at an existing file is accepted
    Given PGSSLROOTCERT points at an existing file
    When _ca_bundle_available() is called
    Then it returns True
```

Implemented by: `tests/unit/test_sidebar_sprint11.py::TestSslmodeCaPrevalidation`, `TestCaBundleHelper`
