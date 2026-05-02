# TC-008–010: DBConnector Service

**User Story**: US-008, US-011
**Service**: `src/services/db_connector.py` — `DBConnector`
**Type**: Integration (SQLite in-memory engine)
**Priority**: P0
**Marker**: `@pytest.mark.integration`

---

## TC-008: Connection Testing

### Scenario 1: Healthy engine returns True
```gherkin
Given a connected in-memory SQLite engine
When DBConnector.test_connection(engine) is called
Then it returns True
```
**Expected**: `True`
**Test Data**: `sqlite_engine` session-scoped fixture

### Scenario 2: Dead / unreachable engine returns False
```gherkin
Given a SQLite engine pointing to a non-existent file path
When DBConnector.test_connection(engine) is called
Then it returns False
And no exception is raised to the caller
```
**Expected**: `False` — all `SQLAlchemyError` exceptions caught internally
**Test Data**: `create_engine("sqlite:////nonexistent/path/db.sqlite")`

### Edge Cases
- Engine created but database file deleted between creation and ping → `False`
- `test_connection` called in rapid succession → no connection pool exhaustion

---

## TC-009: Query Execution Returns DataFrame

### Scenario 1: Full table SELECT
```gherkin
Given a SQLite engine with a "customers" table containing 2 rows
When execute_query(engine, "SELECT * FROM customers") is called
Then it returns a pandas DataFrame
And the DataFrame has 2 rows
And the DataFrame columns include "name"
And df.iloc[0]["name"] == "Alice Smith"
```
**Expected**: `DataFrame` with 2 rows, columns `[id, name, email]`
**Test Data**: `sqlite_engine` pre-seeded with 2 customer rows

### Scenario 2: Filtered SELECT
```gherkin
Given a "orders" table with rows having different "status" values
When execute_query(engine, "SELECT * FROM orders WHERE status = 'pending'") is called
Then it returns a DataFrame with only 1 row
And df.iloc[0]["status"] == "pending"
```
**Expected**: 1-row DataFrame

### Edge Cases
- SELECT returning zero rows → empty DataFrame (not an error)
- SELECT with JOIN → correct multi-column DataFrame returned
- Very large result set → DataFrame returned without truncation

---

## TC-010: Query Validation and Error Handling

### Scenario 1: Non-SELECT raises ValueError
```gherkin
Given a valid database engine
When execute_query(engine, "DROP TABLE customers") is called
Then ValueError is raised immediately
And the error message contains "Only SELECT"
And no database operation is performed
```
**Expected**: `ValueError("Only SELECT statements are permitted. Received: 'DROP TABLE ...'…")`

### Scenario 2: INSERT blocked
```gherkin
Given a valid database engine
When execute_query(engine, "INSERT INTO customers VALUES (99, 'Hacker', 'x@y.com')") is called
Then ValueError is raised
And the error message contains "Only SELECT"
```
**Expected**: `ValueError` — prefix check catches `INSERT` before execution

### Scenario 3: Invalid SQL raises QueryExecutionError
```gherkin
Given a valid database engine
When execute_query(engine, "SELECT * FROM nonexistent_table_xyz") is called
Then QueryExecutionError is raised
And the error message contains "Query execution failed"
```
**Expected**: `QueryExecutionError("Query execution failed: ...")`

### Scenario 4: CREATE ENGINE failure raises DatabaseConnectionError
```gherkin
Given a DBConfig pointing to a host that cannot be reached
When DBConnector.create_engine(config) is called
Then DatabaseConnectionError is raised
And the error message contains the host and port
```
**Expected**: `DatabaseConnectionError("Could not connect to <host>:<port>/<db> — ...")`

### Edge Cases
- SQL injection attempt in the question field → blocked upstream by SELECT-only check
- `execute_query` called with `UPDATE` → `ValueError` (case-insensitive prefix check via `.upper()`)
- `execute_query` called with leading whitespace + SELECT → accepted after `.strip()`

---

## Pytest Implementation

**File**: `tests/integration/test_db_connector.py` ✅ **Implemented (7 tests passing)**

| Scenario    | Test method                                                                      |
| ----------- | -------------------------------------------------------------------------------- |
| TC-008 Sc-1 | `TestDBConnectorIntegration::test_test_connection_returns_true_for_valid_engine` |
| TC-008 Sc-2 | `TestDBConnectorIntegration::test_test_connection_returns_false_for_bad_engine`  |
| TC-009 Sc-1 | `TestDBConnectorIntegration::test_execute_query_returns_dataframe`               |
| TC-009 Sc-2 | `TestDBConnectorIntegration::test_execute_query_filtered_results`                |
| TC-010 Sc-1 | `TestDBConnectorIntegration::test_execute_query_raises_on_non_select`            |
| TC-010 Sc-2 | `TestDBConnectorIntegration::test_execute_query_raises_on_insert`                |
| TC-010 Sc-3 | `TestDBConnectorIntegration::test_execute_query_raises_on_invalid_sql`           |

> **Coverage note**: `DBConnector.create_engine` success path (TC-010 Sc-4) is not
> unit-tested because it requires a live DB or deep SQLAlchemy mocking. The integration
> test suite (Sprint 3) should add a mock-based unit test covering lines 33–60 of
> `db_connector.py` to reach the 80% coverage gate.
