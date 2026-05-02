# Test Cases TC-011 to TC-014 — Sprint 3 Quality Assurance

**Stories Covered**: US-013, US-014, US-015, US-016
**Sprint**: Sprint 3
**Written By**: Test Case Writer Agent
**Date**: 2026-05-01

---

## TC-011 — Unit Test Suite: SQL Generator (US-013)

**Feature**: Unit tests for `SQLGenerator.generate_sql()`

```gherkin
Feature: Unit Tests — SQL Generator

  Scenario TC-011-01: Happy-path generation returns clean SQL
    Given a mocked OpenAI client returns "SELECT * FROM orders;"
    When generate_sql("show all orders", schema) is called
    Then the return value equals "SELECT * FROM orders;"
    And the OpenAI mock was called exactly once
    And the system prompt contains the schema context

  Scenario TC-011-02: Markdown fences are stripped
    Given the mocked OpenAI response is "```sql\nSELECT id FROM users;\n```"
    When generate_sql is called
    Then the returned string is "SELECT id FROM users;"
    And no backticks appear in the result

  Scenario TC-011-03: Empty response raises SQLGenerationError
    Given the mocked OpenAI response content is an empty string ""
    When generate_sql is called
    Then SQLGenerationError is raised
    And the error message contains "Empty response from LLM"

  Scenario TC-011-04: OpenAI API error is wrapped as SQLGenerationError
    Given the mocked OpenAI client raises openai.APIError("timeout")
    When generate_sql is called
    Then SQLGenerationError is raised
    And the original openai.APIError is chained as __cause__

  Scenario TC-011-05: Schema context string includes all tables and columns
    Given a schema {"orders": [SchemaColumn("id","INT",False,True)]}
    When _build_schema_context(schema) is called
    Then the returned string contains "orders"
    And the string contains "id" and "INT" and "PRIMARY KEY"

  Scenario TC-011-06: Missing certificate file raises ConfigurationError
    Given OPENAI_CERT_PATH points to a non-existent file
    When SQLGenerator is instantiated
    Then ConfigurationError is raised
    And the error message names the missing path
```

**Pytest file**: `tests/unit/test_sql_generator.py`
**Status**: ✅ Implemented (20 test functions, 100% coverage on `sql_generator.py`)

---

## TC-012 — Unit Test Suite: Schema Detector (US-014)

**Feature**: Unit tests for `SchemaDetector.load_static_schema()` and `detect_live_schema()`

```gherkin
Feature: Unit Tests — Schema Detector

  Scenario TC-012-01: Valid YAML file loads correct schema
    Given a YAML file with tables "customers" and "orders"
    When load_static_schema(path) is called
    Then the returned dict has keys "customers" and "orders"
    And each value is a list of SchemaColumn instances

  Scenario TC-012-02: Missing YAML file raises FileNotFoundError
    Given the config path does not exist
    When load_static_schema(path) is called
    Then FileNotFoundError is raised

  Scenario TC-012-03: Malformed YAML raises SchemaDetectionError
    Given the config file contains invalid YAML syntax
    When load_static_schema(path) is called
    Then SchemaDetectionError is raised
    And the error message references the config path

  Scenario TC-012-04: YAML missing top-level "tables" key raises SchemaDetectionError
    Given the config file has no "tables" key
    When load_static_schema(path) is called
    Then SchemaDetectionError is raised with message containing "'tables' key"

  Scenario TC-012-05: Live schema detection returns correct tables
    Given an in-memory SQLite engine with table "users(id INTEGER, name TEXT)"
    When detect_live_schema(engine) is called
    Then the returned dict contains key "users"
    And the "users" entry has SchemaColumn instances for "id" and "name"

  Scenario TC-012-06: Empty database returns empty schema dict
    Given an in-memory SQLite engine with no tables
    When detect_live_schema(engine) is called
    Then the returned dict is empty {}

  Scenario TC-012-07: SQLAlchemy error during live detection raises SchemaDetectionError
    Given a mock engine whose inspect() raises SQLAlchemyError
    When detect_live_schema(engine) is called
    Then SchemaDetectionError is raised
```

**Pytest file**: `tests/unit/test_schema_detector.py`
**Status**: ✅ Implemented (11 test functions, 90% coverage on `schema_detector.py`)

---

## TC-013 — Integration Test Suite: DB Connector (US-015)

**Feature**: Integration tests for `DBConnector` against an in-memory SQLite engine

```gherkin
Feature: Integration Tests — DB Connector

  Scenario TC-013-01: create_engine with valid SQLite URL returns connected engine
    Given a DBConfig with SQLite in-memory URL
    When create_engine(config) is called
    Then a SQLAlchemy Engine object is returned
    And test_connection(engine) returns True

  Scenario TC-013-02: create_engine with invalid URL raises DatabaseConnectionError
    Given a DBConfig pointing to an unreachable MySQL host
    When create_engine(config) is called
    Then DatabaseConnectionError is raised
    And the error message contains the host name

  Scenario TC-013-03: execute_query returns correct DataFrame for SELECT
    Given an engine with table "products(id, name, price)"
    And the table contains 3 rows
    When execute_query(engine, "SELECT * FROM products") is called
    Then a DataFrame with 3 rows and columns ["id","name","price"] is returned

  Scenario TC-013-04: execute_query rejects non-SELECT statement
    Given a valid connected engine
    When execute_query(engine, "DROP TABLE products") is called
    Then ValueError is raised
    And the error message contains "Only SELECT statements are permitted"

  Scenario TC-013-05: execute_query on bad SQL raises QueryExecutionError
    Given a valid connected engine
    When execute_query(engine, "SELECT * FROM nonexistent_table") is called
    Then QueryExecutionError is raised

  Scenario TC-013-06: test_connection returns False when engine is disposed
    Given an engine that has been disposed
    When test_connection(engine) is called
    Then False is returned without raising an exception

  Scenario TC-013-07: execute_query returns empty DataFrame for zero-row result
    Given a table with no rows
    When execute_query(engine, "SELECT * FROM empty_table") is called
    Then a DataFrame with 0 rows and correct column names is returned
```

**Pytest file**: `tests/integration/test_db_connector.py`
**Status**: ✅ Implemented (7 test functions, 74% coverage on `db_connector.py`)

---

## TC-014 — Linting & Type Checking (US-016)

**Feature**: Static analysis gates on all source code

```gherkin
Feature: Linting & Type Checking

  Scenario TC-014-01: ruff check passes on all source files
    Given the project is checked out
    When "ruff check src/ tests/" is run
    Then exit code is 0
    And no E, W, F, I, or UP violations are reported

  Scenario TC-014-02: ruff format check passes
    Given the project is checked out
    When "ruff format --check src/ tests/" is run
    Then exit code is 0
    And no formatting diffs are reported

  Scenario TC-014-03: mypy strict type checking passes
    Given the project is checked out
    When "mypy src/" is run
    Then exit code is 0
    And no type errors are reported

  Scenario TC-014-04: pre-commit hooks run successfully on staged files
    Given a staged Python file change
    When "pre-commit run --files <file>" is run
    Then all hooks pass
    And no auto-fixes cause the commit to abort unexpectedly

  Scenario TC-014-05: Coverage gate enforced at 80%
    Given the full test suite
    When "pytest --cov=src --cov-fail-under=80" is run
    Then exit code is 0
    And the reported total coverage is ≥ 80%
```

**Pytest file**: N/A (static analysis — run via CI/pre-commit, not pytest)
**Status**: ✅ Configuration verified (`pyproject.toml`, `.pre-commit-config.yaml`)
