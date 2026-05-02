# EPIC-004: Quality Assurance

## Goal
Achieve ≥ 80% test coverage across all source modules, enforce linting and type checking
in CI, and produce a signed-off quality report before deployment.

## Business Value
High test coverage and automated quality gates prevent regressions, reduce production
defects, and give stakeholders confidence in each release.

## Scope

### In Scope
- Unit tests for all service classes (`SQLGenerator`, `SchemaDetector`, `DBConnector`)
- Integration tests using in-memory SQLite engine
- `pytest-cov` coverage report (HTML + terminal)
- `ruff` linting with zero warnings
- `mypy` type checking with zero errors
- CI coverage gate (fail build if < 80%)

### Out of Scope
- Load / performance testing (future)
- UI end-to-end tests with Selenium/Playwright (future)
- Mutation testing (future)

## Acceptance Criteria
- [x] AC-1: `pytest --cov=src --cov-fail-under=80` passes
- [x] AC-2: `ruff check src/ tests/` exits with code 0
- [x] AC-3: `mypy src/` exits with code 0
- [x] AC-4: All 13 test cases (TC-001 to TC-013) have corresponding test functions
- [x] AC-5: No `# noqa` or `# type: ignore` without a justification comment

## Dependencies
- Depends on: EPIC-001, EPIC-002, EPIC-003
- Blocks: EPIC-005 (deployment requires passing QA)

## Estimated Size
**T-Shirt Size**: M
**Estimated Sprints**: 1

## Child User Stories
- [x] US-013: Unit Tests — SQL Generator
- [x] US-014: Unit Tests — Schema Detector
- [x] US-015: Integration Tests — DB Connector
- [x] US-016: Linting & Type Checking

## Status
- [x] Draft
- [x] Reviewed
- [x] Accepted
