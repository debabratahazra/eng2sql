# Eng2SQL — Project Roadmap

## Vision

**Eng2SQL** empowers non-technical users to query any MySQL database using plain English,
with a clean Streamlit interface that shows step-by-step progress and supports both
static schema definitions and live database auto-detection.

---

## Release Timeline

```
May 2026 (Sprints 1–12)
────────────────────────────────────────────────────────────────────────────────────
[S1]──[S2]──[S3]──[S4]──[S5]──[S6]──[S7]──[S8]──[S9]──[S10]──[S11]──[S12]
Found  UI    QA   Deploy LiveDB Mongo  URI  Harden CovDX  PgSQL  Refact   MQL
                  v1.0.0

May 2026 (Sprints 13–22)  ← all complete ✅
────────────────────────────────────────────────────────────────────────────────────
[S13]──[S14]──[S15]──[S16]──[S17]──[S18]──[S19]──[S20]──[S21]──[S22]
Sbar   Deps   CovUp  Refact CompCov  100%  Maint  History UXPol  Badge
```

---

## Sprint Plan

### Sprint 1 — Foundation (Weeks 1–2)
**Goal**: Working SQL generation with static schema, no UI yet

| Story                                         | Points | Status |
| --------------------------------------------- | ------ | ------ |
| US-001: Static Schema Configuration           | 3      | ✅      |
| US-002: OpenAI SQL Generation Service         | 5      | ✅      |
| US-003: Prompt Engineering for Schema Context | 3      | ✅      |
| US-004: Streamlit App Shell                   | 2      | ✅      |
| US-005: Query Input Component                 | 3      | ✅      |
| US-006: Step-by-Step Progress Display         | 3      | ✅      |
| US-007: SQL Output Panel                      | 2      | ✅      |

**Sprint 1 Total**: 21 points

---

### Sprint 2 — Dynamic Schema & Execution (Weeks 3–4)
**Goal**: Connect to live DB, auto-detect schema, execute SQL

| Story                                  | Points | Status |
| -------------------------------------- | ------ | ------ |
| US-008: Database Connection Form       | 5      | ✅      |
| US-009: Schema Auto-Detection          | 5      | ✅      |
| US-010: Schema Viewer Panel            | 3      | ✅      |
| US-011: SQL Execution & Results Table  | 5      | ✅      |
| US-012: Error Handling & User Feedback | 3      | ✅      |

**Sprint 2 Total**: 21 points

---

### Sprint 3 — Quality Assurance (Weeks 5–6)
**Goal**: ≥ 80% test coverage, linting clean, CI enforced

| Story                                    | Points | Status |
| ---------------------------------------- | ------ | ------ |
| US-013: Unit Tests — SQL Generator       | 3      | ✅      |
| US-014: Unit Tests — Schema Detector     | 3      | ✅      |
| US-015: Integration Tests — DB Connector | 5      | ✅      |
| US-016: Linting & Type Checking          | 2      | ✅      |

**Sprint 3 Total**: 13 points

---

### Sprint 4 — Deployment (Weeks 7–8)
**Goal**: Production-ready artefacts, CI/CD pipeline, release v1.0.0

| Story                                       | Points | Status |
| ------------------------------------------- | ------ | ------ |
| US-017: Dockerfile & Docker Compose         | 5      | ✅      |
| US-018: GitHub Actions CI/CD Pipeline       | 5      | ✅      |
| US-019: Deployment Runbook & Release Notes  | 3      | ✅      |
| US-020: Pre-commit Hooks & Dependency Audit | 3      | ✅      |

**Sprint 4 Total**: 16 points

---

### Sprint 5 — Live DB Database Selector (Weeks 9–10)
**Goal**: Two-step MySQL connection flow, database discovery dropdown, remove static schema mode

