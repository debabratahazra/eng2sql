# Sprint 10 Plan

**Goal**: Deliver EPIC-009 — PostgreSQL live connection support — extending the sidebar with a third database engine alongside MySQL and MongoDB. Mirror the existing two-step connect→list→select→detect→generate flow with PostgreSQL-specific dialect dispatch, sslmode selector, psycopg3 driver, and Docker-backed integration tests.
**Duration**: 2026-05-08 → 2026-05-21 (2 weeks)
**Velocity Target**: 13 points (capacity 14, 1 pt buffer)
**Source**: Auto-generated from SPRINT-9-retro.md action items + US-043 PostgreSQL evaluation Go decision by Retro Analyzer / Scrum Master (2026-05-07)

---

## Committed Stories

| Story ID | Title                                                         | Points | Assignee (Agent) |
| -------- | ------------------------------------------------------------- | ------ | ---------------- |
| US-044   | Add `psycopg[binary]` dependency and dialect-aware `DBConfig` | 2      | Developer        |
| US-045   | Sidebar: PostgreSQL connect form with sslmode selector        | 3      | Developer        |
| US-046   | `DBConnector.list_databases` dialect dispatch for PostgreSQL  | 2      | Developer        |
| US-047   | Pass dialect name into LLM prompt for PostgreSQL              | 1      | Developer        |
| US-048   | PostgreSQL integration tests with testcontainers fixture      | 3      | Developer        |
| US-049   | Documentation updates for PostgreSQL support                  | 2      | Developer        |

**Total committed**: 13 points

---

## Backlog (Not Committed This Sprint)

| Item                                           | Title                                                                    | Type        | Severity | Notes                                                              |
| ---------------------------------------------- | ------------------------------------------------------------------------ | ----------- | -------- | ------------------------------------------------------------------ |
| Action — `coverage-docker` CI job              | Add CI matrix job running `pytest -m docker`                             | Improvement | Medium   | DevOps work; pulled if velocity allows                             |
| Action — `.pre-commit-config.yaml` ruff + mypy | Enforce lint/type via pre-commit hooks                                   | Improvement | Medium   | Closes Sprint 9 retro gap (CR-009 fell back to manual lint review) |
| Action — `SchemaViewerComponent` empty-schema  | Tolerate empty / dict schemas in viewer to remove the AppTest workaround | Improvement | Low      | Discovered during US-040 Sprint 9                                  |
| Future epic                                    | Multi-schema support for PostgreSQL (`pg_namespace`)                     | Epic        | —        | Deferred from EPIC-009 scope; queue for Sprint 11+                 |
| Future epic                                    | AWS RDS IAM authentication                                               | Epic        | —        | Out of scope per EPIC-009                                          |

---

## Carried-Over Context

| Source Retro      | Original Item                                                                               | Action Taken                      |
| ----------------- | ------------------------------------------------------------------------------------------- | --------------------------------- |
| SPRINT-9-retro    | Create `docs/epics/EPIC-009-postgresql-support.md` from US-043 evaluation §3                | ✅ Done — EPIC-009 drafted         |
| SPRINT-9-retro    | Promote US-A..US-F into formal user stories under `docs/user-stories/sprint-10/`            | ✅ Done — US-044..US-049           |
| SPRINT-9-retro    | Add `coverage-docker` job to CI                                                             | → Backlog (not committed)         |
| SPRINT-9-retro    | Add `.pre-commit-config.yaml` with ruff + mypy hooks                                        | → Backlog (not committed)         |
| SPRINT-9-retro    | `SchemaViewerComponent` empty-schema tolerance                                              | → Backlog (not committed)         |
| SPRINT-9-retro    | Tick deferred US-043 EPIC-009 DoD box once epic file lands                                  | → Reconcile on Sprint 10 day 1    |
| US-043 evaluation | Driver choice `psycopg[binary]>=3.2`, sslmode selector, US-A..US-F story breakdown (13 pts) | → Adopted into EPIC-009/Sprint 10 |

---

## Definition of Done

