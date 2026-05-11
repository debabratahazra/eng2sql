# Test Cases TC-023 to TC-030 — Sprint 6 MongoDB Support

**Sprint**: Sprint 6
**Epic**: EPIC-007 — MongoDB Database Support
**Author**: Test Case Writer
**Date**: 2026-05-02

---

## TC-023: MongoDBConnector — Successful Connection

**User Story**: US-027
**Priority**: Must Have

### Preconditions
- `MongoDBConnector` service instantiated
- Valid `MongoConfig` provided (host, port, username, password)
- `pymongo.MongoClient` mocked to return a client that responds to `ping`

### Test Steps

```gherkin
Feature: MongoDBConnector.connect()

  Scenario TC-023-01: Successful connection returns MongoClient
    Given a valid MongoConfig with host "localhost" and port 27017
    And MongoClient is mocked to succeed on ping
    When MongoDBConnector.connect(config) is called
    Then the returned object is the mock MongoClient
    And client.admin.command("ping") was called exactly once

  Scenario TC-023-02: Connection failure raises DatabaseConnectionError
    Given a MongoConfig pointing to an unreachable host
    And MongoClient.admin.command raises an Exception
    When MongoDBConnector.connect(config) is called
    Then DatabaseConnectionError is raised
    And the error message contains "Could not connect to MongoDB"

  Scenario TC-023-03: No-auth config produces URI without credentials
    Given a MongoConfig with auth_mechanism "None / No Auth"
    When MongoDBConnector.connect(config) is called
    Then MongoClient is constructed with a URI containing no "@" character

  Scenario TC-023-04: connect() raises DatabaseConnectionError when pymongo unavailable
    Given _PYMONGO_AVAILABLE is False
    When MongoDBConnector.connect(config) is called
    Then DatabaseConnectionError is raised with "pymongo is not installed" message
```

### Expected Results
- All four scenarios pass without connecting to a real MongoDB server.

---

## TC-024: MongoDBConnector — Database Listing & Retrieval

**User Story**: US-027
**Priority**: Must Have

### Preconditions
- Connected `MongoClient` mock
- `list_database_names()` returns controlled list

### Test Steps

```gherkin
Feature: MongoDBConnector.list_databases() and get_database()

  Scenario TC-024-01: list_databases() filters system databases
    Given client.list_database_names() returns ["admin", "local", "config", "mydb"]
    When MongoDBConnector.list_databases(client) is called
    Then the result is ["mydb"]

  Scenario TC-024-02: list_databases() returns sorted result
    Given client.list_database_names() returns ["zebra", "apple", "mango", "admin"]
    When MongoDBConnector.list_databases(client) is called
    Then the result is ["apple", "mango", "zebra"]

  Scenario TC-024-03: list_databases() raises DatabaseConnectionError on driver failure
    Given client.list_database_names() raises an Exception
    When MongoDBConnector.list_databases(client) is called
    Then DatabaseConnectionError is raised matching "Failed to list MongoDB databases"

  Scenario TC-024-04: get_database() returns subscript result
    Given a mock MongoClient
    When MongoDBConnector.get_database(client, "mydb") is called
    Then client["mydb"] is returned
```

### Expected Results
- System databases always excluded; result always sorted alphabetically.

---

## TC-025: MongoConfig — URI Generation

**User Story**: US-027
**Priority**: Must Have

### Test Steps

```gherkin
Feature: MongoConfig.connection_uri property

  Scenario TC-025-01: URI with credentials includes auth params
    Given MongoConfig(username="user", password="pass", auth_source="admin",
      auth_mechanism="SCRAM-SHA-256")
    When connection_uri is accessed
    Then the URI contains "user", "pass", "authSource=admin", "authMechanism=SCRAM-SHA-256"

  Scenario TC-025-02: No-auth URI omits credentials
    Given MongoConfig(auth_mechanism="None / No Auth")
    When connection_uri is accessed
    Then the URI equals "mongodb://localhost:27017/"

  Scenario TC-025-03: Special characters in password are percent-encoded
    Given MongoConfig(password="p@ss w0rd!")
    When connection_uri is accessed
    Then the URI contains percent-encoded password (no literal "@" or space)
```

---

## TC-026: MongoSchemaDetector — Schema Detection

**User Story**: US-028
**Priority**: Must Have

### Preconditions
- `MongoSchemaDetector` instantiated
- pymongo `Database` object mocked

### Test Steps

```gherkin
Feature: MongoSchemaDetector.detect_schema()

  Scenario TC-026-01: Returns TableSchema keyed by collection name
    Given database has collection "users" with one document {_id: 1, name: "Alice"}
    When detect_schema(db) is called
    Then "users" is present in the returned dict

  Scenario TC-026-02: _id field is marked primary_key=True
    Given collection "items" contains document {_id: 1, label: "Widget"}
    When detect_schema(db) is called
    Then the SchemaColumn for "_id" has primary_key=True

  Scenario TC-026-03: All columns are nullable=True
    Given any collection with any fields
    When detect_schema(db) is called
    Then every SchemaColumn has nullable=True

  Scenario TC-026-04: Fields unioned across sampled documents
    Given "products" has [{_id:1, price:10}, {_id:2, discount:5}]
    When detect_schema(db) is called
    Then both "price" and "discount" appear in the column list

  Scenario TC-026-05: Conflicting types produce "Mixed"
    Given "mixed" has [{_id:1, val:42}, {_id:2, val:"string"}]
    When detect_schema(db) is called
    Then the "val" column has type="Mixed"

  Scenario TC-026-06: Empty collection returns empty column list
    Given collection "empty_col" has no documents
    When detect_schema(db) is called
    Then schema["empty_col"] is an empty list

  Scenario TC-026-07: sample_size parameter is forwarded to find()
    Given sample_size=50 is passed
    When detect_schema(db, sample_size=50) is called
    Then collection.find({}, limit=50) was called

  Scenario TC-026-08: Driver failure on list_collection_names raises SchemaDetectionError
    Given db.list_collection_names() raises an Exception
    When detect_schema(db) is called
    Then SchemaDetectionError is raised matching "Failed to list MongoDB collections"

  Scenario TC-026-09: Driver failure on find() raises SchemaDetectionError
    Given collection.find() raises an Exception
    When detect_schema(db) is called
    Then SchemaDetectionError is raised matching "Failed to sample collection"
```

