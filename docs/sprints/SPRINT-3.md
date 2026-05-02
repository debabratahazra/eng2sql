# Sprint 3 Plan

**Goal**: ≥ 80% test coverage across all service modules, ruff/mypy clean, pre-commit hooks enforced in CI
**Duration**: 2026-05-29 → 2026-06-11 (2 weeks)
**Velocity Target**: 13 points

---

## Committed Stories

| Story ID | Title                            | Points | Assignee (Agent) |
| -------- | -------------------------------- | ------ | ---------------- |
| US-013   | Unit Tests — SQL Generator       | 3      | Developer        |
| US-014   | Unit Tests — Schema Detector     | 3      | Developer        |
| US-015   | Integration Tests — DB Connector | 5      | Developer        |
| US-016   | Linting & Type Checking          | 2      | Developer        |

**Total**: 13 points

---

## Definition of Done

- [x] Code implemented and committed
- [x] Code review passed
- [x] All new test functions passing
- [x] `pytest --cov=src --cov-fail-under=80` passes
- [x] `ruff check src/ tests/` exits 0
- [x] `mypy src/` exits 0
- [x] `.pre-commit-config.yaml` installed and verified
- [x] Documentation updated (developer-guide.md)

---

## Sprint Risks

| Risk                                                                               | Likelihood | Impact | Mitigation                                                                    |
| ---------------------------------------------------------------------------------- | ---------- | ------ | ----------------------------------------------------------------------------- |
| BUG-001: UI layer (app.py, components/) cannot be tested without `AppTest` harness | High       | Medium | Omit UI from coverage scope via `pyproject.toml`; target 80% on services only |
| mypy strict mode failures in legacy code                                           | Medium     | Medium | Fix type annotations incrementally; use `py.typed` marker                     |
| Pre-commit hook conflicts with CI environment                                      | Low        | Low    | Pin hook versions in `.pre-commit-config.yaml`; test locally first            |

---

## Outcome

**Status**: ✅ DONE
**Actual Velocity**: 13 / 13 points (100%)
**Test Coverage**: 91% (38 tests pass; UI layer excluded per BUG-001 scope)
**Notes**: `ruff` and `mypy` both pass clean. `.pre-commit-config.yaml` includes `detect-private-key` and `no-commit-to-branch` hooks.
