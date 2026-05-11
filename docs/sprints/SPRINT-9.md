# Sprint 9 Plan

**Goal**: Coverage completeness and developer experience — mock-patched AppTest tests for `_render_step2`, Docker-based MySQL integration fixture, AppTest quirks documentation, and PostgreSQL epic evaluation
**Duration**: 2026-05-06 → 2026-05-20 (2 weeks)
**Velocity Target**: 14 points
**Source**: Auto-generated from SPRINT-8-retro.md action items by Retro Analyzer / Scrum Master (2026-05-06)

---

## Committed Stories

| Story ID | Title                                                        | Points | Assignee (Agent) |
| -------- | ------------------------------------------------------------ | ------ | ---------------- |
| US-040   | Mock-Patched AppTest Tests for `_render_step2`               | 5      | Developer        |
| US-041   | Document AppTest Quirks in Developer Guide                   | 2      | Developer        |
| US-042   | Docker-Based MySQL Integration Fixture for `db_connector.py` | 5      | Developer        |
| US-043   | Evaluate PostgreSQL Live Connection Epic for Sprint 10       | 2      | Scrum Master     |

**Total committed**: 14 points

---

## Backlog (Not Committed This Sprint)

| Item    | Title                                                                 | Type | Severity | Notes                                                                                        |
| ------- | --------------------------------------------------------------------- | ---- | -------- | -------------------------------------------------------------------------------------------- |
| BUG-006 | MongoDB `localhost` timeout in WSL2 — `directConnection` not injected | Bug  | High     | Reported 2026-05-06; requires investigation of embedded-credential URI code path + WSL2 hint |

---

## Carried-Over Context

| Source Retro   | Original Item                                                      | Action Taken              |
| -------------- | ------------------------------------------------------------------ | ------------------------- |
| SPRINT-8-retro | Mock-patched AppTest for `_render_step2` success/failure paths     | → US-040 this sprint      |
| SPRINT-8-retro | Document AppTest quirks (no chain, no `.get()`, timeout)           | → US-041 this sprint      |
| SPRINT-8-retro | Docker MySQL fixture to raise `db_connector.py` coverage > 90%     | → US-042 this sprint      |
| SPRINT-8-retro | Evaluate PostgreSQL live connection epic                           | → US-043 this sprint      |
| BUG-006        | WSL2 `localhost` MongoDB timeout + `directConnection` not injected | Backlog — not this sprint |

---

## Definition of Done

- [ ] Code implemented and committed
- [ ] Code review passed
- [ ] Unit tests written and passing (≥ 80% coverage — target: raise to ≥ 94%)
- [ ] Integration tests passing (Docker required for US-042)
- [ ] Documentation updated
- [ ] No critical bugs open

---

## Sprint Risks

| Risk                                                                                | Likelihood | Impact | Mitigation                                                                        |
| ----------------------------------------------------------------------------------- | ---------- | ------ | --------------------------------------------------------------------------------- |
| `testcontainers` / `pytest-docker` not available in CI environment                  | Medium     | High   | Mark integration tests with `@pytest.mark.integration`; skip by default in CI     |
| Mock patch path mismatch causes `_render_step2` tests to call real DB               | Medium     | Medium | Verify patch target matches exact import path used in `sidebar.py`                |
| `AppTest` widget tree unstable in `_render_step2` (depends on Step 1 session state) | Medium     | Medium | Pre-seed `session_state` keys before `.run()` to simulate post-Step-1 state       |
| PostgreSQL evaluation (US-043) scope creeps into implementation                     | Low        | Medium | US-043 is documentation only; implementation deferred to Sprint 10 if Go decision |

---

## Session State Changes

### No new session state keys expected this sprint

US-040 tests rely on existing session state from Sprints 5–8:
`detected_schema`, `db_type`, `_db_password`, `mongo_input_mode`, `mongo_raw_uri`.

---

## Test Coverage Targets

| Module                         | Current  | Sprint 9 Target                                    |
| ------------------------------ | -------- | -------------------------------------------------- |
| `src/services/db_connector.py` | ~79%     | ≥ 90% (via US-042 Docker fixture)                  |
| `src/components/sidebar.py`    | excluded | Partially measured via US-040 mock-patched AppTest |
| Overall                        | 93.84%   | ≥ 94%                                              |
