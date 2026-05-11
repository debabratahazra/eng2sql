# Sprint 19 Retrospective

**Sprint**: 19  
**Date**: 2026-05-09  
**Velocity**: 6 points (US-082: 1pt, US-083: 3pt, US-084: 2pt)  
**Cumulative Velocity**: 258 points  
**Status**: ✅ Complete  

---

## What Went Well

- **All three Sprint 18 action items closed** in a single sprint: coverage badge,
  automated pragma audit, and widget-extraction guideline. The sprint fully delivered
  its "Maintainability & DX" goal.
- **`scripts/pragma_audit.py` is a lightweight, self-contained tool** (100 lines, 0
  external dependencies) with 18 unit tests and a real-source regression guard. Future
  contributors can read and understand it in under 5 minutes.
- **CI integration is minimal and fast** — the pragma audit step runs in <1 s inside
  the existing `lint` job, adding no meaningful CI latency.
- **ADR-007 closes the documentation gap** identified in Sprint 16: the extraction
  pattern had never been formally documented even though it was introduced 3 sprints ago.
- All 23 Sprint 19 smoke tests pass in 2.60 s; full 125-test smoke suite passes.
- Coverage remains at **100.00%** (941 stmts, 0 miss) after Sprint 19 changes.
- The certifi pragma in `sidebar.py` now has a proper justification comment — a minor
  correctness issue from Sprint 18 is resolved.

---

## What Could Be Improved

- **US-084 is documentation only** — the worked example in the developer guide covers
  `ProgressTracker`, but `query_input.py` and `schema_viewer.py` still have no
  extracted helpers. If those components grow logic in the future, a follow-up story
  will be needed to apply the pattern.
- **The static shields.io badge requires manual update** if coverage ever drops below
  100% (e.g. after adding a new untested module). A dynamic badge connected to a
  coverage service (Codecov, Coveralls) would eliminate this manual maintenance burden.
  Deferred to Future Backlog.
- **`pragma_audit.py` lives in `scripts/`**, outside the main test infrastructure.
  If more tooling scripts are added, a `tools/` package with its own test directory
  might be cleaner. Deferred to Future Backlog.
- Sprint 19 had only 6 points — the smallest sprint since Sprint 1. This is acceptable
  given that the sprint was focused on consolidating technical debt rather than new
  features.

---

## Action Items

1. **Dynamic coverage badge** — integrate with a real coverage service (Codecov or
   Coveralls) in CI so the badge auto-updates. This requires a third-party account
   and CI secret; defer to a sprint where infrastructure work is scheduled.
2. **Review `query_input.py` and `schema_viewer.py` for future logic** — if either
   file grows beyond widget calls in a future sprint, the US-084 pattern must be
   applied (extract, test, then keep the render path under pragma).
3. **Evaluate ruff plugin for pragma-audit** — as ruff evolves, a native `FLB` or
   custom rule may replace the `scripts/pragma_audit.py` grep approach. Track ruff
   release notes.

---

## Sprint 20 Seeds (from Action Items)

Sprint 20 action items are lightweight; they should be added to the roadmap Future
Backlog rather than a dedicated sprint unless other work is scheduled alongside them.
If the next sprint focuses on new features (e.g. query history, export to CSV), the
badge and tooling improvements can ride along as low-effort additions.

---

## Metrics

| Metric                 | Sprint 19                   | Cumulative |
| ---------------------- | --------------------------- | ---------- |
| Story points delivered | 6                           | 258        |
| User stories completed | 3 (US-082, US-083, US-084)  | 83         |
| New unit tests added   | 18 (pragma_audit.py)        | ~848       |
| New smoke tests added  | 23                          | 125        |
| Bugs filed             | 0                           | 8          |
| Bugs resolved          | 0                           | 8          |
| Coverage               | 100.00% (941 stmts, 0 miss) | —          |
