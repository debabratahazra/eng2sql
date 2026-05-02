# Sprint 1 Plan

**Goal**: Working SQL generation pipeline with static YAML schema and full Streamlit UI shell
**Duration**: 2026-05-01 → 2026-05-14 (2 weeks)
**Velocity Target**: 21 points

---

## Committed Stories

| Story ID | Title                                 | Points | Assignee (Agent) |
| -------- | ------------------------------------- | ------ | ---------------- |
| US-001   | Static Schema Configuration           | 3      | Developer        |
| US-002   | OpenAI SQL Generation Service         | 5      | Developer        |
| US-003   | Prompt Engineering for Schema Context | 3      | Developer        |
| US-004   | Streamlit App Shell                   | 2      | Developer        |
| US-005   | Query Input Component                 | 3      | Developer        |
| US-006   | Step-by-Step Progress Display         | 3      | Developer        |
| US-007   | SQL Output Panel                      | 2      | Developer        |

**Total**: 21 points

---

## Definition of Done

- [x] Code implemented and committed
- [x] Code review passed (CR-001)
- [x] Unit tests written and passing (≥ 80% coverage — 91% achieved)
- [x] Integration tests passing
- [x] Documentation updated (user-guide.md, developer-guide.md)
- [x] No critical bugs open (BUG-002 fixed; BUG-001 deferred to Sprint 3)

---

## Sprint Risks

| Risk                                        | Likelihood | Impact | Mitigation                                                     |
| ------------------------------------------- | ---------- | ------ | -------------------------------------------------------------- |
| Corporate proxy TLS certificate rejection   | Medium     | High   | Supply `cert/ca-bundle.crt`; use `ssl.SSLContext` with httpx   |
| OpenAI API latency > 5 s P95                | Low        | Medium | Set `timeout=30` on httpx client; show progress indicator      |
| Streamlit re-run model complexity           | Medium     | Medium | Use `st.session_state` for all mutable state; document pattern |
| httpx deprecation of `verify=str` in ≥ 0.28 | Medium     | Low    | Pass `ssl.SSLContext` object, not string path                  |

---

## Outcome

**Status**: ✅ DONE
**Actual Velocity**: 21 / 21 points (100%)
**Test Coverage**: 91% (UI layer excluded per BUG-001 scope decision)
**Notes**: httpx `verify=ssl.SSLContext` fix applied; BUG-002 (ResourceWarning) fixed in teardown
