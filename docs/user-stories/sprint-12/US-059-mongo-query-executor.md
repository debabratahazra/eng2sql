# US-059: MongoQueryExecutor Service

**Epic**: EPIC-009 — MQL Query Execution & Dynamic Output Label
**Sprint**: Sprint 12
**Points**: 5
**Status**: ✅ Done

---

## User Story

> As a developer,
> I want a `MongoQueryExecutor` service that safely parses and executes a structured MQL
> JSON string against a connected pymongo database,
> so that the UI can run MongoDB queries without any `eval()` or shell calls.

---

## Acceptance Criteria

- [ ] `src/services/mongo_query_executor.py` exists with a `MongoQueryExecutor` class.
- [ ] `MongoQueryExecutor.execute(db, mql_json)` accepts:
  - `db`: a `pymongo.database.Database` object.
  - `mql_json`: a string produced by the LLM (raw text, may contain markdown fences).
- [ ] The method strips markdown code fences (```` ```json ``` ````) before parsing.
- [ ] The method parses with `json.loads()` — **no `eval()`**.
- [ ] The method validates the `collection` field against `^[a-zA-Z0-9_.\\-]+$`
  and raises `QueryExecutionError` for invalid names.
- [ ] The method validates that `pipeline` is a list.
- [ ] The method appends `{"$limit": 1000}` when no `$limit`, `$count`,
  `$facet`, `$bucketAuto`, or `$group` stage is present.
- [ ] Results are returned as a `pd.DataFrame` (columns = BSON document keys, `_id` column
  converted to `str`).
- [ ] On any pymongo error, raises `QueryExecutionError` with the collection name and
  the original error message (credentials stripped from any URI in the message).
- [ ] Unit-test coverage ≥ 90%.

---

## Definition of Done

- [x] `src/services/mongo_query_executor.py` implemented.
- [x] `tests/unit/test_mongo_query_executor.py` added (≥ 10 tests).
- [x] All pre-existing tests pass.
- [x] `docs/guides/developer-guide.md` updated.
- [x] Code review approved (CR-012).
- [x] Smoke tests passing (STR-003 scenario 7).
