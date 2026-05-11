# US-053 — `coverage-docker` GitHub Actions matrix job

**Sprint**: Sprint 11
**Source**: SPRINT-10-retro.md "Action Items" — carry-over from Sprint 9 retro
**Points**: 2
**Owner**: DevOps

## User Story

As a **CI maintainer**, I want a `coverage-docker` job in `.github/workflows/ci-cd.yml`
that spins up a Docker daemon and runs `pytest -m docker` so the 8 currently-skipped
MySQL + PostgreSQL integration tests actually execute on every PR, raising effective
coverage on `db_connector.py` from 80 % → ≥ 95 %.

## Acceptance Criteria

1. New job `coverage-docker` added to `.github/workflows/ci-cd.yml`:
   - `runs-on: ubuntu-latest` (Docker-in-Docker provided natively)
   - Steps: checkout, setup-python 3.11+, `pip install -r requirements.txt`,
     `pytest -m docker -v --cov=src --cov-report=xml`
   - Uploads `coverage.xml` as an artifact
2. Job runs in parallel with the existing unit job; both must pass for the workflow to
   succeed.
3. Job timeout ≤ 10 minutes.
4. README updated with a "CI status" subsection explaining the matrix.

## Definition of Done

- [x] `coverage-docker` job added to workflow
- [x] Workflow YAML lints clean
- [x] Job runs on a sample PR and exits 0
- [x] README updated
- [x] CR-011 approved

## Status

✅ Done
