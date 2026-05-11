# EPIC-013 — Component Refactoring & Full-Stack Coverage

**Created by**: Retro Analyzer (from SPRINT-15-retro.md action items)  
**Sprint seeded**: 16  
**Priority**: High  
**Status**: 🔲 Not Started

---

## Goal

Refactor `src/components/` to separate pure business logic from Streamlit widget calls,  
enabling line-level coverage measurement for all components. Also verify the CI  
coverage-docker job end-to-end on GitHub Actions and investigate test suite performance.

---

## Acceptance Outcomes

1. `src/components/sidebar.py` has extractable pure-logic functions testable without `st.*`
2. `src/app.py` pure helper functions (if any) are covered by unit tests
3. GitHub Actions `coverage-docker` job runs successfully on a test branch
4. Unit suite runtime reduced below 60 s (current: ~88 s)

---

## Epics → User Stories (Sprint 16 Backlog)

| Story  | Title                                                    | Points |
| ------ | -------------------------------------------------------- | ------ |
| US-071 | Refactor sidebar: extract pure logic from widget calls   | 5      |
| US-072 | Add unit tests for extracted sidebar logic               | 3      |
| US-073 | Verify coverage-docker job on GitHub Actions test branch | 2      |
| US-074 | Investigate pytest-xdist parallel execution              | 1      |

---

## Notes

Seeded from SPRINT-15-retro.md action items 1–4.
