# Sprint 14 — Dependency Hygiene & Coverage Uplift

**Sprint**: 14
**Theme**: Dependency Hygiene & Coverage Uplift
**Epic**: EPIC-009
**Goal**: Declare `testcontainers[mongo]` in dev deps; raise unit coverage for `schema_detector.py` and `db_connector.py`; keep CI green.
**Velocity target**: 7 pts

---

## Sprint Backlog

| #   | Story  | Title                                             | Pts | Priority | Status        |
| --- | ------ | ------------------------------------------------- | --- | -------- | ------------- |
| 1   | US-063 | Add `testcontainers[mongo]` to dev deps           | 1   | High     | 🔲 Not Started |
| 2   | US-064 | Increase `schema_detector.py` unit coverage ≥ 80% | 3   | Medium   | 🔲 Not Started |
| 3   | US-065 | Increase `db_connector.py` unit coverage ≥ 75%    | 3   | Medium   | 🔲 Not Started |

**Total committed**: 7 pts

---

## Definition of Done (Sprint Level)

- [ ] All user stories marked ✅ Done
- [ ] `pytest tests/unit` → ≥ 245 tests passing
- [ ] Overall coverage ≥ 80% (currently 91.55%)
- [ ] `schema_detector.py` ≥ 80% in unit run
- [ ] `db_connector.py` ≥ 75% in unit run
- [ ] STR-005 smoke tests → 10+ pass
- [ ] SPRINT-14-retro.md created

---

## Sprint Phases

| Phase | Agent                  | Output                                             |
| ----- | ---------------------- | -------------------------------------------------- |
| 0     | Retro Analyzer         | Verify SPRINT-13-retro processed                   |
| 5     | Developer              | Implement US-063                                   |
| 5     | Unit Test Agent        | UTR for US-063 (config only — no new tests needed) |
| 5     | Developer              | Implement US-064 test file                         |
| 5     | Unit Test Agent        | UTR-007 for US-064                                 |
| 5     | Developer              | Implement US-065 test file                         |
| 5     | Unit Test Agent        | UTR-008 for US-065                                 |
| 6     | Code Reviewer          | CR-014                                             |
| 7     | Test Case Writer       | TC-076+                                            |
| 8     | Tester                 | TR-014                                             |
| 8b    | Integration Test Agent | ITR-006                                            |
| 8c    | Smoke Test Agent       | STR-005 (test_sprint_14_smoke.py)                  |
| 9     | Retro Analyzer         | SPRINT-14-retro.md                                 |
| 10    | Scrum Master           | Sprint 15 plan                                     |

---

## Carry-Forward Notes

- The `_RelationalDialectConfig` `state_key_prefix` evaluation (Sprint 13 retro action item)
  is deferred to Sprint 15 backlog pending Architect review.
