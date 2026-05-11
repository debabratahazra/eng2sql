# Sprint 8 Plan

**Goal**: Technical quality hardening — AppTest UI coverage, MongoConfig branch coverage, sidebar import cleanup, and password session-state security
**Duration**: 2026-05-06 → 2026-05-19 (2 weeks)
**Velocity Target**: 11 points
**Source**: Auto-generated from SPRINT-7-retro.md by Retro Analyzer (2026-05-06)

---

## Committed Stories

| Story ID | Title                                                | Points | Assignee (Agent) |
| -------- | ---------------------------------------------------- | ------ | ---------------- |
| US-036   | Move `urllib.parse` import to module level           | 1      | Developer        |
| US-037   | Increase `MongoConfig` uncovered branch coverage     | 2      | Developer        |
| US-038   | AppTest-based sidebar UI tests (mode toggle & forms) | 5      | Developer        |
| US-039   | Harden `_db_password` session state storage          | 3      | Developer        |

**Total committed**: 11 points

---

## Carried-Over Context

| Source Retro   | Original Item                                     | Action Taken         |
| -------------- | ------------------------------------------------- | -------------------- |
| SPRINT-4-retro | `AppTest` sidebar UI tests (BUG-001)              | → US-038 this sprint |
| SPRINT-5-retro | `_db_password` in session state — security review | → US-039 this sprint |
| SPRINT-6-retro | `directConnection` SRV incompatibility            | ✅ Fixed in Sprint 7  |
| SPRINT-7-retro | `urllib.parse` local import style inconsistency   | → US-036 this sprint |
| SPRINT-7-retro | `MongoConfig.__repr__` + else branch uncovered    | → US-037 this sprint |

---

## Definition of Done

- [x] Code implemented and committed
- [x] Code review passed
- [x] Unit tests written and passing (≥ 80% coverage — target: raise to ≥ 93%)
- [x] Integration tests passing
- [x] Documentation updated
- [x] No critical bugs open

---

## Sprint Risks

- Risk: `AppTest` (US-038) requires Streamlit ≥ 1.28 — verify `requirements.txt` version.
- Mitigation: Check `streamlit` pinned version; upgrade if needed and re-run existing tests.
- Risk: Password-clearing (US-039) may affect the two-step connection UX if timing is wrong.
- Mitigation: Write regression tests for the full connect-and-query flow before merging.
