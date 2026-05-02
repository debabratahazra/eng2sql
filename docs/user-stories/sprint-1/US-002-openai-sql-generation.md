# US-002: OpenAI SQL Generation Service

**Epic**: EPIC-001
**Sprint**: Sprint 1
**Points**: 5
**Priority**: Must Have

## User Story

> As a **user**, I want to type an English question and receive a valid MySQL SELECT
> statement so that I can query my database without knowing SQL syntax.

## Acceptance Criteria

```gherkin
Feature: SQL Generation from English

  Scenario: Simple SELECT generation
    Given a valid schema with a "customers" table
    And the OpenAI API is available
    When I call generate_sql("Show all customers", schema)
    Then the result starts with "SELECT"
    And the result references the "customers" table

  Scenario: Filtered query generation
    Given a schema with "orders" table containing "status" column
    When I call generate_sql("Show pending orders", schema)
    Then the result contains "WHERE" and references "status"

  Scenario: Empty question input
    When I call generate_sql("", schema)
    Then ValueError is raised with message "Question cannot be empty"

  Scenario: OpenAI API unavailable
    Given the OpenAI API returns a 500 error
    When I call generate_sql("Show all customers", schema)
    Then SQLGenerationError is raised with a user-friendly message

  Scenario: Response cleaning
    Given OpenAI returns SQL wrapped in markdown code fences
    When generate_sql is called
    Then the returned string has no backticks or "sql" prefix
```

## Technical Notes
- Model: `gpt-5.2` (configurable via `OPENAI_MODEL` env var)
- Base URL: `https://gpt4ifx.icp.infineon.com` (configurable via `OPENAI_BASE_URL`)
- TLS cert: `cert/ca-bundle.crt` (configurable via `OPENAI_CERT_PATH`)
- Auth: Bearer token via `Authorization` header (`OPENAI_API_KEY`)
- Temperature: `0.1` (low for deterministic SQL output)
- Max tokens: `500` (sufficient for complex SELECT queries)
- Strip ` ```sql ` and ` ``` ` markers from response

## Definition of Done
- [x] `SQLGenerator` class implemented in `src/services/sql_generator.py`
- [x] `SQLGenerationError` defined in `src/utils/exceptions.py`
- [x] Unit tests TC-001, TC-002, TC-003, TC-004 passing
- [x] No real OpenAI API calls in unit tests
- [x] Code review approved

## Status
✅ DONE