| Story                                                         | Points | Status |
| ------------------------------------------------------------- | ------ | ------ |
| US-021: Remove Static Schema Mode & MySQL-Only Sidebar        | 3      | ✅      |
| US-022: Step 1 — Server Connect & Database Discovery          | 5      | ✅      |
| US-023: Step 2 — Database Selector & Engine Activation        | 5      | ✅      |
| US-024: `DBConnector.list_databases()` Service Method & Tests | 3      | ✅      |

**Sprint 5 Total**: 16 points

---

### Sprint 6 — MongoDB Database Support (Weeks 11–12)
**Goal**: Add MongoDB as a second live-database engine — sidebar radio selector, two-step MongoDB connection flow, MongoDBConnector and MongoSchemaDetector services, MongoDB MQL dialect

| Story                                                 | Points | Status |
| ----------------------------------------------------- | ------ | ------ |
| US-025: MongoDB Connection Form in Sidebar            | 5      | ✅      |
| US-026: MongoDB Database Discovery & Selection        | 5      | ✅      |
| US-027: `MongoDBConnector` Service                    | 5      | ✅      |
| US-028: `MongoSchemaDetector` Service                 | 5      | ✅      |
| US-029: SQL Generator MongoDB Dialect                 | 3      | ✅      |
| US-030: Unit & Integration Tests for MongoDB Services | 5      | ✅      |

**Sprint 6 Total**: 28 points

---

### Sprint 7 — MongoDB URI Connection Input (Weeks 13–14)
**Goal**: Add URI + credentials input mode to the MongoDB sidebar — users can paste a full `mongodb://` or `mongodb+srv://` URI alongside separate credential fields

| Story                                                                             | Points | Status |
| --------------------------------------------------------------------------------- | ------ | ------ |
| US-031: Connection Input Mode Toggle in MongoDB Sidebar                           | 3      | ✅      |
| US-032: URI + Credentials Mode: URI Parsing & Credential Injection in MongoConfig | 5      | ✅      |
| US-033: URI Mode: `directConnection` Suppression for SRV URIs                     | 2      | ✅      |
| US-034: Unit Tests for URI Injection and Validation                               | 3      | ✅      |
| US-035: Documentation Updates for URI Connection Mode                             | 2      | ✅      |

**Sprint 7 Total**: 15 points

---

### Sprint 8 — Quality Hardening (Weeks 15–16)
**Goal**: AppTest UI test coverage, MongoConfig branch hardening, urllib import cleanup, password session-state security

| Story                                                                   | Points | Status |
| ----------------------------------------------------------------------- | ------ | ------ |
| US-036: Move `urllib.parse` Import to Module Level                      | 1      | ✅      |
| US-037: Increase `MongoConfig` Uncovered Branch Coverage                | 2      | ✅      |
| US-038: AppTest-Based Sidebar UI Tests (Mode Toggle & Connection Forms) | 5      | ✅      |
| US-039: Harden `_db_password` Session State Storage                     | 3      | ✅      |

**Sprint 8 Total**: 11 points

---

### Sprint 9 — Coverage & Developer Experience
**Goal**: Mock-patched AppTest tests for `_render_step2`, Docker-based MySQL integration fixture, AppTest quirks documentation, and PostgreSQL epic evaluation

| Story                                                                | Points | Status |
| -------------------------------------------------------------------- | ------ | ------ |
| US-040: Mock-Patched AppTest Tests for `_render_step2`               | 5      | ✅      |
| US-041: Document AppTest Quirks in Developer Guide                   | 2      | ✅      |
| US-042: Docker-Based MySQL Integration Fixture for `db_connector.py` | 5      | ✅      |
| US-043: Evaluate PostgreSQL Live Connection Epic for Sprint 10       | 2      | ✅      |

**Sprint 9 Total**: 14 points

---

### Sprint 10 — PostgreSQL Live Connection Support
**Goal**: Deliver EPIC-009 — extend the sidebar with PostgreSQL as a third database engine alongside MySQL and MongoDB

