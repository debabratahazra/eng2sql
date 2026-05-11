# Sprint 10 Retrospective

**Sprint**: Sprint 10 — PostgreSQL Live Connection Support (EPIC-009)
**Date**: 2026-05-08
**Facilitator**: Scrum Master

---

## What Went Well

- All 6 stories delivered at 13/13 points — velocity target met on the first attempt; cumulative velocity rose to **168 pts** across 49 stories in 10 sprints
- Dialect-aware `DBConfig` refactor (US-044) used a `_DRIVER_SCHEMES` lookup + `__post_init__` validation that auto-normalises legacy long-form `dialect="mysql+pymysql"` to `"mysql"` — **zero existing-test breakage** when 144 Sprint-9 tests re-ran after the rewrite
- `_LIST_DB_QUERIES` dict (US-046) gave us a clean dialect-dispatch pattern in `DBConnector.list_databases` that extends to future engines (Oracle, MSSQL) by adding one line each
- The PostgreSQL system-prompt tip block (US-047) is a single dict entry (`_DIALECT_TIPS["PostgreSQL"]`) — adding more dialects costs one literal each; `sql_generator.py` coverage stayed at **100 %**
- The PostgreSQL sidebar branch (US-045) mirrored the MySQL flow exactly, including the `_pg_password` clear-after-Step-2 invariant from US-039 — security model carried forward without rework
- US-048 `postgres_container` fixture re-used the **two-level skip pattern** from `mysql_container` (ImportError → skip; DockerException → skip) and registered the same `[integration, docker]` markers — fixture contract is now a documented house style; CI without Docker stays green (8 tests skipped cleanly)
- US-049 documentation pass updated user-guide, developer-guide, and README with PostgreSQL walkthrough, dialect dispatch design, sslmode whitelist rationale, and `psycopg3` driver justification — no stale screenshots, no broken links
- Test count grew **144 → 165 (+21 PostgreSQL-specific)**; coverage rose **93.97 % → 94.48 %** (+0.51 pp); zero regressions across MySQL and MongoDB suites
- Sprint executed end-to-end through all 12 phases in a single pipeline invocation with no manual intervention — second consecutive sprint to do so

## What Could Be Improved

- The WSL2 fail-fast helper currently lives **inline in `mongo_connector.py`** (`_LOOPBACK_HOSTS`, `_is_wsl2()`, `_probe_reachable_host()`) — Sprint 10 explicitly punted on extracting it to `src/utils/network.py` for re-use by `db_connector.py`; PostgreSQL therefore inherits no WSL2 protection and could regress BUG-006 against a local Postgres container
- `src/components/sidebar.py` is now **~600 LoC** with three near-parallel render flows (MySQL / PostgreSQL / MongoDB) — duplication is becoming costly; a small `RelationalConnectorSidebar` mixin or template-method refactor would cut ~150 LoC and one-place future engines
- `database="postgres"` is **hard-coded as the Step 1 admin DB** in the sidebar — works for stock PostgreSQL but breaks against managed services that disable the `postgres` database (Azure Single Server, some hardened RDS images); should fall back to user's role default DB
- The `postgres_container` and `mysql_container` fixtures still **never run live in CI** (Docker not installed on the GitHub Actions runner) — the Sprint 9 `coverage-docker` matrix-job action item from DevOps was carried forward into Sprint 10 backlog and is **still not done**, so 8 of 173 tests skip on every CI run
- `pyproject.toml` has no `[project.optional-dependencies]` group for `psycopg[binary]` / `testcontainers[postgres]` — the new deps are only declared in `requirements.txt`, so `pip install -e .[dev]` does not pull them; needs alignment with the standardised packaging pattern
- US-045 PostgreSQL form does **not validate sslmode against installed CA bundle** when `verify-ca`/`verify-full` is selected — error only surfaces at connect time; could be caught earlier by a sidebar pre-check
- Coverage on `db_connector.py` slipped from **93 % → 80 %** because the new PostgreSQL branches (engine creation, list-databases dispatch, dialect filter) are only exercised by Docker-skipped integration tests — needs unit-level mocks even where Docker tests already cover the same paths

## Action Items

| Action                                                                                                                                    | Owner                           | Due                |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ------------------ |
| Extract WSL2 fail-fast helper to `src/utils/network.py`; refactor `mongo_connector.py` and `db_connector.py` to share it                  | Developer                       | Sprint 11 day 1    |
| Refactor `sidebar.py`: extract a `RelationalConnectorSidebar` mixin shared by MySQL + PostgreSQL flows; reduce duplication                | Developer                       | Sprint 11 planning |
| Make Step 1 admin DB **configurable** (sidebar text input, default `postgres`) so managed PostgreSQL services without it can connect      | Developer                       | Sprint 11 planning |
| **Carry-over from Sprint 9**: add `coverage-docker` matrix job to `.github/workflows/ci-cd.yml` running `pytest -m docker`                | DevOps                          | Sprint 11 day 1    |
| Add `[project.optional-dependencies] db = ["psycopg[binary]>=3.2,<4"]` and `dev` group to `pyproject.toml`; align with `requirements.txt` | DevOps                          | Sprint 11 planning |
| Add unit-level mocks for the PostgreSQL `create_engine` happy-path in `db_connector.py` to lift coverage 80 % → ≥ 90 % without Docker     | Tester / Developer              | Sprint 11 backlog  |
| Pre-validate sslmode `verify-*` selections against installed CA bundle in the sidebar before calling `create_engine`                      | Developer                       | Sprint 11 backlog  |
| Tick the Sprint 9 deferred-action carry-overs (`coverage-docker`, `pre-commit-config`) once delivered                                     | Developer (Sprint 11 reconcile) | Sprint 11 day 1    |

---

## Cumulative Velocity

| Sprint    | Committed | Delivered | Cumulative |
| --------- | --------- | --------- | ---------- |
| Sprint 1  | 21        | 21        | 21         |
| Sprint 2  | 21        | 21        | 42         |
| Sprint 3  | 13        | 13        | 55         |
| Sprint 4  | 16        | 16        | 71         |
| Sprint 5  | 16        | 16        | 87         |
| Sprint 6  | 28        | 28        | 115        |
| Sprint 7  | 15        | 15        | 130        |
| Sprint 8  | 11        | 11        | 141        |
| Sprint 9  | 14        | 14        | 155        |
| Sprint 10 | 13        | 13        | **168**    |

**Total delivered**: 168 story points across 49 stories in 10 sprints
**Bugs closed in Sprint 10**: 0 (no bugs filed during the sprint; all open bugs already ✅ Fixed entering the sprint)
**New tests added**: 21 (165 total; coverage 94.48 %)
**Sprints with zero pre-existing-test breakage from a refactor**: 10/10

---

## Carry-Over Backlog Snapshot

The following items were captured here and are now visible in `docs/roadmap.md` Future Backlog. Retro Analyzer will pick them up in Phase 0 of the next pipeline run and convert them into Sprint 11 user stories where appropriate.

1. WSL2 helper extraction → `src/utils/network.py`
2. Sidebar refactor → `RelationalConnectorSidebar` mixin
3. Configurable PostgreSQL admin DB
4. `coverage-docker` CI matrix job
5. `pyproject.toml` optional-dependencies grouping
6. PostgreSQL `db_connector.py` unit-mock coverage lift
7. Sidebar sslmode `verify-*` pre-validation
