# Sprint 1 Retrospective

**Sprint**: Sprint 1 — Foundation
**Date**: 2026-05-14
**Facilitator**: Scrum Master

---

## What Went Well

- Full 21-point velocity achieved — all 7 stories delivered
- Corporate OpenAI proxy integration resolved cleanly using `ssl.SSLContext` + `httpx.Client`
- Test coverage reached 91% — well above the 80% gate
- Code review (CR-001) identified and resolved 4 issues before merge:
  - Broad `except` clause narrowed in `app.py`
  - `logger.info` user field downgraded to `debug`
  - `test_generate_sql_success` mock scope fixed
  - httpx `verify=str` deprecation resolved
- Clean separation of concerns: services are fully independent of Streamlit

## What Could Be Improved

- BUG-001 (UI component test coverage) deferred — `AppTest` harness not set up in Sprint 1;
  needs addressing in Sprint 3
- BUG-002 (ResourceWarning: unclosed SQLite engine) was caught late; teardown pattern
  (`yield` fixture with `engine.dispose()`) should be established earlier in future sprints
- Roadmap sprint point totals for Sprint 4 (12 pts) did not match actual story sizing (16 pts);
  roadmap needs updating after story refinement

## Action Items

| Action                                                                        | Owner        | Due                   |
| ----------------------------------------------------------------------------- | ------------ | --------------------- |
| Establish `yield`-based engine fixture in `conftest.py` from Sprint 1 onwards | Developer    | Sprint 1 (done)       |
| Add `AppTest`-based UI tests to Sprint 3 scope                                | Scrum Master | Sprint 3 planning     |
| Update roadmap.md to reflect actual story point totals                        | Scrum Master | Sprint 1 retro (done) |
