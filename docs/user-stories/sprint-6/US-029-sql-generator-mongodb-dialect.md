# US-029: SQL Generator MongoDB Dialect

**Epic**: EPIC-007
**Sprint**: Sprint 6
**Points**: 3
**Priority**: Must Have

## User Story

> As a **user connected to a MongoDB database**, I want the query generator to
> produce a MongoDB `find()` or aggregation pipeline statement (not MySQL SQL)
> so that the generated query is valid for my MongoDB database.

## Acceptance Criteria

```gherkin
Feature: SQL Generator MongoDB Dialect

  Scenario: MongoDB dialect produces find() or aggregation output
    Given db_type is "MongoDB" and a schema is detected
    When the user submits an English question
    Then the LLM prompt instructs the model to output MongoDB syntax
    And the output panel displays a db.<collection>.find() or aggregate() statement
    And no MySQL-specific keywords (SELECT, FROM, WHERE) appear in the prompt template

  Scenario: MySQL dialect is unchanged
    Given db_type is "MySQL"
    When the user submits an English question
    Then the LLM prompt instructs the model to output MySQL SELECT syntax
    And behaviour is identical to pre-MongoDB implementation

  Scenario: Page header reflects active database type
    Given db_type is "MongoDB"
    When the main page renders
    Then the subtitle reads "… get a valid MongoDB query …"
    Given db_type is "MySQL"
    Then the subtitle reads "… get a valid MySQL query …"
```

## Technical Notes
- `SQLGenerator.generate_sql()` already accepts `dialect: str = "MySQL"` — no change needed to service
- `app.py`: pass `dialect="MongoDB"` when `st.session_state.get("db_type") == "MongoDB"`
- `_SYSTEM_PROMPT_TEMPLATE` in `sql_generator.py`: already uses `{dialect}` placeholder;
  update Rules section to say "Write read-only SELECT / find() queries only" for completeness
- App title subtitle: branch on `db_type` session-state key
- The "Execute SQL" button should be hidden when `db_type == "MongoDB"` (execution not yet implemented)

## Definition of Done
- [x] Code implemented
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated (if needed)

## Status
✅ Done
