# TC-137 to TC-140 — Test Cases: Sprint 21 — Query History UX Polish

**Sprint**: 21  
**Agent**: Test Case Writer  
**Date**: 2026-05-09  
**Stories**: US-087, US-088

---

## TC-137 — db_type Default is MySQL

**Story**: US-087  
**Priority**: High

### Scenario: Default db_type when not supplied

```gherkin
Given the query history is empty
When _append_to_history is called with question="q", sql="SELECT 1" and no db_type argument
Then the resulting entry has db_type equal to "MySQL"
```

**Expected Result**: `result[0]["db_type"] == "MySQL"`

---

## TC-138 — db_type Persisted for MongoDB

**Story**: US-087  
**Priority**: High

### Scenario: MongoDB db_type is stored in history entry

```gherkin
Given the query history is empty
When _append_to_history is called with db_type="MongoDB"
Then the resulting entry has db_type equal to "MongoDB"
And _db_type_to_lang("MongoDB") returns "json"
```

**Expected Result**:
- `result[0]["db_type"] == "MongoDB"`
- `_db_type_to_lang("MongoDB") == "json"`

---

## TC-139 — Language Mapping for SQL Databases

**Story**: US-087  
**Priority**: Medium

### Scenario: Non-MongoDB databases map to sql language token

```gherkin
Given a database type of "MySQL" or "PostgreSQL" or any unknown value
When _db_type_to_lang is called with that value
Then the function returns "sql"
```

**Expected Result**:
- `_db_type_to_lang("MySQL") == "sql"`
- `_db_type_to_lang("PostgreSQL") == "sql"`
- `_db_type_to_lang("Oracle") == "sql"`
- `_db_type_to_lang("") == "sql"`

---

## TC-140 — Clear History Button Present and Functional

**Story**: US-088  
**Priority**: High

### Scenario A: Clear History button string present in source

```gherkin
Given the file src/components/query_history.py
When the file source is read
Then the string "Clear History" appears in the source
```

**Expected Result**: `"Clear History" in source_code`

### Scenario B: Clearing history empties the list

```gherkin
Given a session history with 3 entries
When st.session_state["query_history"] is set to []
Then the history list is empty
And QueryHistoryComponent.render([]) returns without rendering the expander
```

**Expected Result**: Empty list passed to `render()` triggers early return.

### Scenario C: App.py passes db_type to _append_to_history

```gherkin
Given app.py source code
When the _append_to_history call is inspected
Then the call includes the db_type keyword argument
```

**Expected Result**: `"db_type=db_type"` appears in `app.py` source.
