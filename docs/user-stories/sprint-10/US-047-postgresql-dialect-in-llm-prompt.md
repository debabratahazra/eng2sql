# US-047: Pass Dialect Name into LLM Prompt for PostgreSQL

**Epic**: EPIC-009 — PostgreSQL Live Connection Support
**Sprint**: Sprint 10
**Points**: 1
**Priority**: Must Have
**Source**: PostgreSQL evaluation §3 (US-D) — promoted by Retro Analyzer

## User Story

> As a **user**, I want generated SQL to use PostgreSQL syntax (e.g. `ILIKE`, `::`
> casts, `LIMIT … OFFSET …`, `RETURNING`) when I am connected to a PostgreSQL
> database, so that the SQL the app produces actually runs on my server.

## Acceptance Criteria

```gherkin
Feature: Dialect-aware SQL prompt

  Scenario: PostgreSQL dialect injected into prompt
    Given SQLGenerator.generate(query, schema, dialect="PostgreSQL")
    When the LLM prompt is built
    Then it contains the substring "PostgreSQL"
    And it does NOT contain the substring "MySQL" or "MongoDB"

  Scenario: MySQL dialect remains the default (backward compatibility)
    Given SQLGenerator.generate(query, schema)
    When the LLM prompt is built
    Then it contains "MySQL"
    And no PostgreSQL-specific instructions are present

  Scenario: Generated SQL uses PostgreSQL idioms
    Given a schema with a "users" table and dialect="PostgreSQL"
    When the user asks "find users whose email contains 'gmail' case-insensitively"
    Then the generated SQL uses ILIKE (or LOWER(...)+LIKE) — recorded by an LLM-eval test
```

## Technical Notes

- Update `src/services/sql_generator.py`:
  - Add `"PostgreSQL"` to the existing dialect dispatch (already supports `"MySQL"` /
    `"MongoDB"`).
  - Prompt template: include `f"Generate {dialect}-compatible SQL …"` and a short
    PostgreSQL-specific tip block ("Use ILIKE for case-insensitive match; cast with `::`
    not `CAST AS`; pagination uses LIMIT N OFFSET M.").
- Update `src/app.py` to forward `dialect="PostgreSQL"` when `db_type == "PostgreSQL"`.
- Add 2 LLM eval tests (mocked) in `tests/unit/test_sql_generator.py`:
  - One asserts prompt contains "PostgreSQL" when dialect is PostgreSQL.
  - One asserts the rendered prompt does not leak MySQL-only instructions.

## Definition of Done

- [x] PostgreSQL branch added to `SQLGenerator` dialect dispatch
- [x] Prompt template includes PostgreSQL-specific tips
- [x] `app.py` forwards dialect correctly when db_type=="PostgreSQL"
- [x] 2 unit tests added; existing MySQL/MongoDB tests still pass
- [x] Coverage on `sql_generator.py` remains 100 %
- [x] Code review CR-010 approved

## Status

✅ Done
