# Sprint 4 Plan

**Goal**: Production-ready Docker image, CI/CD pipeline on GitHub Actions, deployment documentation, pre-commit hooks, and v1.0.0 release
**Duration**: 2026-06-12 → 2026-06-25 (2 weeks)
**Velocity Target**: 16 points

---

## Committed Stories

| Story ID | Title                               | Points | Assignee (Agent) |
| -------- | ----------------------------------- | ------ | ---------------- |
| US-017   | Dockerfile & Docker Compose         | 5      | Deployment Agent |
| US-018   | GitHub Actions CI/CD Pipeline       | 5      | Deployment Agent |
| US-019   | Deployment Runbook & Release Notes  | 3      | Deployment Agent |
| US-020   | Pre-commit Hooks & Dependency Audit | 3      | DevOps           |

**Total**: 16 points

---

## Definition of Done

- [x] `docker build` completes without errors
- [x] `docker-compose up` starts Streamlit at `http://localhost:8501`
- [x] GitHub Actions workflow runs on push to `main` and on PRs
- [x] CI pipeline enforces lint → test → build → publish order
- [x] `pip-audit` reports zero critical CVEs
- [x] Deployment runbook, release notes, secrets setup, and monitoring docs complete
- [x] `.pre-commit-config.yaml` hooks verified
- [x] `.gitignore` includes private key patterns
- [x] v1.0.0 release tag documented

---

## Sprint Risks

| Risk                                               | Likelihood | Impact | Mitigation                                                                              |
| -------------------------------------------------- | ---------- | ------ | --------------------------------------------------------------------------------------- |
| GHCR push fails without `GITHUB_TOKEN` permissions | Medium     | Medium | Set `packages: write` permission in workflow; document in runbook                       |
| `pip-audit` flags transitive dependency CVE        | Medium     | Medium | Pin or upgrade affected package; use `--ignore-vuln` with justification if low severity |
| Docker non-root user breaks file permissions       | Low        | Medium | `chown -R appuser /app` in Dockerfile; test with `docker exec ... whoami`               |
| Corporate proxy blocks GHCR image pulls            | Low        | High   | Document private registry mirror as fallback in runbook                                 |

---

## Outcome

**Status**: ✅ DONE
**Actual Velocity**: 16 / 16 points (100%)
**Notes**: v1.0.0 released. Runbook, secrets guide, and monitoring docs complete. `pip-audit` clean. DevOps hardening (`secrets-setup.md`, `monitoring.md`, `.gitignore` private key patterns) delivered.
