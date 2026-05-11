# Sprint 15 Plan

**Sprint**: 15
**Start**: 2025-07-28
**End**: 2025-08-08
**Scrum Master**: Scrum Master Agent
**Epic**: EPIC-012 — Coverage Completeness & CI Hardening
**Source**: SPRINT-14-retro.md (Action Items AI-1 to AI-5)

---

## Sprint Goal

> Cover all remaining uncovered lines in `mongo_connector.py`, `models/config.py`, and
> `utils/network.py`; add sidebar component tests; and verify the CI `coverage-docker`
> matrix job runs end-to-end.

---

## Sprint Board

| Story  | Title                                | Pts | Status        | Owner              |
| ------ | ------------------------------------ | --- | ------------- | ------------------ |
| US-066 | `mongo_connector.py` coverage uplift | 3   | 🔲 Not Started | Unit Test Agent    |
| US-067 | `models/config.py` coverage uplift   | 2   | 🔲 Not Started | Unit Test Agent    |
| US-068 | `utils/network.py` coverage uplift   | 1   | 🔲 Not Started | Unit Test Agent    |
| US-069 | Sidebar component unit tests         | 3   | 🔲 Not Started | Unit Test Agent    |
| US-070 | Verify CI coverage-docker matrix job | 2   | 🔲 Not Started | Developer / DevOps |

**Total**: 11 pts

---

## Definition of Done (Sprint Level)

- [ ] All user stories ✅ Done
- [ ] 264+ unit tests pass (target ≥ 275 after Sprint 15 additions)
- [ ] Overall coverage remains ≥ 98%
- [ ] `mongo_connector.py` ≥ 90%
- [ ] `models/config.py` ≥ 99%
- [ ] `utils/network.py` = 100%
- [ ] CR-015 code review approved
- [ ] TR-015 full test run documented
- [ ] STR-006 smoke test suite created and passing
- [ ] SPRINT-15-retro.md written

---

## Risks

| Risk                                                         | Mitigation                                                       |
| ------------------------------------------------------------ | ---------------------------------------------------------------- |
| `mongo_connector.py` import-time fallback paths hard to mock | Investigate module-level mock at collection time                 |
| Sidebar component isolation requires Streamlit internals     | Use `unittest.mock.patch` on `st.*` calls rather than AppTest    |
| CI Docker job may require secrets or self-hosted runner      | Document clearly and gate with `if: github.event_name == 'push'` |

---

## Velocity Reference

| Sprint               | Pts    | %    |
| -------------------- | ------ | ---- |
| Sprint 13            | 10/10  | 100% |
| Sprint 14            | 7/7    | 100% |
| **Sprint 15 target** | **11** | —    |
