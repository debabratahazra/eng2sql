# Test Cases TC-058 to TC-065 — Sprint 12: MQL Query Execution (EPIC-010)

**Sprint**: 12
**Author**: Test Case Writer Agent
**Date**: 2026-05-07
**Coverage**: US-057, US-058, US-059, US-060, BUG-007, BUG-008

---

## TC-058 — Dynamic Output Label: MongoDB shows "Generated MQL"

**Story**: US-057
**Type**: Unit (BDD)

**Given** the SQL output component is rendered with `db_type="MongoDB"`
**When** the component's `render()` method is called
**Then** the subheader text contains "Generated MQL" (not "Generated SQL")
**And** the `st.code()` block uses `language="json"`
**And** the placeholder info text mentions "MQL"

**Test**: `tests/unit/test_sql_output_label.py::TestSQLOutputComponentLabel::test_mongodb_shows_generated_mql_subheader`
**Status**: ✅ PASS

---

## TC-059 — Dynamic Output Label: MySQL/PostgreSQL shows "Generated SQL"

**Story**: US-057
**Type**: Unit (BDD)

**Given** the SQL output component is rendered with `db_type="MySQL"` (default)
**When** the component's `render()` method is called
**Then** the subheader text contains "Generated SQL"
**And** `st.code()` uses `language="sql"`
**And** the same behaviour applies for `db_type="PostgreSQL"`
**And** the same behaviour applies when `db_type` is omitted (backward compatibility)

**Test**: `tests/unit/test_sql_output_label.py` — 5 SQL-label tests
**Status**: ✅ PASS

---

## TC-060 — MongoDB LLM Prompt Includes Structured-JSON MQL Instructions

**Story**: US-058
**Type**: Unit (BDD)

**Given** `SQLGenerator.generate_sql()` is called with `dialect="MongoDB"`
**When** the system prompt is assembled
**Then** the prompt contains instructions to return a JSON object with "collection" and "pipeline" keys
**And** an example pipeline is included in the instructions
**And** JavaScript shell syntax (`db.collection.aggregate(…)`) is explicitly prohibited

**Test**: `tests/unit/test_sql_generator.py` — MongoDB dialect tip assertions
**Status**: ✅ PASS

---

## TC-061 — MongoQueryExecutor: Happy Path Returns DataFrame

**Story**: US-059
**Type**: Unit (BDD)

**Given** a mocked pymongo database returning `[{"_id": 1, "name": "Alice"}]`
**And** a valid MQL JSON string `{"collection": "users", "pipeline": [{"$limit": 10}]}`
**When** `MongoQueryExecutor().execute(db, mql_json)` is called
**Then** the result is a `pd.DataFrame`
**And** the DataFrame columns match `{"_id", "name"}`
**And** no exception is raised

**Test**: `tests/unit/test_mongo_query_executor.py::TestMongoQueryExecutorHappyPath::test_returns_dataframe`
**Status**: ✅ PASS

---

## TC-062 — MongoQueryExecutor: Auto-limit Appended

**Story**: US-059
**Type**: Unit (BDD)

**Given** a pipeline with no terminal stage (only `$match`)
**When** `MongoQueryExecutor().execute()` is called
**Then** `{"$limit": 1000}` is appended to the pipeline before `aggregate()` is called
**And** if the pipeline already ends with `$limit`, no second `$limit` is added

**Test**: `tests/unit/test_mongo_query_executor.py::TestMongoQueryExecutorHappyPath::test_auto_limit_appended_when_missing` and `test_existing_limit_not_doubled`
**Status**: ✅ PASS

---

## TC-063 — MongoQueryExecutor: Invalid Input Raises QueryExecutionError

**Story**: US-059
**Type**: Unit (BDD)

**Given** an MQL string that is (a) not valid JSON, (b) a JSON array, (c) missing "collection", (d) empty collection name, (e) dangerous collection name, or (f) pipeline not a list
**When** `MongoQueryExecutor().execute()` is called
**Then** `QueryExecutionError` is raised with a descriptive message in each case
**And** the error message does NOT expose internal pymongo details

**Tests**: `tests/unit/test_mongo_query_executor.py::TestMongoQueryExecutorErrors` (7 scenarios)
**Status**: ✅ PASS

---

## TC-064 — Execute MQL Button Visible When MongoDB + Schema Connected

**Story**: US-060
**Type**: Smoke / Integration (manual scenario)

**Given** the user has selected "MongoDB" as the DB type in the sidebar
**And** has connected to a MongoDB database and selected a DB (so `mongo_db is not None`)
**And** a MQL query has been generated (so `generated_sql` is non-empty)
**When** the main page renders
**Then** the "▶ Execute MQL" button is visible
**And** clicking the button calls `MongoQueryExecutor().execute(mongo_db, generated_sql)`
**And** on success the results are stored in `session_state["query_result"]` and a rerun triggers
**And** on failure a red `st.error` message is displayed

**Test**: Covered by smoke scenario in `test_sprint_12_smoke.py` (TC-064 manual)
**Status**: 🔲 Pending Sprint 12 smoke run (STR-003)

---

## TC-065 — BUG-007 Regression: Multi-Host URI Does Not Raise ValueError

**Story**: BUG-007
**Type**: Unit (Regression BDD)

**Given** a MongoDB URI in replica-set seed list format: `mongodb://user:pass@h1:27017,h2:27017,h3:27017/db`
**When** `MongoConnector().connect(mongo_config)` is called
**Then** no `ValueError` is raised
**And** `_is_multi_host()` returns True for the URI
**And** `MongoClient` is constructed with the full URI string (not via `_uri_to_kwargs()`)

**Tests**: `tests/unit/test_mongo_connector.py::TestMultiHostURI` (8 tests)
**Status**: ✅ PASS

---

## TC-066 — BUG-008 Regression: system.profile Does Not Abort Schema Detection

**Story**: BUG-008
**Type**: Unit (Regression BDD)

**Given** a MongoDB database that has `system.profile` in its collection list
**And** the user account lacks `dbAdmin` privileges
**When** `MongoSchemaDetector().detect_schema(db)` is called
**Then** `system.profile` is silently skipped (not sampled)
**And** user collections are still processed successfully
**And** no `OperationFailure` propagates to the caller

**Tests**: `tests/unit/test_mongo_schema_detector.py::TestSystemCollectionsAndAuthZ` (7 tests)
**Status**: ✅ PASS
