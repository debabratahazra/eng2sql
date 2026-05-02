# EPIC-005: Deployment & DevOps

## Goal
Package the application as a Docker container, publish a GitHub Actions CI/CD pipeline,
and produce complete deployment documentation so the tool can be run anywhere.

## Business Value
One-command deployment (`docker-compose up`) lowers the barrier to adoption and enables
automated delivery to any environment without manual setup steps.

## Scope

### In Scope
- `Dockerfile` (Python 3.11-slim, non-root user, health check)
- `docker-compose.yml` (app + MySQL services)
- `.env.example` with all required variables documented
- GitHub Actions workflow: lint → test → build → publish (GHCR)
- Deployment runbook (`docs/deployment/runbook.md`)
- Release notes for v1.0.0
- `.pre-commit-config.yaml` for local quality gates
- `pip-audit` check in CI for known CVEs

### Out of Scope
- Kubernetes / Helm charts (future)
- Cloud-provider-specific deployment (AWS ECS, Azure Container Apps) — outlined only
- SSL/TLS termination (assumed handled by upstream proxy)

## Acceptance Criteria
- [x] AC-1: `docker-compose up` starts the app accessible at `http://localhost:8501`
- [x] AC-2: GitHub Actions pipeline runs on every push to `main` and on PRs
- [x] AC-3: Pipeline fails fast if lint, tests, or coverage gate fails
- [x] AC-4: Docker image published to GHCR on successful `main` build
- [x] AC-5: `pip-audit` reports zero critical CVEs
- [x] AC-6: Runbook covers local dev, Docker, and rollback procedures

## Dependencies
- Depends on: EPIC-004 (all tests must pass)
- Blocks: None (final epic)

## Estimated Size
**T-Shirt Size**: M
**Estimated Sprints**: 1

## Child User Stories
- [x] US-017: Dockerfile & Docker Compose
- [x] US-018: GitHub Actions CI/CD Pipeline
- [x] US-019: Deployment Runbook & Release Notes
- [x] US-020: Pre-commit Hooks & Dependency Audit

## Status
- [x] Draft
- [x] Reviewed
- [x] Accepted
