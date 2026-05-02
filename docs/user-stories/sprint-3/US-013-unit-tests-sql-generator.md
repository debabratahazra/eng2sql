# US-013: Unit Tests — SQL Generator

**Epic**: EPIC-004
**Sprint**: Sprint 3
**Points**: 3
**Priority**: Must Have

## User Story

> As a **developer**, I want comprehensive unit tests for `SQLGenerator` so that every
> code path — including prompt building, OpenAI response handling, and error cases — is
> verified in isolation without hitting a real API.

## Acceptance Criteria

```gherkin
Feature: Unit Tests — SQL Generator

  Scenario: Happy-path SQL generation returns cleaned query
    Given a mocked OpenAI client that returns "SELECT * FROM orders;"
    When generate_sql("show all orders", schema) is called
    Then the return value is "SELECT * FROM orders;"
    And the mock was called with the correct system prompt and user message

  Scenario: Markdown code fences are stripped from the response
    Given the mocked OpenAI response wraps SQL in ```sql ... ``` fences
    When generate_sql is called
    Then the returned string contains no backticks or "sql" language tag

  Scenario: Empty response raises SQLGenerationError
    Given the mocked OpenAI response content is an empty string
    When generate_sql is called
    Then SQLGenerationError is raised with message "Empty response from LLM"

  Scenario: OpenAI API error raises SQLGenerationError
    Given the mocked OpenAI client raises openai.APIError
    When generate_sql is called
    Then SQLGenerationError is raised wrapping the original exception

  Scenario: Schema context is included in the prompt
    Given a schema with tables "orders" and "customers"
    When _build_schema_context(schema) is called
    Then the returned string contains both table names and their column definitions
```

## Technical Notes
- Tests live in `tests/unit/test_sql_generator.py`
- Use `unittest.mock.patch` to mock `openai.OpenAI` client; keep mocks inside `with` block
- Test `_build_schema_context()` directly for schema formatting coverage
- Use `pytest.raises` for all error scenarios
- SSL context creation tested via mock to avoid filesystem dependency

## Definition of Done
- [x] `tests/unit/test_sql_generator.py` covers TC-001 to TC-004 scenarios
- [x] 20 test functions passing
- [x] Branch coverage ≥ 95% for `src/services/sql_generator.py`
- [x] No real API calls made (all mocked)
- [x] `ruff` + `mypy` clean on test file
- [x] Code review approved (CR-001)

## Status
✅ DONE
