# US-075 — Re-enable Component Coverage; Hold ≥ 80% Gate

**Epic**: EPIC-014 — Component Coverage Completion  
**Sprint**: 17  
**Points**: 5  
**Priority**: High  
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** `src/components/*` removed from the coverage `omit` list,
> **so that** the coverage gate measures the full application surface including components.

---

## Acceptance Criteria

- [x] `src/components/*` removed from `pyproject.toml` `[tool.coverage.run]` `omit`
- [x] `pytest --cov` passes with overall coverage ≥ 80%
- [x] `src/app.py` remains excluded (Streamlit entry point, exercised by AppTest only)

---

## Definition of Done

- [x] Code implemented
- [x] All tests pass (no regressions)
- [x] Coverage gate ≥ 80% confirmed
- [ ] Code review approved
- [x] Docs updated
