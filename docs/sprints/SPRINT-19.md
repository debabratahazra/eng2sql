# Sprint 19 — Maintainability & Developer Experience

**Sprint**: 19  
**Start Date**: 2026-05-08 (estimated)  
**End Date**: 2026-05-21 (estimated)  
**Velocity Target**: 6 points  
**Epic**: EPIC-016 — Maintainability & Developer Experience  

---

## Sprint Goal

Consolidate the 100% coverage achievement with a README badge, an automated
pragma-audit CI check, and a widget-component extraction guideline for future contributors.

---

## Sprint Backlog

| Story  | Title                                             | Points | Priority |
| ------ | ------------------------------------------------- | ------ | -------- |
| US-082 | Add coverage badge to README.md                   | 1      | Low      |
| US-083 | CI pragma-audit check                             | 3      | Medium   |
| US-084 | Widget-component pure-helper extraction guideline | 2      | Low      |

**Total**: 6 points

---

## Sprint 18 Carry-Forward

No carry-forward items; Sprint 18 delivered all active stories (US-079, US-081).
US-080 was cleanly descoped.

---

## Coverage Baseline (Sprint 18 End)

| Metric              | Value               |
| ------------------- | ------------------- |
| Measured statements | 941                 |
| Misses              | 0                   |
| Coverage            | **100.00%**         |
| Gate                | `fail_under = 80` ✅ |

---

## Definition of Done (Sprint)

- [ ] All US-082–084 acceptance criteria met
- [ ] Coverage gate (≥ 80%) continues to pass
- [ ] All 360 unit tests + 102 smoke tests pass
- [ ] Sprint 19 smoke test file created and passing
- [ ] CR-019 code review completed
- [ ] SPRINT-19-retro.md created
- [ ] Sprint 20 seeded (if action items warrant)
- [ ] `PROJECT_PROGRESS.md` updated

---

## Notes

- US-082 (coverage badge) requires a Codecov or similar external service to be configured;
  a shields.io static badge pointing at the CI XML artifact is an acceptable fallback.
- US-083 (pragma audit) can use a simple `grep` script in CI rather than a full
  `ruff` plugin if the ruff rule set does not support custom patterns.
- `-n auto` remains active in `pyproject.toml` addopts; all new tests must be xdist-safe.
