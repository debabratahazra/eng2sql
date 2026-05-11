# US-062 — `app.py` Execute MQL Unit Tests

**Sprint**: Sprint 13
**Source**: SPRINT-12-retro.md "What Could Be Improved" §5
**Points**: 2
**Owner**: Unit Test Agent

## User Story

As a **developer**, I want isolated unit tests for the Execute MQL paths in `app.py`
so that the button logic, error handling, and info-box fallback are covered by fast
unit tests in addition to smoke tests.

## Acceptance Criteria

1. A new test file `tests/unit/test_app_mql_button.py` is created.
2. Tests cover:
   - Execute MQL button click with mocked `MongoQueryExecutor.execute` → success → `query_result` stored
   - Execute MQL button click → `QueryExecutionError` raised → `st.error` called
   - Info-box path: MongoDB mode + MQL generated + `mongo_db` is None → `st.info` called
3. Tests do NOT use Streamlit `AppTest` (that is smoke scope) — use `unittest.mock.patch` on `streamlit` calls.
4. All 3 paths have 100 % line coverage on the new test file.
5. No existing tests broken.

## Definition of Done

- [x] `test_app_mql_button.py` created with ≥ 3 test scenarios
- [x] All tests pass
- [x] Coverage on the Execute MQL paths in `app.py` improved
- [x] UTR document created in `docs/test-results/` (UTR-003)
- [x] Code review approved (CR-013)

## Status

✅ Done
