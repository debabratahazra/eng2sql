# US-061 — `MongoQueryExecutor` Live Docker Integration Test

**Sprint**: Sprint 13
**Source**: SPRINT-12-retro.md "What Could Be Improved" §1
**Points**: 3
**Owner**: Integration Test Agent

## User Story

As a **QA engineer**, I want a live Docker-based integration test that runs
`MongoQueryExecutor.execute()` against a real `mongod` container so that the
end-to-end MQL execution path is verified beyond mock coverage.

## Acceptance Criteria

1. A new test file `tests/integration/test_mongo_query_executor_integration.py`
   is created tagged `@pytest.mark.docker`.
2. The test seeds a test collection, runs `execute()` with a real pymongo database
   object, and asserts the returned `pd.DataFrame` contains the expected rows.
3. The test covers: happy path, empty pipeline (auto-limit applied), collection not
   found (expects `QueryExecutionError`).
4. The test is skipped automatically when Docker / mongod is not available.
5. CI `coverage-docker` job picks up the new test file automatically.

## Definition of Done

- [x] Integration test file created in `tests/integration/`
- [x] Tests pass against `mongo:latest` Docker container (skip cleanly; CI-ready)
- [x] Tests skip cleanly when Docker unavailable
- [x] ITR doc created in `docs/test-results/` (ITR-005)
- [x] `docs/guides/developer-guide.md` updated with integration test instructions

## Status

✅ Done
