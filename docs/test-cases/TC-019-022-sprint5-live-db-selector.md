# Test Cases — TC-019: Live DB Database Selector (Sprint 5)

**Epic**: EPIC-006
**Sprint**: Sprint 5
**Stories**: US-021, US-022, US-023, US-024
**Test Case Writer**: Test Case Writer Agent
**Date**: 2026-05-02

---

## TC-019: `DBConnector.list_databases()` Unit Tests (US-024)

### TC-019-01: System databases are excluded

```gherkin
Given a mock engine returning rows:
  [("information_schema",), ("performance_schema",), ("mysql",), ("sys",),
   ("myapp_db",), ("analytics_db",)]
When list_databases(engine) is called
Then "information_schema", "performance_schema", "mysql", "sys" are NOT in the result
And "myapp_db" and "analytics_db" ARE in the result
```

### TC-019-02: Non-system databases are returned

```gherkin
Given a mock engine returning [("information_schema",), ("myapp_db",), ("analytics_db",)]
When list_databases(engine) is called
Then the result contains ["analytics_db", "myapp_db"]
```

### TC-019-03: Results are sorted alphabetically

```gherkin
Given a mock engine returning [("zebra_db",), ("alpha_db",), ("mysql",), ("middle_db",)]
When list_databases(engine) is called
Then the result is ["alpha_db", "middle_db", "zebra_db"]
```

### TC-019-04: Empty list when only system databases visible

```gherkin
Given a mock engine returning only system database rows
When list_databases(engine) is called
Then the result is []
And no exception is raised
```

### TC-019-05: Empty list for empty SHOW DATABASES result

```gherkin
Given a mock engine returning []
When list_databases(engine) is called
Then the result is []
```

### TC-019-06: Single user database returned correctly

```gherkin
Given a mock engine returning [("information_schema",), ("my_only_db",)]
When list_databases(engine) is called
Then the result is ["my_only_db"]
```

### TC-019-07: SQLAlchemyError wrapped as DatabaseConnectionError

```gherkin
Given a mock engine whose execute() raises SQLAlchemyError("connection refused")
When list_databases(engine) is called
Then DatabaseConnectionError is raised
And the message matches "Failed to list databases"
```

### TC-019-08: Error message contains original cause

```gherkin
Given a mock engine whose execute() raises SQLAlchemyError("Access denied")
When list_databases(engine) is called
Then DatabaseConnectionError is raised
And the message contains "Access denied"
```

---

## TC-020: Remove Static Schema Mode (US-021)

### TC-020-01: `mode` session key is absent

```gherkin
Given the application starts fresh
When _initialise_session_state() is called
Then "mode" is NOT in st.session_state
```

### TC-020-02: No static schema loading path in app.py

```gherkin
Given a fresh session with no detected_schema
When question is submitted
Then the app shows "⚠️ Please connect to a database and select it in the sidebar first."
And load_static_schema() is NOT called
```

### TC-020-03: SQL generation uses detected_schema from session state

```gherkin
Given st.session_state["detected_schema"] is pre-populated
When a question is submitted
Then generate_sql() is called with the pre-populated schema
And no file I/O occurs during generation
```

---

## TC-021: Step 1 — Server Connect & Database Discovery (US-022)

### TC-021-01: Successful connect populates session state

```gherkin
Given valid host, port, user, password
And a mock that returns ["myapp_db", "analytics_db"] from list_databases()
When _render_step1() executes the Connect logic
Then st.session_state["db_server_engine"] is set (not None)
And st.session_state["available_databases"] == ["myapp_db", "analytics_db"]
And st.session_state["step1_status"] == ("success", "✅ Connected to … — 2 databases found")
```

### TC-021-02: Incomplete form shows warning

```gherkin
Given host is filled but password is empty
When Connect is clicked
Then step1_status is set to ("warning", "Please fill in host, user and password.")
And db_server_engine remains None
```

### TC-021-03: Failed connection stores error status

```gherkin
Given a mock connector.create_engine() that raises DatabaseConnectionError("Access denied")
When Connect is clicked
Then step1_status is ("error", "Connection failed: Access denied …")
And db_server_engine is None
```

### TC-021-04: Connect clears downstream state

```gherkin
Given a previously selected database "old_db" in session state
When Connect is clicked again
Then selected_database, db_engine, detected_schema, available_databases are all removed
```

---

## TC-022: Step 2 — Database Selector & Engine Activation (US-023)

### TC-022-01: Step 2 hidden if Step 1 not complete

```gherkin
Given st.session_state["db_server_engine"] is None
When _render_step2() is called
Then no selectbox or Select Database button is rendered
```

### TC-022-02: No-databases warning shown

```gherkin
Given st.session_state["available_databases"] == []
And st.session_state["db_server_engine"] is set
When _render_step2() is called
Then st.warning("⚠️ No accessible databases found for this user") is shown
```

### TC-022-03: Successful database selection activates engine

```gherkin
Given available_databases == ["myapp_db", "analytics_db"]
And select "myapp_db" and click Select Database
Then db_engine is set to the new engine
And selected_database == "myapp_db"
And detected_schema is populated
And step2_status is ("success", "✅ Using database: myapp_db")
```

### TC-022-04: Missing password shows credential expiry warning

```gherkin
Given _db_password is absent from session state
When Select Database is clicked
Then step2_status is ("warning", "Session credentials expired — please reconnect in Step 1.")
```
