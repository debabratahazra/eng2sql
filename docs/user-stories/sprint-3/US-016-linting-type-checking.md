# US-016: Linting & Type Checking

**Epic**: EPIC-004
**Sprint**: Sprint 3
**Points**: 2
**Priority**: Must Have

## User Story

> As a **developer**, I want `ruff` linting and `mypy` strict type checking enforced
> in CI so that code style and type safety are verified automatically on every commit.

## Acceptance Criteria

```gherkin
Feature: Linting & Type Checking

  Scenario: ruff passes with zero warnings
    Given all source files in src/ and tests/
    When "ruff check src/ tests/" is executed
    Then it exits with code 0
    And no warnings or errors are printed

  Scenario: mypy passes with zero errors
    Given all source files in src/
    When "mypy src/" is executed
    Then it exits with code 0
    And no type errors are reported

  Scenario: Pre-commit hooks prevent bad commits
    Given a file with a linting violation staged for commit
    When "git commit" is run
    Then the pre-commit hook runs ruff and rejects the commit
    And the developer sees the lint error with file and line number

  Scenario: Coverage gate enforced in CI
    Given the test suite runs in GitHub Actions
    When pytest --cov-fail-under=80 runs
    Then the pipeline fails if total coverage drops below 80%
    And a coverage report is uploaded as an artifact
```

## Technical Notes
- `ruff` config in `pyproject.toml` under `[tool.ruff]` — `select = ["E", "F", "I", "N", "UP"]`
- `mypy` config in `pyproject.toml` under `[tool.mypy]` — `strict = true`, `python_version = "3.11"`
- `.pre-commit-config.yaml` hooks: `ruff v0.4.4`, `mypy v1.9.0`, `detect-private-key`, `no-commit-to-branch main`
- UI layer (`src/app.py`, `src/components/`) excluded from coverage via `pyproject.toml` omit (BUG-001 deferred Sprint 3)
- `pip-audit` run in CI as a separate step (covered by US-020)

## Definition of Done
- [x] `pyproject.toml` configured with `[tool.ruff]`, `[tool.mypy]`, `[tool.coverage]` sections
- [x] `ruff check src/ tests/` exits 0
- [x] `mypy src/` exits 0
- [x] `.pre-commit-config.yaml` created with ruff, mypy, detect-private-key hooks
- [x] `pytest --cov=src --cov-fail-under=80` passes at 91% coverage
- [x] CI workflow enforces lint + type-check steps before test step
- [x] Code review approved (CR-001)

## Status
✅ DONE
