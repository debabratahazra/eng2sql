# TC-005–007: SchemaDetector Service

**User Story**: US-001, US-009
**Service**: `src/services/schema_detector.py` — `SchemaDetector`
**Type**: Unit (TC-005, TC-006) / Integration via SQLite (TC-007)
**Priority**: P0

---

## TC-005: Static YAML Schema Loaded Correctly

### Scenario 1: Valid YAML parsed into TableSchema
```gherkin
Given a valid YAML file at a known path
  | tables:               |
  |   users:              |
  |     - name: id        |
  |       type: INT       |
  |       nullable: false |
  |       primary_key: true |
When load_static_schema(path) is called
Then it returns a dict with key "users"
And schema["users"] has length 3
And schema["users"][0].name == "id"
And schema["users"][0].type == "INT"
And schema["users"][0].nullable is False
And schema["users"][0].primary_key is True
```
**Expected**: `TableSchema` with correct `SchemaColumn` objects for every column
**Test Data**: `valid_schema_yaml` fixture (tmp_path YAML with `users` + `posts`)

### Scenario 2: Column attributes default correctly
```gherkin
Given a YAML column definition with only "name" and "type" specified
When load_static_schema(path) is called
Then column.nullable is True  (default)
And column.primary_key is False  (default)
And column.default is None  (default)
```
**Expected**: `SchemaColumn(name="x", type="TEXT", nullable=True, primary_key=False, default=None)`

### Scenario 3: Empty tables dict returns empty schema
```gherkin
Given a YAML file containing {"tables": {}}
When load_static_schema(path) is called
Then it returns {}
```
**Expected**: `{}` — no error, no tables

### Edge Cases
- YAML with numeric column types (e.g. type: `123`) → cast to `str` → no error
- YAML with `default:` value set → `SchemaColumn.default` populated as string
- YAML with multiple tables → all tables present in returned dict

---

## TC-006: Static Schema File Errors Handled

### Scenario 1: File not found
```gherkin
Given no file exists at "/nonexistent/path/schema.yaml"
When load_static_schema("/nonexistent/path/schema.yaml") is called
Then FileNotFoundError is raised
And the error message contains "not found"
```
**Expected**: `FileNotFoundError("Schema config file not found: /nonexistent/...")`

### Scenario 2: Malformed YAML syntax
```gherkin
Given a file whose contents are invalid YAML ("tables: [this: is: not: valid")
When load_static_schema(path) is called
Then SchemaDetectionError is raised
And the error message references the file path
```
**Expected**: `SchemaDetectionError("Failed to parse schema YAML at ...")`

### Scenario 3: Missing top-level "tables" key
```gherkin
Given a valid YAML file that uses "schema" instead of "tables" as the root key
When load_static_schema(path) is called
Then SchemaDetectionError is raised
And the error message contains "'tables' key"
```
**Expected**: `SchemaDetectionError("... must have a top-level 'tables' key.")`

### Edge Cases
- File exists but is empty (`""`) → YAML parses to `None` → `SchemaDetectionError`
- File is valid YAML but `tables` value is a list not a dict → `SchemaDetectionError`

---

## TC-007: Live Schema Auto-Detection

### Scenario 1: Tables and columns detected correctly
```gherkin
Given a connected SQLite engine with tables "customers" and "orders"
When detect_live_schema(engine) is called
Then it returns a TableSchema containing both tables
And schema["customers"] includes columns "id", "name", "email"
And schema["orders"] includes columns "id", "customer_id", "total", "status", "created_at"
```
**Expected**: `TableSchema` with correct column lists matching the SQLite DDL
**Test Data**: `sqlite_engine` session-scoped fixture (in-memory SQLite)

### Scenario 2: Primary key detected
```gherkin
Given the "customers" table has "id" defined as PRIMARY KEY
When detect_live_schema(engine) is called
Then schema["customers"][0].primary_key is True for the "id" column
```
**Expected**: `id_col.primary_key == True`

### Scenario 3: Empty database returns empty schema
```gherkin
Given a connected SQLite engine with no tables
When detect_live_schema(engine) is called
Then it returns {}
```
**Expected**: `{}` — no error

### Edge Cases
- Table exists but has no columns (edge DDL) → `SchemaDetectionError` propagated
- Engine is disconnected / dead → `SchemaDetectionError` wrapping the `SQLAlchemyError`

---

## Pytest Implementation

**Files**:
- `tests/unit/test_schema_detector.py` ✅ **Implemented (11 tests passing)**
- Uses `sqlite_engine` from `tests/conftest.py` for TC-007 integration scenarios

| Scenario           | Test method                                                        |
| ------------------ | ------------------------------------------------------------------ |
| TC-005 Sc-1        | `TestLoadStaticSchema::test_loads_valid_schema_yaml`               |
| TC-005 Sc-1 detail | `TestLoadStaticSchema::test_column_attributes_correct`             |
| TC-005 Sc-2        | `TestLoadStaticSchema::test_nullable_defaults_to_true`             |
| TC-005 Sc-3        | `TestLoadStaticSchema::test_returns_empty_schema_for_empty_tables` |
| TC-006 Sc-1        | `TestLoadStaticSchema::test_raises_file_not_found`                 |
| TC-006 Sc-2        | `TestLoadStaticSchema::test_raises_on_malformed_yaml`              |
| TC-006 Sc-3        | `TestLoadStaticSchema::test_raises_on_missing_tables_key`          |
| TC-007 Sc-1        | `TestDetectLiveSchema::test_returns_tables_from_sqlite_engine`     |
| TC-007 Sc-1 detail | `TestDetectLiveSchema::test_column_names_correct`                  |
| TC-007 Sc-2        | `TestDetectLiveSchema::test_primary_key_detected`                  |
| TC-007 Sc-3        | `TestDetectLiveSchema::test_empty_database_returns_empty_schema`   |
