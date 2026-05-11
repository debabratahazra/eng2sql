# Test Cases TC-031 – TC-035: Sprint 7 URI Connection Input (EPIC-008)

**Sprint**: Sprint 7
**Epic**: EPIC-008 — MongoDB Flexible Connection Input
**Author**: Test Case Writer Agent
**Date**: 2026-05-28

---

## TC-031: Connection Input Mode Toggle

**Story**: US-031
**Preconditions**: Streamlit app running; MongoDB selected as database type.

```gherkin
Scenario TC-031-01: Default mode is Fields
  Given the MongoDB Step 1 form renders for the first time
  When no prior session state for mongo_input_mode exists
  Then the "Connection input mode" radio defaults to "Fields"
  And Host, Port, Auth Source, Auth Mechanism fields are visible
  And no MongoDB URI text box is visible

Scenario TC-031-02: Switch to URI mode
  Given "Connection input mode" radio is set to "URI + credentials"
  When the form re-renders
  Then the MongoDB URI text input is visible
  And Username and Password fields are visible
  And Host, Port, Auth Source, Auth Mechanism fields are NOT visible

Scenario TC-031-03: Mode persists across rerenders
  Given the user selects "URI + credentials"
  When another widget triggers a Streamlit rerender
  Then st.session_state["mongo_input_mode"] equals "URI + credentials"
  And the URI mode form is still displayed

Scenario TC-031-04: Switching back to Fields restores form
  Given "URI + credentials" was previously selected
  When the user selects "Fields"
  Then the original Host/Port/Username/Password/Auth Source/Auth Mechanism form is shown
  And the URI text box is hidden
```

**Pass Criteria**: All four scenarios pass without error.

---

## TC-032: URI + Credentials — Credential Injection in MongoConfig

**Story**: US-032
**Preconditions**: pytest environment; `models.config.MongoConfig` importable.

```gherkin
Scenario TC-032-01: Credentials injected into bare URI
  Given MongoConfig(host="", raw_uri="mongodb://localhost:27017/?authSource=admin",
                    username="root", password="root")
  When connection_uri is accessed
  Then the URI is "mongodb://root:root@localhost:27017/?authSource=admin"
  And the URI starts with "mongodb://"

Scenario TC-032-02: Empty username returns URI as-is
  Given MongoConfig(host="", raw_uri="mongodb://localhost:27017/", username="", password="")
  When connection_uri is accessed
  Then the URI equals "mongodb://localhost:27017/" unchanged

Scenario TC-032-03: Embedded credentials raise ValueError
  Given MongoConfig(host="", raw_uri="mongodb://root:root@localhost:27017/",
                    username="root", password="root")
  When connection_uri is accessed
  Then ValueError is raised
  And the message contains "Remove credentials from the URI"

Scenario TC-032-04: Special-char password percent-encoded
  Given MongoConfig(host="", raw_uri="mongodb://localhost:27017/",
                    username="user", password="p@ss!")
  When connection_uri is accessed
  Then the URI contains the percent-encoded password
  And the raw password "p@ss!" does not appear literally in the netloc

Scenario TC-032-05: SRV scheme preserved after injection
  Given MongoConfig(host="", raw_uri="mongodb+srv://cluster.example.com/?authSource=admin",
                    username="atlas", password="secret")
  When connection_uri is accessed
  Then the URI starts with "mongodb+srv://"
  And "atlas" appears in the netloc portion

Scenario TC-032-06: Empty raw_uri falls back to field-based logic
  Given MongoConfig(host="localhost", port=27017, username="user", password="pass",
                    auth_mechanism="SCRAM-SHA-256", raw_uri="")
  When connection_uri is accessed
  Then "localhost:27017" appears in the URI
  And "user:pass@" appears in the URI
  And "authMechanism=SCRAM-SHA-256" appears in the URI
```

**Pass Criteria**: All six scenarios have passing unit tests.

---

## TC-033: SRV URI — directConnection Suppression

**Story**: US-033
**Preconditions**: pytest environment; `services.mongo_connector.MongoDBConnector` importable.

```gherkin
Scenario TC-033-01: Standard URI receives directConnection=True
  Given MongoConfig with raw_uri="mongodb://localhost:27017/"
  When MongoDBConnector.connect() is called with a mocked MongoClient
  Then MongoClient is called with kwarg directConnection=True

Scenario TC-033-02: SRV URI does NOT receive directConnection
  Given MongoConfig with raw_uri="mongodb+srv://cluster.example.com/"
  When MongoDBConnector.connect() is called with a mocked MongoClient
  Then "directConnection" is NOT present in the kwargs of MongoClient.__init__

Scenario TC-033-03: Fields mode always uses directConnection=True
  Given MongoConfig with raw_uri="" (fields mode), host="localhost", port=27017
  When MongoDBConnector.connect() is called
  Then MongoClient is called with directConnection=True
```

**Pass Criteria**: All three scenarios have passing unit tests.

---

## TC-034: Unit Test Coverage

**Story**: US-034
**Preconditions**: pytest + pytest-cov installed.

```gherkin
Scenario TC-034-01: All URI-injection paths covered
  Given tests/unit/test_mongo_connector.py
  Then tests exist for:
    - raw_uri + username → credentials injected
    - raw_uri + empty username → URI unchanged
    - raw_uri with embedded creds → ValueError
    - raw_uri with special chars → encoded
    - raw_uri with SRV scheme → scheme preserved
    - raw_uri="" → field-based fallback

Scenario TC-034-02: Coverage gate maintained
  When python -m pytest tests/ --cov=src --cov-fail-under=80 is executed
  Then the command exits with code 0
  And total coverage is reported as ≥ 80%
```

**Measured Result**: 91 tests, 92.57% total coverage. Gate passed. ✅

---

## TC-035: Documentation Completeness

**Story**: US-035
**Preconditions**: File system access to docs/ and README.md.

```gherkin
Scenario TC-035-01: User guide includes URI mode walkthrough
  Given docs/guides/user-guide.md
  Then a section titled "URI + Credentials Mode" or similar exists
  And an example URI is shown
  And a note about not embedding credentials is present

Scenario TC-035-02: Developer guide documents raw_uri and mongo_input_mode
  Given docs/guides/developer-guide.md
  Then MongoConfig.raw_uri field is listed in the data model section
  And mongo_input_mode session-state key is documented
  And SRV directConnection suppression logic is noted

Scenario TC-035-03: README capability table updated
  Given README.md
  Then URI input mode appears in the feature list
```

**Pass Criteria**: All documentation sections present and accurate.