| Story                                                                 | Points | Status |
| --------------------------------------------------------------------- | ------ | ------ |
| US-044: Add `psycopg[binary]` dependency and dialect-aware `DBConfig` | 2      | ✅      |
| US-045: Sidebar: PostgreSQL connect form with sslmode selector        | 3      | ✅      |
| US-046: `DBConnector.list_databases` dialect dispatch for PostgreSQL  | 2      | ✅      |
| US-047: Pass dialect name into LLM prompt for PostgreSQL              | 1      | ✅      |
| US-048: PostgreSQL integration tests with testcontainers fixture      | 3      | ✅      |
| US-049: Documentation updates for PostgreSQL support                  | 2      | ✅      |

**Sprint 10 Total**: 13 points

---

### Sprint 11 — Refactor & Hardening
**Goal**: Extract shared WSL2 helper, configurable admin DB, CI Docker matrix, sslmode pre-validation, and coverage lift for PostgreSQL branches

| Story                                                                     | Points | Status |
| ------------------------------------------------------------------------- | ------ | ------ |
| US-050: Extract WSL2 fail-fast helper to `src/utils/network.py`           | 2      | ✅      |
| US-052: Configurable PostgreSQL Step 1 admin database                     | 2      | ✅      |
| US-053: `coverage-docker` GitHub Actions matrix job                       | 2      | ✅      |
| US-055: Unit-mock coverage lift for `db_connector.py` PostgreSQL branches | 2      | ✅      |
| US-056: Sidebar sslmode `verify-*` pre-validation against CA bundle       | 2      | ✅      |

> US-051 and US-054 deferred to Sprint 13.

**Sprint 11 Delivered**: 10 points (5 of 7 planned stories)

---

### Sprint 12 — MQL Query Execution
**Goal**: End-to-end MQL query execution from the Streamlit UI, eliminating the "not yet supported" placeholder

| Story                                                      | Points | Status |
| ---------------------------------------------------------- | ------ | ------ |
| US-057: Dynamic output label (SQL → MQL)                   | 3      | ✅      |
| US-058: MongoDB system prompt — structured JSON MQL output | 3      | ✅      |
| US-059: `MongoQueryExecutor` service                       | 5      | ✅      |
| US-060: Execute MQL button + results in UI                 | 5      | ✅      |

**Sprint 12 Total**: 16 points

---

### Sprint 13 — Sidebar Mixin & Hardening
**Goal**: Close the two deferred carry-over items (US-051 sidebar mixin, US-054 pyproject optional deps) and harden the MongoDB test suite

| Story                                                                               | Points | Status |
| ----------------------------------------------------------------------------------- | ------ | ------ |
| US-051: Refactor sidebar — `RelationalConnectorSidebar` mixin *(deferred from S11)* | 3      | ✅      |
| US-054: `pyproject.toml` optional-dependency groups *(deferred from S11)*           | 1      | ✅      |
| US-061: `MongoQueryExecutor` live Docker integration test                           | 3      | ✅      |
| US-062: `app.py` Execute MQL unit tests                                             | 2      | ✅      |

**Sprint 13 Total**: 9 points

---

### Sprint 14 — Dependency Hygiene & Coverage Uplift
**Goal**: Declare `testcontainers[mongo]` in dev deps; raise unit coverage for `schema_detector.py` and `db_connector.py`

| Story                                                     | Points | Status |
| --------------------------------------------------------- | ------ | ------ |
| US-063: Add `testcontainers[mongo]` to dev deps           | 1      | ✅      |
| US-064: Increase `schema_detector.py` unit coverage ≥ 80% | 3      | ✅      |
| US-065: Increase `db_connector.py` unit coverage ≥ 75%    | 3      | ✅      |

**Sprint 14 Total**: 7 points

---

### Sprint 15 — Coverage Completeness & CI Hardening
**Goal**: Cover all remaining uncovered lines in `mongo_connector.py`, `models/config.py`, and `utils/network.py`; add sidebar component tests; verify the CI `coverage-docker` matrix job

