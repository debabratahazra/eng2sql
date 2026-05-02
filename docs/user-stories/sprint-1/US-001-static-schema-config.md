# US-001: Static Schema Configuration

**Epic**: EPIC-001
**Sprint**: Sprint 1
**Points**: 3
**Priority**: Must Have

## User Story

> As a **developer**, I want a YAML-based static schema definition so that the SQL
> generator has table/column context without requiring a live database connection.

## Acceptance Criteria

```gherkin
Feature: Static Schema Loading

  Scenario: Load valid schema YAML
    Given a valid YAML file exists at config/database_config.yaml
    When SchemaDetector.load_static_schema() is called with that path
    Then it returns a dict mapping table names to lists of column definitions
    And each column definition includes name, type, nullable, and primary_key

  Scenario: Missing schema file
    Given no file exists at the given path
    When SchemaDetector.load_static_schema() is called
    Then it raises FileNotFoundError with a descriptive message

  Scenario: Malformed YAML
    Given a file with invalid YAML syntax
    When SchemaDetector.load_static_schema() is called
    Then it raises ValueError with a descriptive message
```

## Technical Notes
- Schema YAML path configurable via `STATIC_SCHEMA_PATH` env var
- Default path: `config/database_config.yaml`
- Schema format: `{table_name: [{name, type, nullable, primary_key}]}`

## Definition of Done
- [x] `config/database_config.yaml` created with e-commerce sample schema
- [x] `SchemaDetector.load_static_schema()` implemented
- [x] Unit tests TC-005, TC-006 passing
- [x] Code review approved

## Status
✅ DONE
