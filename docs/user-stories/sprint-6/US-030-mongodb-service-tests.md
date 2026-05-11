# US-030: Unit & Integration Tests for MongoDB Services

**Epic**: EPIC-007
**Sprint**: Sprint 6
**Points**: 5
**Priority**: Must Have

## User Story

> As a **developer**, I want comprehensive unit tests for `MongoDBConnector` and
> `MongoSchemaDetector` so that the MongoDB integration has ≥ 80% test coverage
> and regressions are caught by CI.

## Acceptance Criteria

```gherkin
Feature: MongoDB Service Tests

  Scenario: MongoDBConnector unit tests pass
    Given the MongoDBConnector service is implemented
    When the unit test suite runs
    Then tests cover connect() success, connect() failure, list_databases() filtering,
      and get_database() return value
    And all tests pass without hitting a real MongoDB server

  Scenario: MongoSchemaDetector unit tests pass
    Given the MongoSchemaDetector service is implemented
    When the unit test suite runs
    Then tests cover schema detection with populated collections, empty collections,
      multi-document field union, and driver failure (SchemaDetectionError)
    And all tests pass with a mocked pymongo Database object

  Scenario: Sidebar MongoDB flow unit tests pass
    Given the sidebar renders the MongoDB connection form
    When the unit test suite runs
    Then tests cover db_type radio state, mongo step 1 and step 2 rendering,
      and state isolation between MySQL and MongoDB flows

  Scenario: Overall coverage gate maintained
    Given all MongoDB tests are added
    When pytest --cov=src --cov-fail-under=80 runs
    Then the coverage gate passes
```

## Technical Notes
- New files: `tests/unit/test_mongo_connector.py`, `tests/unit/test_mongo_schema_detector.py`
- Mock `pymongo.MongoClient` using `unittest.mock.MagicMock` — never connect to a real server
- Add `mongo_config` fixture to `tests/conftest.py`
- Use `pytest.mark.parametrize` for type-mapping tests in `MongoSchemaDetector`
- Mock `client.admin.command("ping")` to simulate successful ping
- Mock `client.list_database_names()` to control database list in filtering tests

## Definition of Done
- [x] Code implemented
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated (if needed)

## Status
✅ Done
