# Sprint 17 — Component Coverage Completion

**Sprint**: 17  
**Start Date**: 2025-07-15 (estimated)  
**End Date**: 2025-07-28 (estimated)  
**Velocity Target**: 13 points  
**Epic**: EPIC-014 — Component Coverage Completion  

---

## Sprint Goal

Remove `src/components/*` from the coverage `omit` list, add rendering-method tests
for the Streamlit paths that pure-function extraction cannot reach, and ensure the
80% coverage gate continues to hold across the full application.

---

## Sprint Backlog

| Story  | Title                                            | Points | Priority |
| ------ | ------------------------------------------------ | ------ | -------- |
| US-075 | Re-enable component coverage; hold ≥ 80% gate    | 5      | High     |
| US-076 | AppTest rendering-method tests (step2, URI mode) | 3      | High     |
| US-077 | Investigate AppTest fixture sharing              | 2      | Medium   |
| US-078 | Cover error branches in db_connector.py          | 3      | Medium   |

**Total**: 13 points

---

## Sprint 16 Carry-Forward

No carry-forward items; Sprint 16 delivered all 4 stories (11 points).

---

## Definition of Done (Sprint)

- [ ] All US-075–078 acceptance criteria met
- [ ] Overall coverage gate ≥ 80% with `src/components/*` included
- [ ] All 400+ tests pass (0 failures, 0 regressions)
- [ ] Sprint 17 smoke test file created and passing
- [ ] CR-017 code review completed
- [ ] SPRINT-17-retro.md created
- [ ] Sprint 18 seeded from retro action items
- [ ] `PROJECT_PROGRESS.md` updated

---

## Notes

- `src/app.py` will remain excluded from coverage — exercised only via AppTest smoke tests.
- The `-n auto` xdist flag introduced in Sprint 16 is now active by default;
  all new tests must be xdist-compatible (no shared mutable module state between workers).
