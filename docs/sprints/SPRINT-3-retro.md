# Sprint 3 Retrospective

**Sprint**: Sprint 3 — Quality Assurance
**Date**: 2026-06-11
**Facilitator**: Scrum Master

---

## What Went Well

- 38 tests pass with zero warnings — clean test suite
- 91% coverage exceeds the 80% gate with comfortable margin
- `ruff` and `mypy` both pass cleanly — no suppressions needed
- Pre-commit hooks (`detect-private-key`, `no-commit-to-branch`) add strong safety net
- `yield`-based `sqlite_engine` fixture cleanly eliminates all ResourceWarning noise (BUG-002 resolution)
- `pyproject.toml` `[tool.coverage.run]` omit list cleanly excludes UI layer without lowering the gate

## What Could Be Improved

- BUG-001 (UI component coverage) remains open — `AppTest`-based tests for `src/components/`
  and `src/app.py` are still deferred; these represent ~9% of uncovered lines
- Test count (38) covers services well but no tests for utility modules (`logger.py`,
  `exceptions.py`) — these are simple enough to be low risk but worth noting
- Sprint 3 stories (US-013–016) were created as documentation during the User Story Writer
  session rather than written before Sprint 3 started; story-first discipline should be
  maintained going forward

## Action Items

| Action                                                       | Owner        | Due      |
| ------------------------------------------------------------ | ------------ | -------- |
| Create `AppTest`-based UI tests for Sprint 5 / future sprint | Scrum Master | Backlog  |
| Add `exceptions.py` and `logger.py` to test scope            | Developer    | Sprint 5 |
| Enforce story files created before sprint kickoff            | Scrum Master | Ongoing  |
