# EPIC-012 — Coverage Completeness & CI Hardening

**ID**: EPIC-012
**Created**: 2025-07-25
**Sprint**: 15
**Source**: SPRINT-14-retro.md (Action Items AI-1 to AI-5)
**Status**: 🔲 Not Started

---

## Goal

Bring all remaining source modules to ≥ 90% unit coverage and verify that the CI
`coverage-docker` matrix job runs correctly on GitHub Actions.

---

## Context

Sprint 14 achieved 98.06% overall coverage, but four modules still have uncovered lines:

| Module                      | Coverage   | Uncovered                                                |
| --------------------------- | ---------- | -------------------------------------------------------- |
| `mongo_connector.py`        | 95%        | 232, 341–342, 351–352 (import fallback + error branches) |
| `models/config.py`          | 97%        | 79, 177–178 (validation branches)                        |
| `utils/network.py`          | 97%        | 77 (WSL2 error branch)                                   |
| `src/components/sidebar.py` | ~0% direct | No component-level unit tests                            |

The CI `coverage-docker` matrix job (US-053) was planned but not verified end-to-end.

---

## Acceptance Outcomes

1. All modules except `app.py` reach ≥ 90% unit coverage.
2. `mongo_connector.py` uncovered error branches are exercised via mocks.
3. `models/config.py` validation branches covered.
4. `utils/network.py` WSL2 error branch covered.
5. At least one component-level unit test exists for `src/components/sidebar.py`.
6. CI `coverage-docker` matrix job runs successfully on GitHub Actions.

---

## User Stories

| Story  | Title                                | Pts |
| ------ | ------------------------------------ | --- |
| US-066 | `mongo_connector.py` coverage uplift | 3   |
| US-067 | `models/config.py` coverage uplift   | 2   |
| US-068 | `utils/network.py` coverage uplift   | 1   |
| US-069 | Sidebar component unit tests         | 3   |
| US-070 | Verify CI coverage-docker matrix job | 2   |

**Total**: 11 pts
