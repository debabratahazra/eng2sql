# US-014: Unit Tests — Schema Detector

**Epic**: EPIC-004
**Sprint**: Sprint 3
**Points**: 3
**Priority**: Must Have

## User Story

> As a **developer**, I want unit tests for `SchemaDetector` covering both static YAML
> loading and live SQLAlchemy introspection so that schema detection is regression-proof
> for all supported code paths.

## Acceptance Criteria

```gherkin
Feature: Unit Tests — Schema Detector

  Scenario: Load valid static YAML schema
    Given a YAML file with a "tables" key containing "customers" and "orders"
    When load_static_schema(path) is called
    Then a TableSchema dict with two entries is returned
    And each entry contains a list of SchemaColumn objects with correct attributes

  Scenario: Missing YAML file raises FileNotFoundError
    Given a path that does not exist on disk
    When load_static_schema(path) is called
    Then FileNotFoundError is raised

  Scenario: Malformed YAML raises SchemaDetectionError
    Given a YAML file missing the top-level "tables" key
    When load_static_schema(path) is called
    Then SchemaDetectionError is raised with a descriptive message

  Scenario: detect_live_schema returns all tables and columns
    Given an in-memory SQLite engine with tables "users" and "products"
    When detect_live_schema(engine) is called
    Then the returned dict contains both table names
    And each table entry has SchemaColumn objects with correct name, type, nullable, pk

  Scenario: detect_live_schema on empty database returns empty dict
    Given an in-memory SQLite engine with no tables
    When detect_live_schema(engine) is called
    Then an empty dict is returned with no error raised

  Scenario: Connection failure raises SchemaDetectionError
    Given a mocked engine whose inspect() call raises an exception
    When detect_live_schema(engine) is called
    Then SchemaDetectionError is raised
```

## Technical Notes
- Tests live in `tests/unit/test_schema_detector.py`
- Use `tmp_path` pytest fixture for temporary YAML files
- Use `sqlite_engine` fixture from `conftest.py` for live-schema tests
- Mock SQLAlchemy `inspect` for failure scenarios using `unittest.mock.patch`
- Cover `primary_key`, `nullable`, `default`, and `type` field mapping

## Definition of Done
- [x] `tests/unit/test_schema_detector.py` covers TC-005 to TC-007 scenarios
- [x] 11 test functions passing
- [x] Branch coverage ≥ 90% for `src/services/schema_detector.py`
- [x] Both `load_static_schema` and `detect_live_schema` paths covered
- [x] `ruff` + `mypy` clean on test file
- [x] Code review approved (CR-001)

## Status
✅ DONE
