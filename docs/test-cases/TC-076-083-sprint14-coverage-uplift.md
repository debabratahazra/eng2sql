# Test Cases TC-076 to TC-083 — Sprint 14: Coverage Uplift

**Sprint**: 14
**Epic**: EPIC-011 — Dependency Hygiene & Coverage Uplift
**Written by**: Test Case Writer Agent
**Date**: 2025-07-25

---

## TC-076 — testcontainers[mongo] Declared in Dev Dependencies

**User Story**: US-063  
**Type**: Configuration  
**Priority**: High

### Scenario: testcontainers[mongo] present in pyproject.toml

```gherkin
Given the pyproject.toml file in the project root
When I inspect [project.optional-dependencies].dev
Then the entry "testcontainers[mongo]>=4.7.0" is present
And it is grouped with the other testcontainers entries (mysql, postgres)
```

### Scenario: testcontainers[mongo] present in requirements.txt

```gherkin
Given the requirements.txt file in the project root
When I search for testcontainers[mongo]
Then a line matching "testcontainers[mongo]>=4.7.0" is present
```

---

## TC-077 — schema_detector.py: Non-List Columns Raises Error

**User Story**: US-064  
**Type**: Unit  
**Priority**: Medium

### Scenario: columns value is not a list

```gherkin
Given a YAML schema config where a table's "columns" key maps to a string
When load_static_schema() is called
Then SchemaDetectionError is raised
And the error message contains the table name
```

---

## TC-078 — detect_live_schema: Mocked Inspector Returns Schema

**User Story**: US-064  
**Type**: Unit  
**Priority**: Medium

### Scenario: empty database returns empty schema

```gherkin
Given a mock SQLAlchemy inspector returning zero table names
When detect_live_schema(engine) is called
Then the result is an empty dict
And no exception is raised
```

### Scenario: single table with columns is returned

```gherkin
Given a mock inspector returning ["users"] from get_table_names()
And get_columns("users") returning [{"name": "id", "type": Integer(), "nullable": False}]
And get_pk_constraint("users") returning {"constrained_columns": ["id"]}
When detect_live_schema(engine) is called
Then the result dict has key "users"
And the first SchemaColumn has name="id", primary_key=True, nullable=False
```

### Scenario: multiple tables returned

```gherkin
Given a mock inspector returning ["orders", "items"]
And each table has defined columns
When detect_live_schema(engine) is called
Then both "orders" and "items" keys exist in the result
```

---

## TC-079 — detect_live_schema: Inspector Exception Propagation

**User Story**: US-064  
**Type**: Unit  
**Priority**: Medium

### Scenario: get_table_names raises SQLAlchemyError

```gherkin
Given a mock inspector whose get_table_names() raises SQLAlchemyError
When detect_live_schema(engine) is called
Then SchemaDetectionError is raised
```

### Scenario: get_columns raises SQLAlchemyError

```gherkin
Given a mock inspector returning ["users"] from get_table_names()
And get_columns("users") raises SQLAlchemyError
When detect_live_schema(engine) is called
Then SchemaDetectionError is raised
```

---

## TC-080 — create_engine: OperationalError Handling

**User Story**: US-065  
**Type**: Unit  
**Priority**: High

### Scenario: OperationalError is wrapped as DatabaseConnectionError

```gherkin
Given a mocked create_engine that returns an engine
And the engine's connect().execute() raises OperationalError
When DBConnector().create_engine(cfg) is called
Then DatabaseConnectionError is raised
And the error message contains "Could not connect"
```

---

## TC-081 — create_engine: SQLAlchemyError Handling

**User Story**: US-065  
**Type**: Unit  
**Priority**: High

### Scenario: Generic SQLAlchemyError is wrapped as DatabaseConnectionError

```gherkin
Given a mocked create_engine that returns an engine
And the engine's connect().execute() raises SQLAlchemyError
When DBConnector().create_engine(cfg) is called
Then DatabaseConnectionError is raised
And the error message contains "Database error during connection"
```

---

## TC-082 — test_connection: True and False Paths

**User Story**: US-065  
**Type**: Unit  
**Priority**: Medium

### Scenario: returns True when SELECT 1 succeeds

```gherkin
Given a mock engine whose connect() executes without error
When DBConnector().test_connection(engine) is called
Then the result is True
```

### Scenario: returns False when SQLAlchemyError raised

```gherkin
Given a mock engine whose connect().execute() raises SQLAlchemyError
When DBConnector().test_connection(engine) is called
Then the result is False (no exception propagated)
```

### Scenario: returns False when connect() itself raises

```gherkin
Given a mock engine whose connect() raises SQLAlchemyError
When DBConnector().test_connection(engine) is called
Then the result is False
```

---

## TC-083 — execute_query: SELECT and Error Paths

**User Story**: US-065  
**Type**: Unit  
**Priority**: High

### Scenario: valid SELECT returns populated DataFrame

```gherkin
Given a mock engine returning rows [("Alice", 30)] with columns ["name", "age"]
When DBConnector().execute_query(engine, "SELECT name, age FROM users") is called
Then a pandas DataFrame is returned
And len(df) == 1
And df.iloc[0]["name"] == "Alice"
```

### Scenario: empty SELECT result returns empty DataFrame

```gherkin
Given a mock engine returning no rows
When DBConnector().execute_query(engine, "SELECT id FROM t WHERE 1=0") is called
Then an empty DataFrame is returned (not None or exception)
```

### Scenario: non-SELECT statement raises ValueError

```gherkin
Given any valid mock engine
When DBConnector().execute_query(engine, "DROP TABLE users") is called
Then ValueError is raised
And the message contains "Only SELECT statements"
```

### Scenario: SQLAlchemyError during query raises QueryExecutionError

```gherkin
Given a mock engine whose execute() raises SQLAlchemyError
When DBConnector().execute_query(engine, "SELECT bad FROM nonexistent") is called
Then QueryExecutionError is raised
And the message contains "Query execution failed"
```

### Scenario: SELECT with leading whitespace is accepted

```gherkin
Given a valid mock engine
When DBConnector().execute_query(engine, "  SELECT id FROM t  ") is called
Then a DataFrame is returned without ValueError
```
