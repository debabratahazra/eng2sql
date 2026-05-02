# US-003: Prompt Engineering for Schema Context

**Epic**: EPIC-001
**Sprint**: Sprint 1
**Points**: 3
**Priority**: Must Have

## User Story

> As a **system**, I want the LLM prompt to include table names, column names, and types
> so that the generated SQL is schema-aware and references only real tables and columns.

## Acceptance Criteria

```gherkin
Feature: Schema-Aware Prompt Engineering

  Scenario: Schema context injected into prompt
    Given a schema with tables "customers" and "orders"
    When SQLGenerator.generate_sql() is called
    Then the system prompt sent to OpenAI contains "Table: customers"
    And it contains "Table: orders"
    And each column entry includes the column name and type

  Scenario: Primary key and NOT NULL flags appear in prompt
    Given a schema with a "customers.id" column marked as primary_key=True, nullable=False
    When the schema context is built
    Then the prompt context includes "[PK, NOT NULL]" for that column

  Scenario: Empty schema raises ValueError
    Given an empty schema dict
    When generate_sql() is called
    Then ValueError is raised with message "Schema cannot be empty"

  Scenario: SQL-only response enforced
    Given the system prompt is constructed
    Then it instructs the model to output ONLY the SQL query
    And it forbids INSERT, UPDATE, DELETE, or DROP statements
```

## Technical Notes
- `_build_schema_context(schema)` formats schema into human-readable lines
- `_SYSTEM_PROMPT_TEMPLATE` uses `{dialect}` and `{schema_context}` placeholders
- Dialect defaults to `"MySQL"`; function signature: `generate_sql(question, schema, dialect="MySQL")`
- Implemented in `src/services/sql_generator.py`

## Definition of Done
- [x] `_build_schema_context()` implemented in `src/services/sql_generator.py`
- [x] `_SYSTEM_PROMPT_TEMPLATE` includes schema context and SQL-only instructions
- [x] Unit tests TC-001–TC-004 cover prompt construction indirectly via generate_sql mocks
- [x] Code review approved (CR-001)

## Status
✅ DONE
