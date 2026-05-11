# EPIC-009: PostgreSQL Live Connection Support

## Goal

Extend the Streamlit sidebar to support **PostgreSQL** as a third live-database engine
alongside MySQL and MongoDB. Mirror the existing two-step MySQL flow (server connect →
list databases → select database → detect schema → generate dialect-aware SQL) so that
existing users have zero new concepts to learn while the application opens up to the
largest open-source RDBMS userbase.

---

## Business Value

- PostgreSQL is the most-requested database in the Sprint 7 retro user survey; closing
  this gap removes the #1 onboarding blocker for new teams.
- Demonstrates the engine-agnostic design of the SQLAlchemy + dialect-aware prompt
  pipeline introduced in EPIC-006/EPIC-007 — proves the abstraction.
- Establishes the multi-dialect SQL generation pattern that future epics (MSSQL, Oracle,
  Snowflake) will plug into with minimal code changes.
- Unlocks AWS RDS PostgreSQL, Azure Database for PostgreSQL, and Cloud SQL users with no
  cloud-specific code.

---

## Scope

### In Scope

- **DB-type radio selector** updated in `src/components/sidebar.py`:
  - Options: `MySQL` | `PostgreSQL` | `MongoDB` (PostgreSQL inserted between MySQL and
    MongoDB to keep relational engines grouped).
  - Selecting PostgreSQL clears all downstream session-state keys and renders the new
    PostgreSQL form.

- **PostgreSQL form** (new):
  - Fields: Host (default `localhost`), Port (default `5432`), User, Password,
    `sslmode` selectbox (`disable` | `allow` | `prefer` | `require` | `verify-ca` |
    `verify-full`, default `prefer`).
  - **Connect** button: connects to the PostgreSQL server (no specific database;
    SQLAlchemy connects to the default `postgres` maintenance DB), then calls
    `DBConnector.list_databases(engine)` which dispatches to a PostgreSQL-specific
    `SELECT datname FROM pg_database WHERE datistemplate = false` query.
  - Step 2: dropdown listing user databases (system DBs `postgres`, `template0`,
    `template1` filtered out by default) → **Select Database** button finalises the
    engine and detects schema via the existing `SchemaDetector` (SQLAlchemy
    `inspect()` already supports PostgreSQL out of the box).

- **`DBConfig` updates** in `src/models/config.py`:
  - Add `dialect: Literal["mysql", "postgresql"]` field (default `"mysql"` for backward
    compatibility).
  - URL builder picks driver scheme based on dialect:
    - `mysql` → `mysql+pymysql://…?ssl=false` (existing)
    - `postgresql` → `postgresql+psycopg://…?sslmode={sslmode}` (new)
  - Add `sslmode` field used only for `postgresql` dialect.

- **`DBConnector` updates** in `src/services/db_connector.py`:
  - `list_databases(engine)` dispatches on `engine.dialect.name`:
    - `mysql` → existing `SHOW DATABASES` query.
    - `postgresql` → `SELECT datname FROM pg_database WHERE datistemplate = false`.
  - `_SYSTEM_DATABASES` extended to include `postgres`, `template0`, `template1`.
  - Reuse the BUG-006 WSL2 fail-fast pattern in `create_engine` for PostgreSQL TCP
    probes too.

- **`SQLGenerator` updates** in `src/services/sql_generator.py`:
  - Accept `dialect: str` parameter (already supports `"MySQL"` / `"MongoDB"`); add
    `"PostgreSQL"` branch.
  - Inject dialect name into the LLM prompt so the model emits PostgreSQL-specific
    syntax (e.g. `LIMIT … OFFSET …`, `RETURNING`, `ILIKE`, `::` casts).

- **App wiring updates** in `src/app.py`:
  - Read `db_type` to choose between MySQL/PostgreSQL/MongoDB code paths (already
    structured for this from EPIC-007).
  - Pass dialect name through to `SQLGenerator`.

- **Driver dependency**:
  - Add `psycopg[binary]>=3.2,<4` to `requirements.txt`.
  - Choice rationale documented in
    [docs/architecture/postgresql-epic-evaluation.md](../architecture/postgresql-epic-evaluation.md)
    §2: psycopg3 chosen over `psycopg2-binary` for SQLAlchemy 2.x default support,
    better thread safety for Streamlit's threaded environment, and active maintenance.

