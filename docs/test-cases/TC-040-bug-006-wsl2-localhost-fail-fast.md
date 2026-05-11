# TC-040 — BUG-006 Regression: WSL2 Localhost MongoDB Fail-Fast With Hint

**Linked Bug**: [BUG-006](../bug-reports/BUG-006-wsl2-localhost-mongodb-connection-timeout.md)
**Linked Story**: US-031, US-032
**Type**: Regression (BDD)
**Priority**: High
**Status**: ✅ Passing

---

## Scenario 1 — WSL2 + loopback + probe failure raises actionable hint

```gherkin
Given the application is running inside WSL2
  And the user supplies a MongoDB URI with a loopback host (localhost / 127.0.0.1 / ::1)
  And the TCP probe cannot reach any address for that host
When MongoDBConnector.connect() is invoked
Then a DatabaseConnectionError is raised IMMEDIATELY (no MongoClient call)
  And the error message contains the substring "WSL2"
  And the error message recommends /etc/resolv.conf or host.docker.internal
  And MongoClient is NOT instantiated (no 5-second topology timeout)
```

**Automated test**:
`tests/unit/test_mongo_connector.py::TestMongoDBConnector::test_bug_006_wsl2_localhost_unreachable_fails_fast_with_hint`

---

## Scenario 2 — Non-WSL2 environments preserve prior behaviour

```gherkin
Given the application is running on Windows / macOS / native Linux (not WSL2)
  And the TCP probe cannot reach any loopback address
When MongoDBConnector.connect() is invoked
Then MongoClient IS instantiated (connect attempt proceeds normally)
  And the WSL2 fail-fast does NOT trigger
```

**Automated test**:
`tests/unit/test_mongo_connector.py::TestMongoDBConnector::test_bug_006_non_wsl2_localhost_probe_failure_still_calls_mongoclient`

---

## Scenario 3 — Existing directConnection invariant preserved

```gherkin
Given the BUG-005 decision that directConnection MUST NOT be forced
When MongoDBConnector.connect() builds MongoClient kwargs
Then "directConnection" is absent from the kwargs dictionary
```

**Automated test**:
`tests/unit/test_mongo_connector.py::TestMongoDBConnector::test_connect_does_not_force_direct_connection`

---

## Definition of Done

- [x] Regression test added (`test_bug_006_wsl2_localhost_unreachable_fails_fast_with_hint`)
- [x] Negative test added (`test_bug_006_non_wsl2_localhost_probe_failure_still_calls_mongoclient`)
- [x] Existing `directConnection` invariant test still passes
- [x] Full pytest suite passes (136/136)
- [x] Coverage ≥ 80 % (93.97 %)
- [x] AppTest UI smoke tests pass (10/10)
- [x] BUG-006 status updated to ✅ Fixed
- [x] Developer guide updated with WSL2 networking note
