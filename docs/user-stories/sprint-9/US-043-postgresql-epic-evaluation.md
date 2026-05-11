# US-043: Evaluate PostgreSQL Live Connection Epic for Sprint 10

**Epic**: EPIC-004 — Quality Assurance / Product
**Sprint**: Sprint 9
**Points**: 2
**Priority**: Could Have
**Source**: Retro — SPRINT-8-retro.md Action Item 4

## User Story

> As a **product owner / scrum master**, I want a formal evaluation of the effort required
> to add PostgreSQL live connection support, so that a decision can be made on whether to
> schedule EPIC-009 for Sprint 10.

## Acceptance Criteria

```gherkin
Feature: PostgreSQL epic evaluation

  Scenario: Evaluation document produced
    Given the codebase architecture is reviewed
    When the effort for PostgreSQL support is assessed
    Then a written evaluation exists at docs/architecture/postgresql-epic-evaluation.md
    And it covers: effort estimate, required code changes, risks, and a Go/No-Go recommendation

  Scenario: Scope defined if Go decision
    Given the evaluation recommends proceeding
    Then EPIC-009 is drafted at docs/epics/EPIC-009-postgresql-support.md
    And at least 3 candidate user stories are outlined

  Scenario: Backlog updated
    Given the evaluation is complete
    Then docs/roadmap.md is updated with the EPIC-009 entry (or "not pursued" note)
```

## Technical Notes

- Review `src/services/db_connector.py` — assess whether SQLAlchemy already supports
  PostgreSQL via `psycopg2` / `asyncpg` without significant changes.
- Review `src/components/sidebar.py` — assess UI changes needed for PostgreSQL host/port/sslmode.
- Review `config/database_config.yaml` — assess schema changes.
- Evaluate `psycopg2-binary` vs `psycopg[binary]` (psycopg3) as the driver choice.
- Document any `ssl` / `sslmode` differences vs. MySQL's `ssl=false` query param.
- Evaluation file: `docs/architecture/postgresql-epic-evaluation.md`

## Definition of Done

- [x] Evaluation document written at `docs/architecture/postgresql-epic-evaluation.md`
- [x] Go/No-Go recommendation documented with rationale _(Decision: ✅ GO; 13 pts; targeted for Sprint 10)_
- [x] If Go: `docs/epics/EPIC-009-postgresql-support.md` drafted _(reconciled by Retro Analyzer on Sprint 10 day 1, 2026-05-07)_
- [x] `docs/roadmap.md` updated
- [x] Code review approved
- [x] Docs updated

## Status

✅ Done
