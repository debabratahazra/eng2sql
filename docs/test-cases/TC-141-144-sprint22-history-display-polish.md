# TC-141 to TC-144 — Test Cases: Sprint 22 — History Panel Display Polish

**Sprint**: 22  
**Agent**: Test Case Writer  
**Date**: 2026-05-09  
**Story**: US-089

---

## TC-141 — MySQL Badge Display

**Story**: US-089  
**Priority**: High

### Scenario: MySQL history entry displays dolphin badge

```gherkin
Given _db_type_badge is called with "MySQL"
Then the return value equals "🐬 MySQL"
```

**Expected Result**: `_db_type_badge("MySQL") == "🐬 MySQL"`

---

## TC-142 — PostgreSQL Badge Display

**Story**: US-089  
**Priority**: High

### Scenario: PostgreSQL history entry displays elephant badge

```gherkin
Given _db_type_badge is called with "PostgreSQL"
Then the return value equals "🐘 PostgreSQL"
```

**Expected Result**: `_db_type_badge("PostgreSQL") == "🐘 PostgreSQL"`

---

## TC-143 — MongoDB Badge Display

**Story**: US-089  
**Priority**: High

### Scenario: MongoDB history entry displays leaf badge

```gherkin
Given _db_type_badge is called with "MongoDB"
Then the return value equals "🍃 MongoDB"
```

**Expected Result**: `_db_type_badge("MongoDB") == "🍃 MongoDB"`

---

## TC-144 — Unknown Type Fallback

**Story**: US-089  
**Priority**: Medium

### Scenario A: Unknown db_type is returned unchanged

```gherkin
Given _db_type_badge is called with an unrecognised value (e.g. "Oracle")
Then the return value equals the input string unchanged
```

**Expected Result**: `_db_type_badge("Oracle") == "Oracle"`

### Scenario B: Badge appears in render() output

```gherkin
Given query_history.py source
When the source is read
Then the string "_db_type_badge" appears in the render() method body
```

**Expected Result**: `"_db_type_badge"` present in `query_history.py` source.

### Scenario C: Badge is importable from module

```gherkin
Given the components.query_history module
When _db_type_badge is imported
Then no ImportError is raised
```

**Expected Result**: `from components.query_history import _db_type_badge` succeeds.
