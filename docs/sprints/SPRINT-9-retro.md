# Sprint 9 Retrospective

**Sprint**: Sprint 9 — Coverage Completeness & Developer Experience
**Date**: 2026-05-07
**Facilitator**: Scrum Master

---

## What Went Well

- All 4 stories delivered at 14/14 points — velocity target met
- US-040 added 8 mock-patched AppTest tests for `_render_step2`, lifting Step 2 coverage from 0 % to fully covered without needing a live database
- US-041 codified six AppTest quirks discovered during Sprint 8 + Sprint 9 (chaining ban, SafeSessionState `.get`/`.pop` bans, `default_timeout=10`, widget-tree instability, mock-at-import-source path) into a developer-guide quick-reference table — future UI tests will cost a fraction of the original investigation time
- US-042 introduced a `testcontainers[mysql]` Docker fixture with **graceful skip** semantics — tests skip cleanly on hosts without Docker (4 skipped on this run) instead of failing, so CI without Docker stays green while Docker-enabled CI gets full coverage
- US-043 PostgreSQL evaluation produced a 13-pt Go decision with concrete story breakdown (US-A..US-F), driver justification (`psycopg[binary]>=3.2` over `psycopg2-binary`), and risk mitigation table — Sprint 10 can start immediately with no further analysis
- BUG-006 (WSL2 localhost MongoDB timeout) was fixed mid-sprint by the Bug Fix Agent using Strategy E (WSL2-aware fail-fast) after Strategy A (`directConnection=True`) was correctly rejected because it would have broken the BUG-005 invariant test — the multi-strategy pattern paid off
- BUG-001 (coverage-below-gate, stale "Open" since Sprint 1) was discovered during Phase 12 audit and corrected to ✅ Fixed — backlog hygiene improved
- Coverage rose 93.84 % → 93.97 % (+0.13 pp); 144 tests green, 4 Docker-skipped (expected)
- Pipeline ran end-to-end through all 12 phases without manual intervention — first session to do so

## What Could Be Improved

- `src/services/db_connector.py` still at 79 % when Docker is unavailable — coverage gap only closes when CI has Docker; worth adding a `coverage-docker` job to the matrix
- `ruff` and `mypy` are listed as project standards but were not installed in the active venv during the pipeline run — CR-009 had to fall back to manual review for lint/type checks; should be enforced via `.pre-commit-config.yaml` or a `make check` target
- The Step 2 AppTest fake-schema needed to be `{}` (empty dict) because `SchemaViewerComponent` iterates columns expecting `.name` attributes — this contract is not documented; the component should accept an empty schema or the test pattern should be documented
- Sprint 9 capacity (14 pts) was a recovery sprint after Sprint 8 (11 pts) — still under the 16-pt average from Sprints 4–6; could pull a small story from the bug backlog if velocity holds
- `docs/architecture/postgresql-epic-evaluation.md` §5 deferred EPIC-009 file creation to "Sprint 10 first phase" — convenient for Sprint 9 close-out but it leaves one DoD checkbox intentionally unchecked in US-043, which makes auto-audits noisy

## Action Items

| Action                                                                                           | Owner                           | Due                |
| ------------------------------------------------------------------------------------------------ | ------------------------------- | ------------------ |
| Create `docs/epics/EPIC-009-postgresql-support.md` from US-043 evaluation §3 story breakdown     | Epic Writer                     | Sprint 10 day 1    |
| Promote US-A..US-F into formal user stories under `docs/user-stories/sprint-10/`                 | User Story Writer               | Sprint 10 day 1    |
| Add a `coverage-docker` job to `.github/workflows/ci-cd.yml` running `pytest -m docker`          | DevOps                          | Sprint 10 planning |
| Add `.pre-commit-config.yaml` with ruff + mypy hooks; document `pip install -e .[dev]` workflow  | Developer / DevOps              | Sprint 10 planning |
| Make `SchemaViewerComponent` tolerate empty / dict-shaped schemas, or document the contract      | Developer                       | Sprint 10 backlog  |
| Tick the deferred US-043 EPIC-009 DoD box once `docs/epics/EPIC-009-postgresql-support.md` lands | Developer (Sprint 10 reconcile) | Sprint 10 day 1    |

---

## Cumulative Velocity

| Sprint   | Committed | Delivered | Cumulative |
| -------- | --------- | --------- | ---------- |
| Sprint 1 | 21        | 21        | 21         |
| Sprint 2 | 21        | 21        | 42         |
| Sprint 3 | 13        | 13        | 55         |
| Sprint 4 | 16        | 16        | 71         |
| Sprint 5 | 16        | 16        | 87         |
| Sprint 6 | 28        | 28        | 115        |
| Sprint 7 | 15        | 15        | 130        |
| Sprint 8 | 11        | 11        | 141        |
| Sprint 9 | 14        | 14        | 155        |

**Total delivered**: 155 story points across 43 stories in 9 sprints
**Bugs closed in Sprint 9**: BUG-006 (WSL2 fail-fast) + BUG-001 (stale-status correction) = 2
