# Test Cases TC-015 to TC-018 — Sprint 4 Deployment & DevOps

**Stories Covered**: US-017, US-018, US-019, US-020
**Sprint**: Sprint 4
**Written By**: Test Case Writer Agent
**Date**: 2026-05-01

---

## TC-015 — Dockerfile & Docker Compose (US-017)

**Feature**: Container build and startup verification

```gherkin
Feature: Dockerfile & Docker Compose

  Scenario TC-015-01: Docker image builds without errors
    Given the repository root contains a valid Dockerfile
    When "docker build -t eng2sql:test ." is run
    Then the build exits with code 0
    And the image is based on python:3.11-slim
    And all Python dependencies from requirements.txt are installed

  Scenario TC-015-02: Application runs as non-root user
    Given the eng2sql:test image is built
    When "docker run --rm eng2sql:test whoami" is run
    Then the output is "appuser"
    And the UID is 1001

  Scenario TC-015-03: Health check endpoint responds
    Given the container is running with docker-compose
    When a GET request is made to "http://localhost:8501/_stcore/health"
    Then the response status is 200
    And the container health status transitions to "healthy" within 60 seconds

  Scenario TC-015-04: docker-compose up starts both services
    Given docker-compose.yml defines "app" and "db" services
    When "docker-compose up -d" is run
    Then both containers reach running state
    And the app container can reach the db container on port 3306

  Scenario TC-015-05: Secrets supplied via environment variables only
    Given the running container
    When "docker inspect eng2sql_app" is run
    Then OPENAI_API_KEY value is not present in image layer metadata
    And the .env file is not embedded in the image

  Scenario TC-015-06: .env.example documents all required variables
    Given the project root contains .env.example
    When its contents are inspected
    Then OPENAI_API_KEY, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME are present
    And each variable has a descriptive comment
```

**Pytest file**: N/A (Docker integration — verified manually or via CI build job)
**Status**: ✅ `Dockerfile` and `docker-compose.yml` present and reviewed (CR-004)

---

## TC-016 — GitHub Actions CI/CD Pipeline (US-018)

**Feature**: Automated CI/CD pipeline correctness

```gherkin
Feature: GitHub Actions CI/CD Pipeline

  Scenario TC-016-01: Lint job passes on clean code
    Given a push to the main branch with compliant code
    When the "Lint & Type Check" job runs
    Then ruff and mypy both exit 0
    And the job status is "success"

  Scenario TC-016-02: Test job is blocked when lint fails
    Given a push with a ruff violation
    When the "Tests & Coverage" job is triggered
    Then the job is skipped or fails due to "needs: lint" dependency
    And no test run is attempted

  Scenario TC-016-03: Coverage gate blocks merge on low coverage
    Given a code change that drops coverage below 80%
    When the "Tests & Coverage" job runs
    Then pytest exits with code 1
    And the CI check status is "failure"

  Scenario TC-016-04: Docker image is built and pushed on main merge
    Given a merged pull request to main
    When the "Build & Push Docker Image" job runs
    Then the image is pushed to ghcr.io with "latest" and "<sha>" tags
    And no errors appear in the build log

  Scenario TC-016-05: Workflow runs on pull_request to main
    Given a pull request opened against main
    When the CI pipeline runs
    Then all jobs (lint, test) execute
    And the build/push job is skipped (push only)
```

**Pytest file**: N/A (CI verification — executed by GitHub Actions runner)
**Status**: ✅ `.github/workflows/ci-cd.yml` present and reviewed (CR-004)

---

## TC-017 — Deployment Runbook & Release Notes (US-019)

**Feature**: Deployment documentation completeness

```gherkin
Feature: Deployment Runbook & Release Notes

  Scenario TC-017-01: Runbook covers first-time deployment steps
    Given docs/deployment/runbook.md exists
    When a new operator reads it
    Then they can deploy the application following the steps alone
    And the runbook includes: clone, .env setup, docker-compose up, health check

  Scenario TC-017-02: Runbook covers rollback procedure
    Given a failed deployment
    When the operator follows the rollback section
    Then the previous version is restored
    And downtime is minimised

  Scenario TC-017-03: Release notes describe v1.0.0 features
    Given docs/deployment/RELEASE-1.0.0.md exists
    When it is reviewed
    Then it lists all 20 user stories as delivered features
    And it documents known limitations

  Scenario TC-017-04: Secrets setup guide is complete
    Given docs/deployment/secrets-setup.md exists
    When reviewed
    Then it documents how to create each required GitHub Actions secret
    And it includes key rotation procedures
```

**Pytest file**: N/A (documentation review)
**Status**: ✅ All deployment docs present in `docs/deployment/`

---

## TC-018 — Pre-commit Hooks & Dependency Audit (US-020)

**Feature**: Pre-commit hook execution and dependency hygiene

```gherkin
Feature: Pre-commit Hooks & Dependency Audit

  Scenario TC-018-01: pre-commit install sets up hooks correctly
    Given the repository is cloned fresh
    When "pre-commit install" is run
    Then hooks are installed in .git/hooks/pre-commit
    And exit code is 0

  Scenario TC-018-02: ruff hook auto-fixes style issues on commit
    Given a staged file with a fixable ruff violation (unused import)
    When "git commit" is triggered
    Then the pre-commit ruff hook removes the unused import
    And the commit is aborted so the developer can re-stage the fix

  Scenario TC-018-03: Large file hook blocks commits over 500 KB
    Given a staged file larger than 500 KB
    When "git commit" is triggered
    Then the large-file hook blocks the commit
    And an error message identifies the oversized file

  Scenario TC-018-04: .gitignore excludes secrets and keys
    Given the .gitignore file
    When inspected
    Then *.env, *.key, *.pem, __pycache__/, .venv/, and dist/ are excluded
    And "git status" does not show these paths as untracked

  Scenario TC-018-05: pip-audit reports no critical vulnerabilities
    Given requirements.txt is installed
    When "pip-audit -r requirements.txt" is run
    Then no CRITICAL or HIGH severity CVEs are reported
    And the exit code is 0
```

**Pytest file**: N/A (tool-chain verification)
**Status**: ✅ `.pre-commit-config.yaml` present and reviewed (CR-004); `.gitignore` hardened