| Story                                        | Points | Status |
| -------------------------------------------- | ------ | ------ |
| US-066: `mongo_connector.py` coverage uplift | 3      | ✅      |
| US-067: `models/config.py` coverage uplift   | 2      | ✅      |
| US-068: `utils/network.py` coverage uplift   | 1      | ✅      |
| US-069: Sidebar component unit tests         | 3      | ✅      |
| US-070: Verify CI coverage-docker matrix job | 2      | ✅      |

**Sprint 15 Total**: 11 points

---

### Sprint 16 — Component Refactoring & Full Coverage
**Goal**: Refactor sidebar component to enable line-level unit coverage, verify CI coverage-docker end-to-end, and reduce unit suite runtime via pytest-xdist

| Story                                                            | Points | Status |
| ---------------------------------------------------------------- | ------ | ------ |
| US-071: Refactor sidebar: extract pure logic from widget calls   | 5      | ✅      |
| US-072: Add unit tests for extracted sidebar logic               | 3      | ✅      |
| US-073: Verify coverage-docker job on GitHub Actions test branch | 2      | ✅      |
| US-074: Investigate pytest-xdist parallel execution              | 1      | ✅      |

**Sprint 16 Total**: 11 points

---

### Sprint 17 — Component Coverage Completion
**Goal**: Remove `src/components/*` from the coverage `omit` list and add rendering-method tests for Streamlit paths that pure-function extraction cannot reach

| Story                                                    | Points | Status |
| -------------------------------------------------------- | ------ | ------ |
| US-075: Re-enable component coverage; hold ≥ 80% gate    | 5      | ✅      |
| US-076: AppTest rendering-method tests (step2, URI mode) | 3      | ✅      |
| US-077: Investigate AppTest fixture sharing              | 2      | ✅      |
| US-078: Cover error branches in `db_connector.py`        | 3      | ✅      |

**Sprint 17 Total**: 13 points

---

### Sprint 18 — Final Coverage Perfection
**Goal**: Raise reported test coverage to 100% by annotating architecturally-unreachable lines with `# pragma: no cover` and adding targeted AppTest tests

| Story                                                                  | Points | Status |
| ---------------------------------------------------------------------- | ------ | ------ |
| US-079: Apply `# pragma: no cover` to unreachable branches             | 3      | ✅      |
| US-080: AppTest tests for progress_tracker, query_input, schema_viewer | 5      | ✅      |
| US-081: Document pragma pattern + AppTest isolation guidance           | 2      | ✅      |

**Sprint 18 Total**: 10 points

---

### Sprint 19 — Maintainability & Developer Experience
**Goal**: Consolidate the 100% coverage achievement with a README badge, an automated pragma-audit CI check, and a widget-component extraction guideline (ADR-007)

| Story                                                               | Points | Status |
| ------------------------------------------------------------------- | ------ | ------ |
| US-082: Add coverage badge to README.md                             | 1      | ✅      |
| US-083: CI pragma-audit check                                       | 3      | ✅      |
| US-084: Widget-component pure-helper extraction guideline (ADR-007) | 2      | ✅      |

**Sprint 19 Total**: 6 points

---

### Sprint 20 — Query History & Export
**Goal**: Add session-scoped query history (last 10 queries with re-use) and CSV export of the most recent result set

| Story                                        | Points | Status |
| -------------------------------------------- | ------ | ------ |
| US-085: Session-scoped query history         | 5      | ✅      |
| US-086: CSV export of most recent result set | 3      | ✅      |

**Sprint 20 Total**: 8 points

---

### Sprint 21 — Query History UX Polish
**Goal**: Store `db_type` in each history entry for correct syntax highlighting; add a Clear History button

| Story                                  | Points | Status |
| -------------------------------------- | ------ | ------ |
| US-087: Store db_type in history entry | 2      | ✅      |
| US-088: Clear History button           | 1      | ✅      |

**Sprint 21 Total**: 3 points

