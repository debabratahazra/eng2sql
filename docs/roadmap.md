# Eng2SQL — Project Roadmap

## Vision

**Eng2SQL** empowers non-technical users to query any MySQL database using plain English,
with a clean Streamlit interface that shows step-by-step progress and supports both
static schema definitions and live database auto-detection.

---

## Release Timeline

```
May 2026         Jun 2026         Jul 2026         Aug 2026
│                │                │                │
▼                ▼                ▼                ▼
[Sprint 1]──[Sprint 2]──[Sprint 3]──[Sprint 4]──[Sprint 5]──[Sprint 6]──[Sprint 7]──[Sprint 8]
Foundation  Core UI      QA          Deploy       Live DB     MongoDB     URI Mode    Hardening
                                     v1.0.0       Selector    Support     (EPIC-008)  (Retro)
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

---

## Milestones

| Milestone                                                                                                         | Target Date   | Status       |
| ----------------------------------------------------------------------------------------------------------------- | ------------- | ------------ |
| M1: SQL generator works end-to-end (CLI)                                                                          | Sprint 1 End  | ✅ DONE       |
| M2: Full Streamlit UI for static schema                                                                           | Sprint 1 End  | ✅ DONE       |
| M3: Live DB connect, detect, execute                                                                              | Sprint 2 End  | ✅ DONE       |
| M4: All tests passing, coverage ≥ 80%                                                                             | Sprint 3 End  | ✅ DONE       |
| M5: v1.0.0 released to GHCR                                                                                       | Sprint 4 End  | ✅ DONE       |
| M6: Two-step live DB connection flow                                                                              | Sprint 5 End  | ✅ DONE       |
| M7: MongoDB live database support                                                                                 | Sprint 6 End  | ✅ DONE       |
| M8: MongoDB URI + credentials input mode                                                                          | Sprint 7 End  | ✅ DONE       |
| M9: AppTest UI coverage + quality hardening                                                                       | Sprint 8 End  | ✅ DONE       |
| M10: Coverage completeness + DX (Step 2 AppTest, Docker MySQL fixture, AppTest quirks doc, PostgreSQL evaluation) | Sprint 9 End  | ✅ DONE       |
| M11: PostgreSQL live connection support                                                                           | Sprint 10 End | ✅ DONE       |
| M12: Refactor & hardening (WSL2 helper, CI Docker matrix, sslmode pre-validation; US-051/054 deferred)            | Sprint 11 End | ✅ DONE (79%) |
| M13: MQL query execution end-to-end (dynamic label, system prompt, executor, Execute MQL button)                  | Sprint 12 End | ✅ DONE       |
| M14: Sidebar mixin, pyproject optional deps, Docker integration test, app.py MQL unit tests                       | Sprint 13 End | ✅ DONE       |
| M15: Dependency hygiene, testcontainers[mongo], schema_detector/db_connector 100% coverage                        | Sprint 14 End | ✅ DONE       |
| M16: 100% coverage on all measured modules (568 stmts), CI coverage-docker job active                             | Sprint 15 End | ✅ DONE       |
| M17: Pure-logic sidebar extraction, pytest-xdist (~41% speedup), 74 stories delivered                             | Sprint 16 End | ✅ DONE       |
| M18: Component coverage re-enabled (src/components/* in gate), rendering-method AppTest coverage                  | Sprint 17 End | 🔲 Planned    |

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
