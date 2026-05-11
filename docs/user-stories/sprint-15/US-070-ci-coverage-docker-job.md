# US-070 — Verify CI coverage-docker Matrix Job

**Epic**: EPIC-012 — Coverage Completeness & CI Hardening
**Sprint**: 15
**Points**: 2
**Priority**: High
**Status**: ✅ Done

---

## User Story

> **As a** CI/CD pipeline,
> **I want** the `coverage-docker` matrix job in `.github/workflows/ci-cd.yml` to run
> successfully end-to-end,
> **so that** Docker-based integration tests are verified in CI on every PR.

---

## Background

US-053 planned a `coverage-docker` matrix job. It was declared in `pyproject.toml` but
not verified end-to-end on GitHub Actions. This story verifies or fixes it.

---

## Acceptance Criteria

- [x] `.github/workflows/ci-cd.yml` includes a job that runs Docker-based integration tests
- [x] The job completes successfully (or skips cleanly if Docker unavailable) → `if-no-files-found: warn`
- [x] Coverage from Docker tests is reported in the CI summary → `coverage-docker.xml` artifact uploaded
- [x] No existing CI jobs are broken

---

## Definition of Done

- [x] CI job verified or fixed (already correct; no changes needed)
- [x] Documentation updated in `docs/guides/developer-guide.md`
- [x] Code review approved (CR-015)