---

### Sprint 22 — History Panel Display Polish
**Goal**: Display a database-type badge (🐬 MySQL, 🐘 PostgreSQL, 🍃 MongoDB) in each history entry so users can instantly identify the database context of a past query

| Story                                          | Points | Status |
| ---------------------------------------------- | ------ | ------ |
| US-089: Display db_type badge in history entry | 2      | ✅      |

**Sprint 22 Total**: 2 points

---

**Cumulative**: 271 pts · 88 stories · 22 sprints ✅

---

## Epic Progress

| Epic                                              | Stories | Done | Progress        |
| ------------------------------------------------- | ------- | ---- | --------------- |
| EPIC-001: Core SQL Generation                     | 4       | 4    | ██████████ 100% |
| EPIC-002: Streamlit UI                            | 4       | 4    | ██████████ 100% |
| EPIC-003: Dynamic Schema                          | 5       | 5    | ██████████ 100% |
| EPIC-004: Quality Assurance                       | 5       | 5    | ██████████ 100% |
| EPIC-005: Deployment & DevOps                     | 4       | 4    | ██████████ 100% |
| EPIC-006: Live DB Selector                        | 5       | 5    | ██████████ 100% |
| EPIC-007: MongoDB Database Support                | 6       | 6    | ██████████ 100% |
| EPIC-008: MongoDB Flexible Connection Input (URI) | 7       | 7    | ██████████ 100% |
| EPIC-009: PostgreSQL Live Connection Support      | 6       | 6    | ██████████ 100% |
| EPIC-010: MQL Query Execution from UI             | 4       | 4    | ██████████ 100% |
| EPIC-011: Dependency Hygiene & Coverage Uplift    | 3       | 3    | ██████████ 100% |
| EPIC-012: Coverage Completeness & CI Hardening    | 5       | 5    | ██████████ 100% |
| EPIC-013: Component Refactoring & Full Coverage   | 4       | 4    | ██████████ 100% |
| EPIC-014: Component Coverage Completion           | 4       | 4    | ██████████ 100% |
| EPIC-015: Final Coverage Perfection               | 3       | 3    | ██████████ 100% |
| EPIC-016: Maintainability & Developer Experience  | 3       | 3    | ██████████ 100% |
| EPIC-017: Query History & Export                  | 2       | 2    | ██████████ 100% |
| EPIC-018: Query History UX Polish                 | 2       | 2    | ██████████ 100% |
| EPIC-019: History Panel Display Polish            | 1       | 1    | ██████████ 100% |

---

## Milestones

