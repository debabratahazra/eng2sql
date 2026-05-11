# Sprint 20 — Query History & Export

**Sprint**: 20  
**Start Date**: 2026-05-10 (estimated)  
**End Date**: 2026-05-23 (estimated)  
**Velocity Target**: 8 points  
**Epic**: EPIC-017 — Query History & Export  

---

## Sprint Goal

Add session-scoped query history (last 10 queries with re-use) and CSV export of
the most recent result set to the Streamlit app. All new component logic must follow
the ADR-007 pure-helper extraction pattern to remain unit-testable.

---

## Sprint Backlog

| Story  | Title                                | Points | Priority |
| ------ | ------------------------------------ | ------ | -------- |
| US-085 | Session-scoped query history         | 5      | Medium   |
| US-086 | CSV export of most recent result set | 3      | Medium   |

**Total**: 8 points

---

## Sprint 19 Carry-Forward

No carry-forward items; Sprint 19 delivered all three active stories.

---

## Coverage Baseline (Sprint 19 End)

| Metric              | Value               |
| ------------------- | ------------------- |
| Measured statements | 941                 |
| Misses              | 0                   |
| Coverage            | **100.00%**         |
| Gate                | `fail_under = 80` ✅ |

---

## Definition of Done (Sprint)

- [ ] US-085 and US-086 acceptance criteria met
- [ ] All new pure helpers unit-tested; coverage gate (≥ 80%) continues to pass
- [ ] Sprint 20 smoke test file created and passing
- [ ] CR-020 code review completed
- [ ] SPRINT-20-retro.md created
- [ ] Sprint 21 seeded (if action items warrant)
- [ ] `PROJECT_PROGRESS.md` updated

---

## Notes

- Session history should use `st.session_state` with initialisation in `app.py`;
  the history list must be passed to the rendering component rather than read
  directly from session_state inside the helper.
- CSV export uses `pandas.DataFrame.to_csv(index=False)` — pandas is already a
  transitive dependency via `streamlit`; no new requirement needed.
- The pragma-audit CI step (`python scripts/pragma_audit.py`) must pass after any
  new `# pragma: no cover` annotations are added.
