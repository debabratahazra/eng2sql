# Test Cases TC-131 to TC-136 — Sprint 20: Query History & CSV Export

**Sprint**: 20  
**Date**: 2026-05-09  
**Stories**: US-085 (Query History), US-086 (CSV Export)  
**Agent**: Test Case Writer

---

## TC-131 — Query History: Entry Appended After Successful Generation

**Story**: US-085  
**Priority**: High  
**Type**: Unit

### Scenario
```gherkin
Given the session query_history is empty
When a user generates a valid SQL query
Then the history list contains one entry with the question and sql
And the entry is at index 0
```

### Test Steps
1. Call `_append_to_history([], "top customers", "SELECT * FROM customers LIMIT 10")`
2. Assert the returned list has length 1
3. Assert `result[0]["question"] == "top customers"`
4. Assert `result[0]["sql"] == "SELECT * FROM customers LIMIT 10"`

### Expected Result
Single-item list with the new entry at index 0.

---

## TC-132 — Query History: Most-Recent Entry Always at Top

**Story**: US-085  
**Priority**: High  
**Type**: Unit

### Scenario
```gherkin
Given the query_history contains 3 older entries
When a new query is generated successfully
Then the new entry appears at index 0
And the older entries retain their relative order below it
```

### Test Steps
1. Build a history with entries q1, q2, q3 (q1 at index 0)
2. Call `_append_to_history(history, "q_new", "SELECT 99")`
3. Assert `result[0]["question"] == "q_new"`
4. Assert `[h["question"] for h in result[1:]] == ["q1", "q2", "q3"]`

### Expected Result
New entry at top; older entries in original order.

---

## TC-133 — Query History: Capped at 10 Entries

**Story**: US-085  
**Priority**: Medium  
**Type**: Unit

### Scenario
```gherkin
Given the query_history already contains 10 entries
When a new (distinct) query is generated
Then the history still contains exactly 10 entries
And the oldest entry has been dropped
```

### Test Steps
1. Build a history list of 10 distinct entries
2. Call `_append_to_history(history, "q_new", "SELECT 99")`
3. Assert `len(result) == 10`
4. Assert `result[0]["question"] == "q_new"`

### Expected Result
History capped at 10; newest entry at top, oldest dropped.

---

## TC-134 — Query History: Duplicate Question Deduplicated

**Story**: US-085  
**Priority**: Medium  
**Type**: Unit

### Scenario
```gherkin
Given the query_history contains an entry with question "find all orders"
When the user re-submits the exact same question with a new SQL result
Then the old entry is removed
And only one entry with that question exists, at index 0, with the new SQL
```

### Test Steps
1. Build history: `[{"question": "find all orders", "sql": "SELECT 1"}, ...]`
2. Call `_append_to_history(history, "find all orders", "SELECT 2")`
3. Assert `result.count({"question": "find all orders", "sql": "..."}) == 1`
4. Assert `result[0]["sql"] == "SELECT 2"`

### Expected Result
One entry with the question, at top, with updated SQL.

---

## TC-135 — CSV Export: Download Filename Format

**Story**: US-086  
**Priority**: High  
**Type**: Unit

### Scenario
```gherkin
Given a date string "20260509"
When _export_filename("20260509") is called
Then the return value is "eng2sql_results_20260509.csv"
```

### Test Steps
1. Call `_export_filename("20260509")`
2. Assert result equals `"eng2sql_results_20260509.csv"`
3. Assert result starts with `"eng2sql_results_"`
4. Assert result ends with `".csv"`

### Expected Result
`"eng2sql_results_20260509.csv"`

---

## TC-136 — CSV Export: DataFrame Serialised Correctly

**Story**: US-086  
**Priority**: High  
**Type**: Unit

### Scenario
```gherkin
Given a DataFrame with columns "name" and "score" and 2 data rows
When _result_to_csv(df) is called
Then the return value is UTF-8 bytes
And the first line contains "name,score"
And both data rows are present
And there is no index column
```

### Test Steps
1. Create `df = pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 87]})`
2. Call `csv_bytes = _result_to_csv(df)`
3. Assert `isinstance(csv_bytes, bytes)`
4. Decode as UTF-8; assert first line is `"name,score"`
5. Assert `"Alice"` and `"Bob"` appear in the decoded CSV
6. Assert no leading integer index column

### Expected Result
Valid UTF-8 CSV bytes; header row; two data rows; no index.

---

## Test Coverage Matrix

| TC     | Story  | Type | Component Tested     | Status |
| ------ | ------ | ---- | -------------------- | ------ |
| TC-131 | US-085 | Unit | `_append_to_history` | ✅      |
| TC-132 | US-085 | Unit | `_append_to_history` | ✅      |
| TC-133 | US-085 | Unit | `_append_to_history` | ✅      |
| TC-134 | US-085 | Unit | `_append_to_history` | ✅      |
| TC-135 | US-086 | Unit | `_export_filename`   | ✅      |
| TC-136 | US-086 | Unit | `_result_to_csv`     | ✅      |
