# Sprint 21 — Query History UX Polish

**Sprint**: 21  
**Start Date**: 2026-05-10 (estimated)  
**End Date**: 2026-05-16 (estimated)  
**Velocity Target**: 3 points  
**Epic**: EPIC-018 — Query History UX Polish  

---

## Sprint Goal

Improve the Sprint 20 query history feature: store `db_type` in each entry for correct
syntax highlighting, and add a "Clear History" button for session-state control.

---

## Sprint Backlog

| Story  | Title                          | Points | Priority |
| ------ | ------------------------------ | ------ | -------- |
| US-087 | Store db_type in history entry | 2      | Low      |
| US-088 | Clear history button           | 1      | Low      |

**Total**: 3 points

---

## Sprint 20 Carry-Forward

No carry-forward items; Sprint 20 delivered all two active stories.

---

## Coverage Baseline (Sprint 20 End)

| Metric              | Value               |
| ------------------- | ------------------- |
| Measured statements | 962                 |
| Misses              | 0                   |
| Coverage            | **100.00%**         |
| Gate                | `fail_under = 80` ✅ |

---

## Definition of Done (Sprint)

- [ ] US-087 and US-088 acceptance criteria met
- [ ] All new pure helpers unit-tested; coverage gate (≥ 80%) continues to pass
- [ ] Sprint 21 smoke test file created and passing
- [ ] CR-021 code review completed
- [ ] SPRINT-21-retro.md created
- [ ] Sprint 22 seeded (if action items warrant)
- [ ] `PROJECT_PROGRESS.md` updated

---

## Notes

- US-087 modifies the `_append_to_history` signature — update call sites in `app.py`
  and all affected unit tests in `test_query_history.py`.
- US-088 is widget-only for the button, but the "no history → no render" guard is
  already a tested pure path (it's in the `render()` pragma block — no new helper needed).
- The pragma audit must pass after both stories are implemented.