- **Integration tests** (mirroring US-042 pattern):
  - `testcontainers[postgres]>=4.7` added to dev dependencies.
  - `postgres_container` session-scoped fixture in `tests/conftest.py` with the same
    graceful Docker-skip semantics as `mysql_container`.
  - 4+ live PostgreSQL tests in `tests/integration/test_db_connector_postgres_live.py`
    covering connect, list_databases, execute_query, invalid credentials.

- **Documentation**:
  - Update `docs/guides/user-guide.md` — add PostgreSQL connection walkthrough.
  - Update `docs/guides/developer-guide.md` — document dialect dispatch, sslmode field,
    psycopg3 driver choice.
  - Update `README.md` — list `psycopg[binary]` and `testcontainers[postgres]` as new
    deps and add PostgreSQL example.

### Out of Scope

- AWS RDS IAM authentication for PostgreSQL — separate epic if needed.
- Azure AD / Google IAM authentication.
- PostgreSQL `LISTEN/NOTIFY`, advisory locks, or other vendor-specific runtime features.
- Schema-level filtering (`pg_namespace` / multiple schemas per database) — Sprint 10
  treats `public` as the only schema; multi-schema support deferred.
- PgBouncer / connection-pooler-specific tuning.
- Saving / recalling PostgreSQL connection profiles.
- MSSQL, Oracle, Snowflake, Redis, or other engines.
- Modifying the existing MySQL or MongoDB code paths beyond the dialect-dispatch
  refactor required to slot PostgreSQL in.

---

## User Stories

| US ID     | Title                                                         | Points |
| --------- | ------------------------------------------------------------- | -----: |
| US-044    | Add `psycopg[binary]` dependency and dialect-aware `DBConfig` |      2 |
| US-045    | Sidebar: PostgreSQL connect form with sslmode selector        |      3 |
| US-046    | `DBConnector.list_databases` dialect dispatch for PostgreSQL  |      2 |
| US-047    | Pass dialect name into LLM prompt for PostgreSQL              |      1 |
| US-048    | PostgreSQL integration tests with testcontainers fixture      |      3 |
| US-049    | Documentation updates for PostgreSQL support                  |      2 |
| **Total** |                                                               | **13** |

Sprint capacity 14 pts → fits with 1 pt buffer.

---

## Acceptance Criteria

- [ ] User can pick `PostgreSQL` from the sidebar radio
- [ ] Step 1 form shows host/port/user/password/sslmode fields with PostgreSQL defaults
- [ ] Step 1 Connect successfully lists user databases (excluding `postgres`,
      `template0`, `template1`)
- [ ] Step 2 Select Database successfully detects schema via SQLAlchemy `inspect()`
- [ ] Generated SQL uses PostgreSQL syntax (e.g. `ILIKE`, `::` casts, `LIMIT`/`OFFSET`)
- [ ] All integration tests pass on a host with Docker; skip cleanly without Docker
- [ ] Coverage remains ≥ 80 % (target ≥ 93 % to match Sprint 9 baseline)
- [ ] No regression in existing MySQL or MongoDB code paths
- [ ] BUG-006-style WSL2 fail-fast works for PostgreSQL `localhost` connections
- [ ] All Sprint 10 user stories US-044..US-049 marked ✅ Done

---

## Definition of Done

- [ ] All 6 user stories delivered and marked ✅ Done
- [ ] Code review CR-010 ✅ Approved
- [ ] Test cases TC-045..TC-050 written
- [ ] Test results TR-010 — coverage ≥ 80 %, all tests passing
- [ ] Integration test report ITR-002 — PostgreSQL fixture verified
- [ ] User-guide / developer-guide / README updated
- [ ] No open bugs introduced by EPIC-009
- [ ] Sprint 10 retrospective authored

---

## Linked Documents

- Evaluation: [docs/architecture/postgresql-epic-evaluation.md](../architecture/postgresql-epic-evaluation.md)
- Sprint plan: [docs/sprints/SPRINT-10.md](../sprints/SPRINT-10.md)
- Roadmap: [docs/roadmap.md](../roadmap.md)

---

## Status

🔄 **In Progress** — Sprint 10 (planned 2026-05-08 → 2026-05-21)
