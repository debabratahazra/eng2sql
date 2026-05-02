# US-009: Schema Auto-Detection

**Epic**: EPIC-003
**Sprint**: Sprint 2
**Points**: 5
**Priority**: Must Have

## User Story

> As a **system**, I want SQLAlchemy `inspect()` to enumerate all tables and columns
> from a live database connection so that the SQL generator always has an accurate,
> up-to-date schema context.

## Acceptance Criteria

```gherkin
Feature: Live Schema Detection

  Scenario: Detect tables and columns
    Given a connected SQLAlchemy engine to a MySQL database
    When SchemaDetector.detect_live_schema(engine) is called
    Then it returns a dict with one key per table in the database
    And each value is a list of column dicts with name, type, nullable, primary_key

  Scenario: Empty database
    Given a database with no tables
    When detect_live_schema is called
    Then it returns an empty dict (no error raised)

  Scenario: Schema cached in session
    Given schema has already been detected in this Streamlit session
    When the user triggers another SQL generation
    Then detect_live_schema is NOT called again (uses cached value)
    And the session cache is invalidated when user clicks "Refresh Schema"

  Scenario: Connection dropped
    Given the DB connection drops during schema detection
    When detect_live_schema is called
    Then SchemaDetectionError is raised with a descriptive message
```

## Technical Notes
- Use `sqlalchemy.inspect(engine).get_table_names()` and `get_columns(table)`
- Cache result in `st.session_state["detected_schema"]`
- `type` value: use `str(col["type"])` for human-readable type names
- Add "Refresh Schema" button next to Schema Viewer

## Definition of Done
- [x] `SchemaDetector.detect_live_schema()` implemented
- [x] Schema cached in `st.session_state`
- [x] Unit test TC-007 passing
- [x] Integration tests (TC-008–TC-010) passing (SQLite in-memory)
- [x] Code review approved (CR-001)

## Status
✅ DONE
