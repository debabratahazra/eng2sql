# Test Cases TC-107–TC-116: Sprint 17 — Component Coverage Completion

**Sprint**: 17  
**Author**: Test Case Writer Agent  
**Related Stories**: US-075, US-076, US-077, US-078  
**Coverage**: 98.03% (966 statements, 19 missing)

---

## TC-107: Coverage Gate Passes After Removing Component Omit

**Story**: US-075  
**Type**: Unit / Configuration  
**Priority**: High

### Scenario
```
Given the pyproject.toml has "src/components/*" removed from the coverage omit list
When pytest is run with --cov=src across tests/unit/
Then the total coverage is ≥ 80%
And src/app.py remains excluded from measurement
```

**Verification**: UTR-019 — 90.79% (then 98.03% after US-076 tests added)

---

## TC-108: `src/app.py` Remains Excluded from Coverage

**Story**: US-075  
**Type**: Configuration  
**Priority**: Medium

### Scenario
```
Given pyproject.toml [tool.coverage.run] omit contains "src/app.py"
When coverage is collected
Then src/app.py does not appear in the coverage report
```

---

## TC-109: Relational Step 2 Not Rendered Without Server Engine

**Story**: US-076  
**Type**: Unit / AppTest  
**Priority**: High

### Scenario
```
Given the app renders with db_server_engine = None (default)
When the sidebar step 2 is checked
Then no "mysql_db_select" selectbox appears
```

**Test**: `TestRelationalStep2::test_step2_not_rendered_when_no_server_engine`

---

## TC-110: Relational Step 2 Renders Selectbox When Databases Available

**Story**: US-076  
**Type**: Unit / AppTest  
**Priority**: High

### Scenario
```
Given db_server_engine is set to a mock engine
And available_databases = ["appdb", "testdb"]
When the sidebar renders
Then the "mysql_db_select" selectbox is present
```

**Test**: `TestRelationalStep2::test_step2_renders_selectbox_when_databases_available`

---

## TC-111: Relational Step 2 Expired Password Shows Warning

**Story**: US-076  
**Type**: Unit / AppTest  
**Priority**: High

### Scenario
```
Given db_server_engine is set and available_databases is non-empty
And _db_password is NOT in session state
When "Select Database" button is clicked
Then step2_status level is "warning"
And message contains "expired" or "reconnect"
```

**Test**: `TestRelationalStep2::test_step2_expired_password_yields_warning`

---

## TC-112: MongoDB URI Mode Renders URI Text Input

**Story**: US-076  
**Type**: Unit / AppTest  
**Priority**: High

### Scenario
```
Given the user switches DB type to MongoDB
And selects "URI + credentials" connection mode
When the sidebar renders
Then a text input with label "MongoDB URI" is visible
```

**Test**: `TestMongoURIMode::test_uri_mode_renders_uri_text_input`

---

## TC-113: MongoDB URI Mode Empty URI Shows Warning

**Story**: US-076  
**Type**: Unit / AppTest  
**Priority**: High

### Scenario
```
Given MongoDB URI mode is active
And the URI input field is empty
When the Connect button is clicked
Then mongo_step1_status level is "warning"
And message contains "uri"
```

**Test**: `TestMongoURIMode::test_uri_mode_empty_uri_click_yields_warning`

---

## TC-114: MongoDB URI Mode Connect Success Stores Databases

**Story**: US-076  
**Type**: Unit / AppTest  
**Priority**: High

### Scenario
```
Given MongoDB URI mode is active
And the URI input is filled with a valid URI
And MongoDBConnector.connect() is mocked to return a client
And list_databases() returns ["prod", "staging"]
When the Connect button is clicked
Then mongo_step1_status level is "success"
And mongo_available_databases = ["prod", "staging"]
```

**Test**: `TestMongoURIMode::test_uri_mode_connect_success_stores_databases`

---

## TC-115: MongoDB Step 2 Not Rendered Without Client

**Story**: US-076  
**Type**: Unit / AppTest  
**Priority**: High

### Scenario
```
Given MongoDB type is selected
And mongo_client = None (default)
When the sidebar renders
Then no "mongo_db_select" selectbox appears
```

**Test**: `TestMongoStep2::test_step2_not_rendered_without_mongo_client`

---

## TC-116: Module-Scoped AppTest Fixture Is Read-Only Safe

**Story**: US-077  
**Type**: Unit / Investigation  
**Priority**: Medium

### Scenario
```
Given the initial_app_state fixture provides a module-scoped AppTest
When test A reads session_state["db_type"] (read only)
And test B switches the radio to MongoDB in its own function-scoped AppTest
Then test C (using initial_app_state) still sees db_type = "MySQL"
```

**Test**: `TestInteractiveTestsRequireFunctionScope::test_subsequent_read_only_check_still_sees_mysql`

---

## TC-117: db_connector.py OperationalError Wraps to DatabaseConnectionError

**Story**: US-078  
**Type**: Unit (existing)  
**Priority**: High

### Scenario
```
Given the DBConnector.create_engine() is called
And the engine.connect().execute() raises OperationalError
When the error is caught
Then DatabaseConnectionError is raised with the original message
```

**Test**: `test_db_connector_extended.py::test_create_engine_operational_error` (pre-existing)

---

## TC-118: db_connector.py SQLAlchemyError in execute_query Wraps to QueryExecutionError

**Story**: US-078  
**Type**: Unit (existing)  
**Priority**: High

### Scenario
```
Given DBConnector.execute_query() is called with a mocked engine
And the connection raises SQLAlchemyError("syntax error near SELECT")
When the error propagates
Then QueryExecutionError is raised
```

**Test**: `test_db_connector_extended.py::test_execute_query_sqlalchemy_error` (pre-existing)