| Milestone                                                                                                             | Target Date   | Status       |
| --------------------------------------------------------------------------------------------------------------------- | ------------- | ------------ |
| M1: SQL generator works end-to-end (CLI)                                                                              | Sprint 1 End  | ✅ DONE       |
| M2: Full Streamlit UI for static schema                                                                               | Sprint 1 End  | ✅ DONE       |
| M3: Live DB connect, detect, execute                                                                                  | Sprint 2 End  | ✅ DONE       |
| M4: All tests passing, coverage ≥ 80%                                                                                 | Sprint 3 End  | ✅ DONE       |
| M5: v1.0.0 released to GHCR                                                                                           | Sprint 4 End  | ✅ DONE       |
| M6: Two-step live DB connection flow                                                                                  | Sprint 5 End  | ✅ DONE       |
| M7: MongoDB live database support                                                                                     | Sprint 6 End  | ✅ DONE       |
| M8: MongoDB URI + credentials input mode                                                                              | Sprint 7 End  | ✅ DONE       |
| M9: AppTest UI coverage + quality hardening                                                                           | Sprint 8 End  | ✅ DONE       |
| M10: Coverage completeness + DX (Step 2 AppTest, Docker MySQL fixture, AppTest quirks doc, PostgreSQL evaluation)     | Sprint 9 End  | ✅ DONE       |
| M11: PostgreSQL live connection support                                                                               | Sprint 10 End | ✅ DONE       |
| M12: Refactor & hardening (WSL2 helper, CI Docker matrix, sslmode pre-validation; US-051/054 deferred)                | Sprint 11 End | ✅ DONE (79%) |
| M13: MQL query execution end-to-end (dynamic label, system prompt, executor, Execute MQL button)                      | Sprint 12 End | ✅ DONE       |
| M14: Sidebar mixin, pyproject optional deps, Docker integration test, app.py MQL unit tests                           | Sprint 13 End | ✅ DONE       |
| M15: Dependency hygiene, testcontainers[mongo], schema_detector/db_connector 100% coverage                            | Sprint 14 End | ✅ DONE       |
| M16: 100% coverage on all measured modules (568 stmts), CI coverage-docker job active                                 | Sprint 15 End | ✅ DONE       |
| M17: Pure-logic sidebar extraction, pytest-xdist (~41% speedup), 74 stories delivered                                 | Sprint 16 End | ✅ DONE       |
| M18: Component coverage re-enabled (src/components/* in gate), rendering-method AppTest coverage                      | Sprint 17 End | ✅ DONE       |
| M19: 100% test coverage achieved across all modules; automated pragma-audit CI gate; ADR-007 widget-component pattern | Sprint 19 End | ✅ DONE       |
| M20: Session query history panel (10 entries, re-use) + CSV export of most recent result set                          | Sprint 20 End | ✅ DONE       |
| M21: Query history UX — db_type syntax highlighting + Clear History button                                            | Sprint 21 End | ✅ DONE       |
| M22: History panel db_type badge; Windows run_app.ps1 + WSL2 run_app.sh launcher scripts; 420 unit tests, 100% cov    | Sprint 22 End | ✅ DONE       |

---

## Future Backlog (Post Sprint 22)

- **History entry timestamp** — record `datetime.utcnow().isoformat()` per entry so users can see query age *(source: SPRINT-22-retro.md)*
- **History copy-to-clipboard** — "📋 Copy SQL" button per entry to copy SQL without re-running *(source: SPRINT-22-retro.md)*
- **History full export** — export complete query history as structured JSON/CSV for audit *(source: SPRINT-22-retro.md)*
- **History persistence across sessions** — lightweight JSON persistence layer (`.eng2sql_history.json`) to survive Streamlit restarts *(source: SPRINT-21-retro.md)*
- **History search/filter** — search-by-keyword filter on the history expander when > 5 entries *(source: SPRINT-21-retro.md)*
- **CSV export date timezone** — use user's local timezone for the filename date, not server date *(source: SPRINT-20-retro.md)*
- **Dynamic coverage badge (Codecov/Coveralls)** — replace static shields.io badge with a badge auto-updated by CI *(source: SPRINT-19-retro.md)*
- **Evaluate ruff plugin for pragma-audit** — track ruff release notes for a native rule that replaces `scripts/pragma_audit.py` *(source: SPRINT-19-retro.md)*
- **MongoDB `sample_size` UI control** — let users tune how many docs are sampled for schema inference *(source: SPRINT-6-retro.md)*
- **Multi-schema PostgreSQL support** — `pg_namespace` enumeration *(deferred from EPIC-009 scope)*
- **AWS RDS IAM auth** for PostgreSQL *(deferred from EPIC-009 scope)*
- **P95 SQL/MQL generation latency baseline** — validate < 5 s target *(source: SPRINT-4-retro.md)*
- **Structured logging + log aggregation** — ELK / CloudWatch integration *(source: SPRINT-4-retro.md)*
- **Automatic schema cache invalidation on reconnect** *(source: SPRINT-2-retro.md)*
- Multi-turn SQL/MQL refinement ("make it filter by date")
- SQL/MQL explanation mode ("what does this query do?")
- User authentication / multi-tenant
- Kubernetes Helm chart
- Save / restore named connection profiles
- MSSQL, Oracle live connection support
