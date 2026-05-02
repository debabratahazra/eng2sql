# Sprint 4 Retrospective

**Sprint**: Sprint 4 — Deployment & DevOps
**Date**: 2026-06-25
**Facilitator**: Scrum Master

---

## What Went Well

- v1.0.0 shipped on schedule — all 4 stories delivered at 16/16 points
- Docker non-root user (`appuser`) pattern implemented cleanly — security baseline met
- GitHub Actions pipeline covers lint → test → coverage gate → build → publish in one workflow
- `pip-audit` clean — zero critical CVEs in `requirements.txt`
- `docs/deployment/` suite comprehensive: runbook, release notes, secrets setup, monitoring
- Pre-commit hooks (`detect-private-key`, `no-commit-to-branch`) work correctly
- `.gitignore` hardened with `*.key`, `*.pem`, `*.p12`, `*.pfx` — no accidental key commits
- Architecture docs (ADR-001–005, api-contracts.md, security.md) completed alongside sprint

## What Could Be Improved

- Sprint 4 point total (16) differed from the original roadmap estimate (12) — US-017–020
  were re-estimated when story files were written; roadmap should be kept in sync
- `docs/deployment/monitoring.md` outlines alerting for Sprint 4+ but SIEM integration
  and structured logging are still future work
- No load or performance testing was done — P95 < 5 s latency target is aspirational;
  baseline measurements should be taken before v2 planning
- `AppTest`-based UI tests (BUG-001) remain unresolved — should be scheduled as a
  dedicated story in the next sprint

## Action Items

| Action                                                         | Owner              | Due                   |
| -------------------------------------------------------------- | ------------------ | --------------------- |
| Schedule US-021: AppTest UI coverage for next sprint           | Scrum Master       | Sprint 5 planning     |
| Measure actual P95 SQL generation latency against target       | Developer / DevOps | Sprint 5              |
| Set up structured logging + log aggregation (ELK / CloudWatch) | DevOps             | Sprint 5              |
| Update roadmap.md story point totals to match actual estimates | Scrum Master       | Done (Sprint 4 retro) |

---

## Cumulative Velocity

| Sprint   | Committed | Delivered | Cumulative |
| -------- | --------- | --------- | ---------- |
| Sprint 1 | 21        | 21        | 21         |
| Sprint 2 | 21        | 21        | 42         |
| Sprint 3 | 13        | 13        | 55         |
| Sprint 4 | 16        | 16        | 71         |

**Total delivered**: 71 story points across 20 stories in 4 sprints