- [ ] Code implemented and committed for all 6 stories
- [ ] Code review CR-010 ✅ Approved
- [ ] Unit tests written and passing (≥ 80 % coverage gate; target ≥ 94 %)
- [ ] Integration tests passing on Docker-enabled hosts; skip cleanly without Docker
- [ ] `docs/guides/user-guide.md`, `docs/guides/developer-guide.md`, `README.md` updated
- [ ] No critical bugs open
- [ ] Sprint 10 retrospective authored
- [ ] EPIC-009 marked ✅ Done in `PROJECT_PROGRESS.md`

---

## Sprint Risks

| Risk                                                                                  | Likelihood | Impact | Mitigation                                                                        |
| ------------------------------------------------------------------------------------- | ---------- | ------ | --------------------------------------------------------------------------------- |
| `psycopg[binary]>=3.2` wheel missing for Python 3.14 on some OSs                      | Low        | Medium | Pin `psycopg[binary]>=3.2,<4`; CI tests across 3.11–3.14                          |
| LLM emits MySQL-specific syntax for PostgreSQL prompts                                | Medium     | Low    | Inject dialect into prompt; add 2 LLM eval tests in US-047                        |
| `SchemaDetector` (SQLAlchemy `inspect()`) returns PostgreSQL-specific types (`JSONB`) | Medium     | Low    | `SchemaColumn.type` is a free-text string; type mapping is cosmetic               |
| `pg_hba.conf` connection refusals on Windows hosts (mirrors BUG-006)                  | Low        | Medium | Reuse BUG-006 WSL2 fail-fast pattern in `db_connector.create_engine`              |
| Docker not available in CI for US-048                                                 | Medium     | Medium | Reuse US-042 graceful-skip pattern; tests skip cleanly without Docker             |
| Adding PostgreSQL to radio breaks existing MySQL/MongoDB AppTest fixtures             | Low        | Medium | Run full Sprint 8/9 AppTest suite (`tests/unit/test_sidebar*.py`) before PR merge |

---

## Session State Changes

### New session state keys (US-045)

- `pg_host` — PostgreSQL server host (default `localhost`)
- `pg_port` — PostgreSQL server port (default `5432`)
- `pg_user` — PostgreSQL username
- `_pg_password` — PostgreSQL password (popped after use, mirrors MySQL `_db_password`)
- `pg_sslmode` — `disable`/`allow`/`prefer`/`require`/`verify-ca`/`verify-full`
- `pg_server_engine` — Step-1 SQLAlchemy engine bound to default `postgres` database
- `pg_available_databases` — `list[str]` from PostgreSQL discovery
- `pg_selected_database` — chosen database name (Step 2)

### Updated keys

- `db_type` — radio now accepts `"PostgreSQL"` in addition to `"MySQL"` / `"MongoDB"`

---

## Test Coverage Targets

| Module                          | Sprint 9 baseline     | Sprint 10 target                                    |
| ------------------------------- | --------------------- | --------------------------------------------------- |
| `src/services/db_connector.py`  | 79 % (94 % w/ Docker) | ≥ 85 % unit-only; ≥ 95 % with Docker (US-048)       |
| `src/models/config.py`          | 95 %                  | ≥ 95 % (new dialect field branches must be covered) |
| `src/services/sql_generator.py` | 100 %                 | 100 % (US-047 new dialect branch)                   |
| `src/components/sidebar.py`     | excluded              | New PostgreSQL flow tested via mock-patched AppTest |
| Overall                         | 93.97 %               | ≥ 94 %                                              |

---

## Linked Documents

- Epic: [docs/epics/EPIC-009-postgresql-support.md](../epics/EPIC-009-postgresql-support.md)
- Evaluation: [docs/architecture/postgresql-epic-evaluation.md](../architecture/postgresql-epic-evaluation.md)
- Sprint 9 retro: [docs/sprints/SPRINT-9-retro.md](SPRINT-9-retro.md)
- Roadmap: [docs/roadmap.md](../roadmap.md)
