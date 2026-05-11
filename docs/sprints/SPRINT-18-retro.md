# Sprint 18 Retrospective

**Sprint**: 18  
**Date**: 2026-05-07  
**Velocity**: 5 points (US-079: 3pt, US-081: 2pt; US-080 descoped)  
**Cumulative Velocity**: 252 points  
**Status**: ✅ Complete  

---

## What Went Well

- **100% coverage achieved** for the first time across the full measured codebase
  (941 statements, 0 miss). US-079's pragma strategy required zero new tests and zero
  production logic changes — a clean, minimal solution.
- **US-080 cleanly descoped**: the story explicitly anticipated this outcome
  ("If US-079 is implemented instead, this story can be descoped"), so no story-point
  deduction is needed. The sprint still delivered its primary goal.
- **Pragma justification comments** are co-located with every annotation — future
  contributors will immediately understand why a line is excluded without needing to
  search the git history.
- **Developer guide enriched** with two high-value sections (xdist isolation, pragma
  pattern) that resolve the two most common contributor confusion points identified
  in Sprint 17.
- All 15 Sprint 18 smoke tests pass in 7.29 s; full 102-test smoke suite passes.
- No regressions: all 360 unit tests continue to pass.

---

## What Could Be Improved

- **US-080 was never really needed** — the story was created as an alternative to US-079
  before the team committed to the pragma strategy. Sprint planning could have resolved
  this conflict earlier (at story refinement) instead of carrying both into the sprint.
- **`progress_tracker.py` and `query_input.py` have zero testable logic** outside of
  Streamlit widget calls. Future enhancements to these components should extract any
  business logic into pure helpers (following the Sprint 16 pattern) to avoid growing
  the pragma-excluded surface area.
- **15 smoke tests** is slightly below the established 16-test-per-sprint pattern. The
  sprint had fewer deliverables than average (annotation + docs only), so this is
  acceptable.
- The statement count dropped from 966 → 941 (25 excluded). This is correct behaviour
  but worth documenting: the 100% figure reflects the *measured* surface, not the total
  source lines.

---

## Action Items

1. **Pure-logic extraction for remaining widget-heavy components** — if `progress_tracker.py`
   or `query_input.py` grow new logic in future sprints, extract it into pure helpers
   following the Sprint 16 `_validate_*` / `_build_*` pattern so it can be tested
   without Streamlit.
2. **Coverage badge in README** — now that the project is at 100%, add a coverage badge
   to `README.md` pointing at the CI coverage artifact.
3. **Automate pragma audit** — add a `ruff` or `grep`-based check in CI that flags any
   NEW `# pragma: no cover` added without a justification comment. This prevents future
   contributors from adding silent exclusions.

---

## Sprint 19 Seeds (from Action Items)

- **EPIC-016**: Maintainability & Developer Experience
  - US-082: Add coverage badge to README.md
  - US-083: Add CI pragma-audit check (ruff noqa rule or pre-commit hook)
  - US-084: Extract pure helpers from `progress_tracker.py` / `query_input.py`
    (if those components add new logic)

---

## Metrics

| Metric                 | Sprint 18                                         | Cumulative |
| ---------------------- | ------------------------------------------------- | ---------- |
| Story points delivered | 5 (US-080 descoped, -5 not counted against)       | 252        |
| User stories completed | 2 (US-079, US-081)                                | 80         |
| New tests added        | 15 (smoke only)                                   | ~830       |
| Bugs filed             | 0                                                 | 5          |
| Bugs resolved          | 0                                                 | 5          |
| Code reviews           | 1 (CR-018)                                        | 18         |
| Test result docs       | 5 (UTR-023, TR-018, ITR-010, STR-009, TC-119–124) | —          |
| Coverage               | **100.00%** (941 stmts, 0 miss)                   | —          |
