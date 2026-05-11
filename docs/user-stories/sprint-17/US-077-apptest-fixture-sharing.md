# US-077 — Investigate AppTest Fixture Sharing

**Epic**: EPIC-014 — Component Coverage Completion  
**Sprint**: 17  
**Points**: 2  
**Priority**: Medium  
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** to investigate whether Streamlit `AppTest` instances can be shared across
> tests using `pytest` fixtures (session/module scope),
> **so that** the ~2–3 s per-test startup cost can be reduced for the smoke suite.

---

## Acceptance Criteria

- [x] Investigation completed with findings documented
- [x] If fixture sharing is safe: a `conftest.py` fixture is added and smoke tests refactored
- [x] If unsafe: document why and close story as "not viable"
- [x] Smoke test wall-clock time before/after measured and recorded

---

## Definition of Done

- [x] Investigation completed
- [x] Finding documented in `docs/guides/developer-guide.md`
- [ ] Code review approved (if refactor done)
