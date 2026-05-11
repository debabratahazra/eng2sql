# US-076 — AppTest Rendering-Method Tests (Step 2, URI Mode)

**Epic**: EPIC-014 — Component Coverage Completion  
**Sprint**: 17  
**Points**: 3  
**Priority**: High  
**Status**: ✅ Done

---

## User Story

> **As a** developer,
> **I want** AppTest-based tests for `_render_relational_step2`,
> `_render_mongo_step1_uri_mode`, and `_render_mongo_step2`,
> **so that** the rendering paths that cannot be covered by pure-function extraction
> alone are also verified.

---

## Acceptance Criteria

- [x] AppTest tests exercise the Step 2 database-selection flow for MySQL/PostgreSQL
- [x] AppTest tests exercise the MongoDB URI connection mode (Step 1 URI path)
- [x] AppTest tests exercise the MongoDB Step 2 collection/database selection
- [x] All new tests pass without a live database connection (mocked connectors)

---

## Definition of Done

- [x] Code implemented (`tests/unit/test_sidebar_rendering.py`)
- [x] Unit tests written and passing
- [x] UTR document created
- [ ] Code review approved
