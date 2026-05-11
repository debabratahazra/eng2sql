# US-049: Documentation Updates for PostgreSQL Support

**Epic**: EPIC-009 — PostgreSQL Live Connection Support
**Sprint**: Sprint 10
**Points**: 2
**Priority**: Must Have
**Source**: PostgreSQL evaluation §3 (US-F) — promoted by Retro Analyzer

## User Story

> As a **new user**, I want clear documentation showing me how to connect Eng2SQL to a
> PostgreSQL server, what `sslmode` to pick, and which Python dependencies are required,
> so that I can be productive without reading source code.

## Acceptance Criteria

```gherkin
Feature: PostgreSQL documentation

  Scenario: User guide includes PostgreSQL walkthrough
    Then docs/guides/user-guide.md contains a "Connecting to PostgreSQL" section
    And it explains the sslmode selectbox values
    And it shows the Step 1 → Step 2 flow with screenshots or annotated steps

  Scenario: Developer guide documents the dialect dispatch
    Then docs/guides/developer-guide.md contains a "PostgreSQL Support" subsection
    And it documents:
      - DBConfig.dialect and sslmode fields
      - DBConnector.list_databases dialect dispatch
      - psycopg3 driver choice rationale (cross-link to evaluation doc)
      - postgres_container fixture usage
      - WSL2 fail-fast pattern shared with MongoDB

  Scenario: README updated
    Then README.md mentions PostgreSQL support in the features section
    And the "Setup" section lists psycopg[binary] as a runtime dependency
    And a PostgreSQL connection example appears in the usage section

  Scenario: Roadmap reflects EPIC-009 completion
    Then docs/roadmap.md moves EPIC-009 from "Future Backlog" to "Delivered"
```

## Technical Notes

- Files to update:
  - `docs/guides/user-guide.md` — new "Connecting to PostgreSQL" section
  - `docs/guides/developer-guide.md` — new "PostgreSQL Support" section + cross-links
  - `README.md` — features list + setup + usage example
  - `docs/roadmap.md` — promote EPIC-009 to "Delivered" once Sprint 10 closes
- Optional: add `config/database_config.yaml` PostgreSQL example block.
- Cross-link to `docs/architecture/postgresql-epic-evaluation.md` for the deep-dive
  on driver choice and risks.

## Definition of Done

- [x] `docs/guides/user-guide.md` updated
- [x] `docs/guides/developer-guide.md` updated
- [x] `README.md` updated
- [x] `docs/roadmap.md` updated
- [x] Code review CR-010 approved (docs lint pass)
- [x] No broken markdown links (verified manually or via linter)

## Status

✅ Done
