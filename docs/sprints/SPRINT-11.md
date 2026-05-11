# SPRINT-11 — Refactor & Hardening

**Theme**: Address Sprint 10 retro action items — extract shared WSL2 helper, refactor relational sidebar, lift PostgreSQL unit-coverage, ship CI Docker matrix and packaging cleanup.
**Dates**: Sprint 11 (post-Sprint-10 close)
**Capacity**: 14 pts (matches Sprint 10 velocity; cumulative target 182 pts)
**Source**: Seeded by Retro Analyzer from `docs/sprints/SPRINT-10-retro.md` action items.

---

## Sprint Goal

Pay down Sprint 10 technical debt without adding new user-facing features:
1. Eliminate WSL2 fail-fast duplication between `mongo_connector.py` and `db_connector.py`.
2. Reduce `sidebar.py` duplication via a shared mixin for relational engines.
3. Make the PostgreSQL Step 1 admin-DB **configurable** so managed services without the `postgres` database can connect.
4. Close coverage gap on `db_connector.py` (currently 80 %) without requiring Docker.
5. Ship the long-overdue `coverage-docker` CI matrix job.
6. Align `pyproject.toml` optional-dependency groups with `requirements.txt`.
7. Pre-validate sslmode `verify-*` selections in the sidebar.

---

## Committed Stories

| Story  | Title                                                             | Points | Owner     |
| ------ | ----------------------------------------------------------------- | ------ | --------- |
| US-050 | Extract WSL2 fail-fast helper to `src/utils/network.py`           | 2      | Developer |
| US-051 | Refactor sidebar — `RelationalConnectorSidebar` mixin             | 3      | Developer |
| US-052 | Configurable PostgreSQL Step 1 admin database                     | 2      | Developer |
| US-053 | `coverage-docker` GitHub Actions matrix job                       | 2      | DevOps    |
| US-054 | `pyproject.toml` optional-dependency groups                       | 1      | DevOps    |
| US-055 | Unit-mock coverage lift for `db_connector.py` PostgreSQL branches | 2      | Developer |
| US-056 | Sidebar sslmode `verify-*` pre-validation against CA bundle       | 2      | Developer |

**Total committed**: 14 pts

## Backlog (not committed)

- Multi-schema PostgreSQL support (`pg_namespace` enumeration) — kept in roadmap Future Backlog
- AWS RDS IAM auth for PostgreSQL — kept in roadmap Future Backlog

---

## Definition of Done (sprint-level)

- All 7 stories ✅ Done with DoD ticked
- 165 + 6+ tests passing (zero regression on existing 165)
- Coverage ≥ 94 % maintained; `db_connector.py` ≥ 90 %
- `ruff` + `mypy` clean (or documented gap)
- CR-011 approved
- TR-011 + ITR-003 captured
- Documentation updated (developer-guide, README if packaging changes)
- SPRINT-11-retro.md authored
