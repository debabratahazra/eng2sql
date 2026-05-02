# US-018: GitHub Actions CI/CD Pipeline

**Epic**: EPIC-005
**Sprint**: Sprint 4
**Points**: 5
**Priority**: Must Have

## User Story

> As a **developer**, I want a GitHub Actions workflow that automatically lints, tests,
> and builds the Docker image on every push and pull request so that quality gates are
> enforced without manual intervention.

## Acceptance Criteria

```gherkin
Feature: GitHub Actions CI/CD Pipeline

  Scenario: Pipeline runs on push to main and on pull requests
    Given a commit is pushed to the main branch
    When the GitHub Actions workflow triggers
    Then all jobs (lint, test, build, publish) execute in order
    And subsequent jobs are skipped if an earlier job fails

  Scenario: Lint job fails fast on ruff or mypy errors
    Given a PR introduces a ruff lint violation
    When the lint job runs
    Then the job exits with a non-zero code
    And the PR cannot be merged until the violation is fixed

  Scenario: Test job enforces coverage gate
    Given the test job runs pytest with --cov-fail-under=80
    When coverage drops below 80%
    Then the test job fails and the pipeline stops

  Scenario: Docker image published to GHCR on main merge
    Given all lint and test jobs pass on main
    When the build job runs
    Then the Docker image is tagged with the commit SHA and "latest"
    And it is pushed to ghcr.io/<org>/eng2sql

  Scenario: pip-audit reports zero critical CVEs
    Given the CI pipeline runs pip-audit
    When known critical CVEs are found in dependencies
    Then the audit step fails and the pipeline stops
```

## Technical Notes
- Workflow file: `.github/workflows/ci-cd.yml`
- Jobs: `lint` → `test` → `build` → `publish` (sequential with `needs:`)
- `lint` job: `ruff check src/ tests/` + `mypy src/`
- `test` job: `pytest --cov=src --cov-fail-under=80 --cov-report=xml`; upload coverage as artifact
- `build` job: `docker build` with `--cache-from`; uses `GITHUB_TOKEN` for GHCR push
- `pip-audit` runs in the `test` job after pytest
- Secrets: `OPENAI_API_KEY` set as GitHub Actions repository secret (never logged)

## Definition of Done
- [x] `.github/workflows/ci-cd.yml` created with lint, test, build, publish jobs
- [x] Pipeline triggers on `push` to `main` and on `pull_request`
- [x] Coverage report uploaded as artifact on every test run
- [x] Docker image pushed to GHCR on successful `main` build
- [x] `pip-audit` step runs and fails build on critical CVEs
- [x] No secrets logged in pipeline output
- [x] Code review approved

## Status
✅ DONE
