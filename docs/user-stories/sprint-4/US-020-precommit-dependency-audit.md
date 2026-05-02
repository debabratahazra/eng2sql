# US-020: Pre-commit Hooks & Dependency Audit

**Epic**: EPIC-005
**Sprint**: Sprint 4
**Points**: 3
**Priority**: Must Have

## User Story

> As a **developer**, I want pre-commit hooks that run linting and security checks
> locally before every commit, and a `pip-audit` step in CI so that vulnerabilities
> and style violations are caught before they reach the repository.

## Acceptance Criteria

```gherkin
Feature: Pre-commit Hooks & Dependency Audit

  Scenario: Pre-commit blocks commit with lint violation
    Given .pre-commit-config.yaml is installed (pre-commit install)
    And a staged file contains a ruff lint violation
    When "git commit" is run
    Then the ruff hook blocks the commit
    And the developer sees the file path and violation description

  Scenario: Pre-commit blocks commit of private key file
    Given a file matching *.key or *.pem is staged
    When "git commit" is run
    Then the detect-private-key hook blocks the commit
    And no key material is committed

  Scenario: Pre-commit blocks direct commit to main
    Given the current branch is "main"
    When "git commit" is run
    Then the no-commit-to-branch hook blocks the commit
    And the developer is redirected to create a feature branch

  Scenario: pip-audit reports zero critical CVEs in CI
    Given requirements.txt lists all project dependencies
    When "pip-audit -r requirements.txt" runs in GitHub Actions
    Then the step passes if no critical CVEs are found
    And the step fails and lists affected packages if critical CVEs are found

  Scenario: pip-audit can be run locally
    Given pip-audit is installed (pip install pip-audit)
    When a developer runs "pip-audit -r requirements.txt"
    Then a clean report is shown or vulnerabilities are listed with CVE IDs
```

## Technical Notes
- `.pre-commit-config.yaml` hooks: `ruff v0.4.4`, `mypy v1.9.0`, `pre-commit-hooks v4.6.0`
- `pre-commit-hooks` used: `detect-private-key`, `no-commit-to-branch` (args: `--branch main`)
- `pip-audit` runs as a CI step in `.github/workflows/ci-cd.yml` after `pip install -r requirements.txt`
- `.gitignore` hardened with `*.key`, `*.pem`, `*.p12`, `*.pfx` patterns (DevOps sprint)
- `cert/ca-bundle.crt` is a public CA cert — intentionally tracked; not a private key

## Definition of Done
- [x] `.pre-commit-config.yaml` created with ruff, mypy, detect-private-key, no-commit-to-branch
- [x] `pre-commit install` documented in `docs/guides/developer-guide.md`
- [x] `pip-audit` step added to `.github/workflows/ci-cd.yml`
- [x] `.gitignore` updated with private key patterns
- [x] All hooks verified to trigger on appropriate violations
- [x] `pip-audit` reports zero critical CVEs on current `requirements.txt`
- [x] Code review approved

## Status
✅ DONE