---

## TC-027: Sidebar — Database Type Radio

**User Story**: US-025
**Priority**: Must Have

### Test Steps

```gherkin
Feature: Database type radio in sidebar

  Scenario TC-027-01: Default db_type is MySQL
    Given a fresh Streamlit session
    When st.session_state["db_type"] is read
    Then the value is "MySQL"

  Scenario TC-027-02: Switching to MongoDB clears MySQL state keys
    Given "db_server_engine", "db_engine", "detected_schema" are set in session
    When db_type is switched to "MongoDB"
    Then those keys are removed from session state

  Scenario TC-027-03: Switching back to MySQL clears MongoDB state keys
    Given "mongo_client", "mongo_db", "detected_schema" are set in session
    When db_type is switched to "MySQL"
    Then those keys are removed from session state
```

---

## TC-028: Sidebar — MongoDB Step 1 Connect

**User Story**: US-025, US-026
**Priority**: Must Have

### Test Steps

```gherkin
Feature: MongoDB Step 1 connection flow

  Scenario TC-028-01: Successful connect stores client and database list
    Given valid MongoDB credentials and mocked MongoDBConnector.connect()
    When the Connect button is clicked
    Then st.session_state["mongo_client"] is set
    And st.session_state["mongo_available_databases"] contains the filtered list
    And a success status message is stored in "mongo_step1_status"

  Scenario TC-028-02: Failed connect stores error status
    Given MongoDBConnector.connect() raises DatabaseConnectionError
    When the Connect button is clicked
    Then st.session_state["mongo_client"] remains None
    And "mongo_step1_status" contains an "error" tuple

  Scenario TC-028-03: Missing host shows warning
    Given an empty host field
    When the Connect button is clicked
    Then "mongo_step1_status" contains a "warning" tuple
```

---

## TC-029: Sidebar — MongoDB Step 2 Select Database

**User Story**: US-026
**Priority**: Must Have

### Test Steps

```gherkin
Feature: MongoDB Step 2 database selection

  Scenario TC-029-01: Successful selection stores mongo_db and detected_schema
    Given mongo_client is set and mocked get_database() returns a Database
    And MongoSchemaDetector.detect_schema() returns a non-empty TableSchema
    When Select Database is clicked
    Then st.session_state["mongo_db"] is set
    And st.session_state["mongo_selected_database"] equals the chosen name
    And st.session_state["detected_schema"] is populated
    And "mongo_step2_status" contains a "success" tuple

  Scenario TC-029-02: Step 2 hidden when mongo_client is None
    Given st.session_state["mongo_client"] is None
    When the sidebar renders
    Then the Step 2 form is not visible
```

---

## TC-030: App — MongoDB Dialect in Query Generation

**User Story**: US-029
**Priority**: Must Have

### Test Steps

```gherkin
Feature: MongoDB dialect passed to SQLGenerator

  Scenario TC-030-01: dialect="MongoDB" passed when db_type is MongoDB
    Given st.session_state["db_type"] = "MongoDB"
    And detected_schema is set
    And SQLGenerator.generate_sql is mocked
    When the user submits a question
    Then generate_sql is called with dialect="MongoDB"

  Scenario TC-030-02: dialect="MySQL" passed when db_type is MySQL
    Given st.session_state["db_type"] = "MySQL"
    When the user submits a question
    Then generate_sql is called with dialect="MySQL"

  Scenario TC-030-03: Execute SQL button hidden for MongoDB
    Given st.session_state["db_type"] = "MongoDB"
    And generated_sql is non-empty
    When app renders
    Then the "Execute SQL" button is not shown
    And an info message about MongoDB execution appears instead

  Scenario TC-030-04: Page subtitle reflects active db_type
    Given st.session_state["db_type"] = "MongoDB"
    When app renders
    Then the subtitle contains "MongoDB"
    Given st.session_state["db_type"] = "MySQL"
    Then the subtitle contains "MySQL"
```

---

## Test Coverage Summary

| TC     | Story  | Category       | Tests in Code                                   | Status |
| ------ | ------ | -------------- | ----------------------------------------------- | ------ |
| TC-023 | US-027 | Unit           | `test_mongo_connector.py::TestMongoDBConnector` | ✅ PASS |
| TC-024 | US-027 | Unit           | `test_mongo_connector.py::TestMongoDBConnector` | ✅ PASS |
| TC-025 | US-027 | Unit           | `test_mongo_connector.py::TestMongoConfig`      | ✅ PASS |
| TC-026 | US-028 | Unit           | `test_mongo_schema_detector.py`                 | ✅ PASS |
| TC-027 | US-025 | Unit           | Covered via session-state isolation logic       | ✅ PASS |
| TC-028 | US-025 | Unit (sidebar) | Covered by sidebar service-layer mocks          | ✅ PASS |
| TC-029 | US-026 | Unit (sidebar) | Covered by sidebar service-layer mocks          | ✅ PASS |
| TC-030 | US-029 | Unit (app)     | app.py branches verified by integration         | ✅ PASS |
