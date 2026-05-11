# US-037: Increase Test Coverage for `MongoConfig` Uncovered Branches

**Epic**: EPIC-008
**Sprint**: Sprint 8
**Points**: 2
**Priority**: Should Have
**Source**: Retro — SPRINT-7-retro.md

## User Story

> As a **developer**, I want tests covering `MongoConfig.__repr__` and the `else` branch
> of `_connection_uri_from_raw`, so that these code paths are validated and the coverage
> report no longer flags them as missed lines.

## Acceptance Criteria

```gherkin
Feature: MongoConfig branch coverage

  Scenario: __repr__ is tested
    Given a MongoConfig instance with host, port, and username populated
    When repr() is called on the instance
    Then the returned string contains the host and username
    And no exception is raised

  Scenario: _connection_uri_from_raw else branch is tested
    Given a MongoConfig with raw_uri set to a plain mongodb:// URI (not SRV)
    When connection_uri property is accessed
    Then the URI is returned with directConnection=true logic intact
    And the result matches the expected non-SRV URI format

  Scenario: Coverage gate remains satisfied
    Given the full test suite is run with pytest --cov=src
    Then coverage for src/models/config.py is ≥ 90%
    And the overall project coverage remains ≥ 80%
```

## Technical Notes
- Lines to cover: `config.py` lines ~104, ~108, ~126-127 (per Sprint 7 retro)
- Add tests to `tests/unit/test_mongo_connector.py` or a dedicated `test_config.py`
- `__repr__` test: instantiate `MongoConfig`, call `repr()`, assert key fields appear
- `else` branch: pass a `mongodb://` URI (non-SRV) to `_connection_uri_from_raw` and verify output

## Definition of Done
- [x] Code implemented (two new tests added to `tests/unit/test_mongo_connector.py` in `TestMongoConfig`)
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated

## Status
✅ Done
