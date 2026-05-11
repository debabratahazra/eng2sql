# TC-067-074 — Sprint 13 Test Cases

**Sprint**: 13
**Source**: Sprint 13 stories (US-051, US-054, US-061, US-062)
**Agent**: Test Case Writer

---

## TC-067 — Execute MQL Button: renders when `mongo_db` set

**Story**: US-062
**Type**: Unit (Streamlit AppTest)

### Scenario: Execute MQL button present when MongoDB connected

```gherkin
Given the app is running
And  session_state["db_type"] = "MongoDB"
And  session_state["mongo_db"] is a MagicMock Database object
And  session_state["generated_sql"] = '{"collection":"orders","pipeline":[]}'
When  the app renders
Then  a button with key "execute_mql" is visible in the main area
```

**Expected**: `at.button(key="execute_mql")` found in rendered output.

---

## TC-068 — Execute MQL Button: success path stores result

**Story**: US-062
**Type**: Unit (Streamlit AppTest)

### Scenario: Clicking Execute MQL on valid query writes result to session state

```gherkin
Given the app is running with mongo_db and generated_sql set
And  MongoQueryExecutor.execute is mocked to return a 2-row DataFrame
When  the user clicks "Execute MQL"
Then  session_state["query_result"] is the returned DataFrame
```

**Expected**: `at.session_state["query_result"]` is not None after click.

---

## TC-069 — Execute MQL Button: QueryExecutionError shows st.error

**Story**: US-062
**Type**: Unit (Streamlit AppTest)

### Scenario: Execution failure displays error message

```gherkin
Given MongoQueryExecutor.execute raises QueryExecutionError("bad query")
When  the user clicks "Execute MQL"
Then  an st.error element containing "bad query" appears
And   session_state["query_result"] is unchanged (None)
```

**Expected**: `at.error[0].value` contains `"bad query"`.

---

## TC-070 — Execute MQL Button: info box when no DB

**Story**: US-062
**Type**: Unit (Streamlit AppTest)

### Scenario: Info message shown when MongoDB selected but not connected

```gherkin
Given db_type = "MongoDB" and generated_sql is set
And  mongo_db is None (not connected)
When  the app renders
Then  an st.info element containing "Connect" appears
And   no "Execute MQL" button is rendered
```

**Expected**: `at.info[0].value` contains "Connect"; no execute_mql button.

---

## TC-071 — pyproject.toml optional-deps: pip install -e parses correctly

**Story**: US-054
**Type**: Configuration validation

### Scenario: pyproject.toml is valid after adding optional-dependency groups

```gherkin
Given pyproject.toml has a [project] section with [project.optional-dependencies]
When  pytest is invoked (which reads pyproject.toml)
Then  all existing unit tests collect and run without import errors
```

**Expected**: `pytest tests/unit/test_sql_generator.py -q` → 22 passed.

---

## TC-072 — MongoQueryExecutor integration: simple find returns DataFrame

**Story**: US-061
**Type**: Integration (`@pytest.mark.docker`)

### Scenario: Live MongoDB aggregation returns seeded documents

```gherkin
Given a real MongoDB 7 container with "orders" collection (3 documents)
And  a MongoQueryExecutor instance
When  execute(db, '{"collection":"orders","pipeline":[{"$match":{}}]}') is called
Then  a DataFrame with 3 rows is returned
And  "customer", "amount", "status" columns are present
```

**Expected**: `len(df) == 3` and `"customer" in df.columns`.

---

## TC-073 — MongoQueryExecutor integration: empty pipeline auto-limit

**Story**: US-061
**Type**: Integration (`@pytest.mark.docker`)

### Scenario: Empty pipeline triggers auto-limit guard and returns data

```gherkin
Given a real MongoDB container with "sensors" collection (3 documents)
When  execute(db, '{"collection":"sensors","pipeline":[]}') is called
Then  a non-empty DataFrame is returned (all 3 docs — well below 1000 auto-limit)
```

**Expected**: `df.empty is False` and `len(df) == 3`.

---

## TC-074 — sidebar relational mixin: MySQL Step 1 renders (regression)

**Story**: US-051
**Type**: Unit (Streamlit AppTest) — regression guard

### Scenario: MySQL Step 1 form renders correctly after refactor

```gherkin
Given the app is running with db_type = "MySQL"
When  the app renders
Then  a "Connect" button with key "mysql_connect" is present
And   no exception is raised
```

**Expected**: `at.button(key="mysql_connect")` found; `at.exception` is empty.

---

## TC-075 — sidebar relational mixin: PostgreSQL Step 1 renders (regression)

**Story**: US-051
**Type**: Unit (Streamlit AppTest) — regression guard

### Scenario: PostgreSQL Step 1 form renders correctly after refactor

```gherkin
Given the app is running with db_type = "PostgreSQL"
When  the app renders
Then  an SSL mode selectbox with key "pg_sslmode_input" is present
And   a "Connect" button with key "pg_connect" is present
And   no exception is raised
```

**Expected**: `at.selectbox(key="pg_sslmode_input")` found; `at.button(key="pg_connect")` found.
