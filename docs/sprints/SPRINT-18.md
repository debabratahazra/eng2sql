# Sprint 18 — Final Coverage Perfection

**Sprint**: 18  
**Start Date**: 2025-08-02 (estimated)  
**End Date**: 2025-08-15 (estimated)  
**Velocity Target**: 10 points  
**Epic**: EPIC-015 — Final Coverage Perfection  

---

## Sprint Goal

Raise reported test coverage from 98.03% to ≥ 99% by annotating architecturally-
unreachable lines with `# pragma: no cover` and/or adding targeted AppTest tests for
the three partially-covered UI components (`progress_tracker`, `query_input`,
`schema_viewer`). Document the patterns for future contributors.

---

## Sprint Backlog

| Story  | Title                                                          | Points | Priority |
| ------ | -------------------------------------------------------------- | ------ | -------- |
| US-079 | Apply `# pragma: no cover` to unreachable branches             | 3      | Medium   |
| US-080 | AppTest tests for progress_tracker, query_input, schema_viewer | 5      | Medium   |
| US-081 | Document pragma pattern + AppTest isolation guidance           | 2      | Low      |

**Total**: 10 points

---

## Sprint 17 Carry-Forward

No carry-forward items; Sprint 17 delivered all 4 stories (13 points).

---

## Current Coverage Baseline (Sprint 17 End)

| File                                 | Stmts   | Miss   | Cover      |
| ------------------------------------ | ------- | ------ | ---------- |
| `src/components/progress_tracker.py` | 15      | 9      | 40%        |
| `src/components/query_input.py`      | 17      | 4      | 76%        |
| `src/components/schema_viewer.py`    | 18      | 4      | 78%        |
| `src/components/sidebar.py`          | 328     | 2      | 99%        |
| All other files                      | —       | 0      | 100%       |
| **TOTAL**                            | **966** | **19** | **98.03%** |

---

## Definition of Done (Sprint)

- [ ] All US-079–081 acceptance criteria met
- [ ] Overall coverage ≥ 99% (or all remaining gaps explicitly `# pragma: no cover`)
- [ ] All existing 360 unit tests + 87 smoke tests pass (0 failures)
- [ ] Sprint 18 smoke test file created and passing
- [ ] CR-018 code review completed
- [ ] SPRINT-18-retro.md created
- [ ] Sprint 19 seeded from retro action items (if needed)
- [ ] `PROJECT_PROGRESS.md` updated

---

## Notes

- US-079 and US-080 are alternatives — if US-079 (pragma) fully resolves all 19
  misses, US-080 can be descoped or reduced in scope to add test coverage value only.
- The `-n auto` xdist flag remains active; AppTest rendering tests must use
  `--override-ini="addopts=..."` for sequential runs (documented in US-081).
- `src/app.py` remains excluded from coverage per ADR-001 / US-075.
