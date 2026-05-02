# Eng2SQL — Project Roadmap

## Vision

**Eng2SQL** empowers non-technical users to query any MySQL database using plain English,
with a clean Streamlit interface that shows step-by-step progress and supports both
static schema definitions and live database auto-detection.

---

## Release Timeline

```
May 2026         Jun 2026         Jul 2026
│                │                │
▼                ▼                ▼
[Sprint 1]───[Sprint 2]───[Sprint 3]───[Sprint 4]───[Sprint 5]
Foundation    Core UI       QA            Deploy        Live DB
                                          v1.0.0        Selector
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
| US-021: Remove Static Schema Mode & MySQL-Only Sidebar        | 3      | 🔲      |
| US-022: Step 1 — Server Connect & Database Discovery          | 5      | 🔲      |
| US-023: Step 2 — Database Selector & Engine Activation        | 5      | 🔲      |
| US-024: `DBConnector.list_databases()` Service Method & Tests | 3      | 🔲      |

**Sprint 5 Total**: 16 points

---

## Epic Progress

| Epic                          | Stories | Done | Progress        |
| ----------------------------- | ------- | ---- | --------------- |
| EPIC-001: Core SQL Generation | 4       | 4    | ██████████ 100% |
| EPIC-002: Streamlit UI        | 4       | 4    | ██████████ 100% |
| EPIC-003: Dynamic Schema      | 5       | 4    | ████████░░ 80%  |
| EPIC-004: Quality Assurance   | 4       | 4    | ██████████ 100% |
| EPIC-005: Deployment & DevOps | 4       | 4    | ██████████ 100% |
| EPIC-006: Live DB Selector    | 4       | 0    | ░░░░░░░░░░ 0%   |

---

## Milestones

| Milestone                                | Target Date  | Status    |
| ---------------------------------------- | ------------ | --------- |
| M1: SQL generator works end-to-end (CLI) | Sprint 1 End | ✅ DONE    |
| M2: Full Streamlit UI for static schema  | Sprint 1 End | ✅ DONE    |
| M3: Live DB connect, detect, execute     | Sprint 2 End | ✅ DONE    |
| M4: All tests passing, coverage ≥ 80%    | Sprint 3 End | ✅ DONE    |
| M5: v1.0.0 released to GHCR              | Sprint 4 End | ✅ DONE    |
| M6: Two-step live DB connection flow     | Sprint 5 End | 🔲 Planned |

---

## Future Backlog (Post Sprint 5)

- Multi-turn SQL refinement ("make it filter by date")
- PostgreSQL, MSSQL, Oracle live connection support (EPIC-007 placeholder)
- Query history and bookmarks
- SQL explanation mode ("what does this query do?")
- User authentication / multi-tenant
- Kubernetes Helm chart
- Save / restore named connection profiles
