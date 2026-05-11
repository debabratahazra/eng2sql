# PostgreSQL Live Connection — Epic Evaluation (US-043)

**Sprint**: Sprint 9
**Author**: Pipeline (Scrum Master role)
**Date**: 2026-05-07
**Decision target**: Schedule **EPIC-009 — PostgreSQL Live Connection** for Sprint 10?
**Recommendation**: **✅ GO** — small, well-scoped epic (~13 pts), majority of code already
generic via SQLAlchemy.

---

## 1. Scope of Evaluation

Assess what changes are required to add live PostgreSQL connection support to Eng2SQL,
mirroring the existing MySQL flow (Step 1 connect → list databases → Step 2 select →
detect schema → run generated SQL).

Out of scope for this evaluation:
- AWS RDS PostgreSQL specifics (IAM auth) — separate epic if needed.
- PostgreSQL-specific dialect features in the LLM prompt (defer to Sprint 11+).

---

## 2. Codebase Audit

| File                                                                     | Generic today?                                                 | PostgreSQL changes needed                                                                                                                                                                        |
| ------------------------------------------------------------------------ | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [src/services/db_connector.py](../../src/services/db_connector.py)       | ✅ Mostly — uses SQLAlchemy `create_engine`, `text("SELECT 1")` | Update `_SYSTEM_DATABASES` to also exclude `postgres`, `template0`, `template1`. `list_databases` must switch query to `SELECT datname FROM pg_database` (currently relies on `SHOW DATABASES`). |
| [src/services/schema_detector.py](../../src/services/schema_detector.py) | ✅ Fully generic — uses SQLAlchemy `inspect()`                  | None. SQLAlchemy `inspect()` supports PostgreSQL out of the box.                                                                                                                                 |
| [src/services/sql_generator.py](../../src/services/sql_generator.py)     | ⚠️ Prompt currently says "MySQL"                                | Pass dialect name into prompt template (e.g. "PostgreSQL 16").                                                                                                                                   |
| `src/models/config.py` (`DBConfig`)                                      | ❌ Hardcodes `mysql+pymysql://` URL scheme                      | Add `dialect: Literal["mysql", "postgresql"]` field; pick driver scheme accordingly.                                                                                                             |
| [src/components/sidebar.py](../../src/components/sidebar.py)             | ❌ Step 1 form is MySQL-specific                                | Add `PostgreSQL` to the DB-type radio (currently `["MySQL", "MongoDB"]`); reuse fields (host/port/user/password) but default port to 5432; add `sslmode` selectbox.                              |
| `src/app.py`                                                             | ✅ Wiring is generic                                            | None.                                                                                                                                                                                            |
| [config/database_config.yaml](../../config/database_config.yaml)         | ✅ Static schema only                                           | Optional: add a PostgreSQL example section.                                                                                                                                                      |

### Driver choice — `psycopg2-binary` vs `psycopg[binary]` (psycopg3)

| Aspect                             | `psycopg2-binary` 2.9  | `psycopg[binary]` 3.2      |
| ---------------------------------- | ---------------------- | -------------------------- |
| Maturity                           | Stable since 2010      | GA since 2021              |
| SQLAlchemy 2.x default             | ⚠️ Supported but legacy | ✅ Recommended for new code |
| Async support                      | ❌                      | ✅                          |
| Wheel availability (win/linux/mac) | ✅                      | ✅                          |
| Streaming `COPY` (future)          | ⚠️ Awkward              | ✅ Native                   |
| Maintenance                        | Bug-fix only           | Active                     |

**Choice**: `psycopg[binary]>=3.2` — Streamlit's threaded environment benefits from
psycopg3's better thread safety, and the dependency footprint is the same.

### `sslmode` differences vs MySQL `ssl=false`

PostgreSQL exposes `sslmode={disable|allow|prefer|require|verify-ca|verify-full}`
as a query parameter on the connection URL. The default is `prefer`. For
self-signed local MySQL the existing app uses `?ssl=false`; the equivalent for
PostgreSQL is `?sslmode=disable`. UI exposes this as a selectbox in Step 1.

---

## 3. Effort Estimate (story-level)

| US ID     | Title                                                                | Points | Notes                                                     |
| --------- | -------------------------------------------------------------------- | -----: | --------------------------------------------------------- |
| US-A      | Add `psycopg[binary]` to requirements + dialect-aware `DBConfig`     |      2 | Trivial code change + URL builder unit tests              |
| US-B      | Sidebar: PostgreSQL connect form + sslmode selector                  |      3 | Mirrors MySQL form; shares 80% code                       |
| US-C      | `DBConnector.list_databases` dialect dispatch                        |      2 | One `if dialect == 'postgresql'` branch                   |
| US-D      | Pass dialect name into LLM prompt                                    |      1 | Single string substitution                                |
| US-E      | Integration tests against real PostgreSQL container (testcontainers) |      3 | Reuses US-042 pattern                                     |
| US-F      | Documentation updates (user-guide, developer-guide, README)          |      2 | Standard sprint docs work                                 |
| **Total** |                                                                      | **13** | Comfortably fits a single sprint (sprint capacity 14 pts) |

---

## 4. Risks

| #   | Risk                                                                               | Likelihood | Impact | Mitigation                                                                       |
| --- | ---------------------------------------------------------------------------------- | ---------: | -----: | -------------------------------------------------------------------------------- |
| R1  | psycopg3 wheel missing for Python 3.14 on some OSs                                 |        Low |    Med | Pin `psycopg[binary]>=3.2,<4`; CI tests across 3.11–3.14                         |
| R2  | LLM generates MySQL-specific syntax (`LIMIT … OFFSET …` ok, but `LIMIT 10, 5` not) |        Med |    Low | Pass dialect name in prompt; add 2 LLM eval tests per dialect                    |
| R3  | SQLAlchemy `inspect()` PostgreSQL types differ subtly (e.g. `JSONB` not `JSON`)    |        Med |    Low | `SchemaColumn.type` is already a free-text string; type-mapping cosmetic only    |
| R4  | `pg_hba.conf` connection refusals on Windows hosts (similar to BUG-006 WSL2 case)  |        Low |    Med | Reuse the BUG-006 WSL2 fail-fast pattern in `db_connector.py` for PostgreSQL too |

No blocker risks identified.

---

## 5. Go / No-Go Recommendation

### ✅ GO — schedule EPIC-009 for Sprint 10

**Rationale**:
1. SQLAlchemy + the existing schema-detector design make PostgreSQL a near-drop-in addition.
2. Effort fits in one sprint at 13 pts (capacity 14).
3. No blocker risks; mitigations are standard patterns the team already applies.
4. Strategic value: PostgreSQL is the most-requested DB in our user survey (Sprint 7 retro action items).
5. Pipes naturally into a future "Multi-dialect SQL generation" epic.

### EPIC-009 placeholder

A draft **EPIC-009** has **not** been created in this evaluation iteration —
the user stories US-A through US-F above will be promoted to epic + story
files by the Epic Writer / User Story Writer in the **first phase of Sprint 10**
(after the Scrum Master commits the sprint based on this Go decision).

This keeps the backlog clean and avoids speculative epic files for work not yet
formally committed.

---

## 6. Roadmap Update

A line item is appended to `docs/roadmap.md` under "Future Backlog" pointing at
this evaluation file. Sprint 10 planning will pick up EPIC-009 from this entry.
