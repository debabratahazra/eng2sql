# TC-001–004: SQLGenerator Service

**User Story**: US-002, US-003
**Service**: `src/services/sql_generator.py` — `SQLGenerator`
**Type**: Unit (all OpenAI calls mocked)
**Priority**: P0

---

## TC-001: Valid English Question → Valid SQL

### Scenario 1: Simple SELECT generation
```gherkin
Given a valid AppConfig with a non-empty OPENAI_API_KEY
And a schema containing a "customers" table
When generate_sql("Show all customers", schema) is called
Then the returned string starts with "SELECT"
And the returned string references "customers"
```
**Expected**: `SELECT * FROM customers;` (or equivalent)
**Test Data**: `question="Show all customers"`, `schema={"customers": [...]}`

### Scenario 2: Markdown code fences stripped
```gherkin
Given the OpenAI API returns SQL wrapped in markdown code fences
  | raw response            |
  | ```sql\nSELECT 1;\n```  |
When generate_sql() is called
Then the returned string contains no backtick characters
And the returned string equals "SELECT 1;"
```
**Expected**: `"SELECT 1;"` — no ` ``` ` or `sql` prefix
**Test Data**: mocked `message.content = "```sql\nSELECT 1;\n```"`

### Scenario 3: Empty OpenAI response
```gherkin
Given the OpenAI API returns a choice with empty string content
When generate_sql("Show customers", schema) is called
Then SQLGenerationError is raised
And the error message contains "empty response"
```
**Expected**: `SQLGenerationError("OpenAI returned an empty response.")`

### Edge Cases
- OpenAI returns only whitespace → treated as empty → `SQLGenerationError`
- Response has only code fences with no SQL body → cleaned to `""` → `SQLGenerationError`

---

## TC-002: Schema Context Injected into Prompt

### Scenario 1: All table names present in system message
```gherkin
Given a schema with tables "customers" and "orders"
When generate_sql() is called
Then the system message sent to OpenAI contains the string "customers"
And the system message sent to OpenAI contains the string "orders"
```
**Expected**: `messages[0]["content"]` contains both table names
**Test Data**: `sample_schema` fixture

### Scenario 2: Empty schema rejected before API call
```gherkin
Given an empty schema dict {}
When generate_sql("Show data", {}) is called
Then ValueError is raised
And the error message contains "Schema cannot be empty"
And no OpenAI API call is made
```
**Expected**: `ValueError("Schema cannot be empty — provide at least one table.")`

### Edge Cases
- Schema with a single table → still accepted, table name in prompt
- Column with `primary_key=True` → prompt includes `[PK]` flag
- Column with `nullable=False` → prompt includes `[NOT NULL]` flag

---

## TC-003: OpenAI API Failure → SQLGenerationError

### Scenario 1: API returns HTTP 500
```gherkin
Given the OpenAI API raises OpenAIError("API unavailable")
When generate_sql("Show all customers", schema) is called
Then SQLGenerationError is raised
And the error message contains "OpenAI API error"
And the original OpenAIError is chained as __cause__
```
**Expected**: `SQLGenerationError("Failed to generate SQL — OpenAI API error: ...")`
**Test Data**: `mock_openai_error` fixture (raises `OpenAIError`)

### Scenario 2: API key invalid — ConfigurationError at init
```gherkin
Given an AppConfig with an empty openai_api_key
When SQLGenerator(config) is instantiated
Then ConfigurationError is raised immediately
And the error message contains "OPENAI_API_KEY"
```
**Expected**: `ConfigurationError("OPENAI_API_KEY is not set. Add it to your .env file.")`

### Edge Cases
- Rate-limit error (429) → same path as 500; raises `SQLGenerationError`
- Timeout → caught by `OpenAIError` wrapper → `SQLGenerationError`
- HTTP 400 `unsupported_parameter` (BUG-003) → caught by `OpenAIError` wrapper → `SQLGenerationError`

---

## TC-005 (BUG-003 Regression): `max_completion_tokens` Used in API Call

**Linked Bug**: BUG-003
**Added**: 2026-05-02

### Scenario 1: `max_completion_tokens` kwarg is passed, not `max_tokens`
```gherkin
Given a configured SQLGenerator with max_tokens=500
When generate_sql() is called successfully
Then the OpenAI API was called with kwarg "max_completion_tokens" = 500
And the kwarg "max_tokens" is NOT present in the API call
```
**Expected**: `create.call_args.kwargs["max_completion_tokens"] == 500`
**Test**: `test_uses_max_completion_tokens_not_max_tokens`

### Scenario 2: HTTP 400 `unsupported_parameter` is wrapped as `SQLGenerationError`
```gherkin
Given the OpenAI API raises BadRequestError with code "unsupported_parameter"
When generate_sql() is called
Then SQLGenerationError is raised
And the error message contains "OpenAI API error"
```
**Expected**: `SQLGenerationError("Failed to generate SQL — OpenAI API error: ...")`
**Test**: `test_unsupported_parameter_400_wrapped_as_sql_generation_error`

---

## TC-004: Empty / Invalid Question → ValueError

### Scenario 1: Empty string
```gherkin
Given a valid schema and configured generator
When generate_sql("", schema) is called
Then ValueError is raised
And the error message contains "empty"
```
**Expected**: `ValueError("Question cannot be empty.")`

### Scenario 2: Whitespace-only string
```gherkin
Given a valid schema and configured generator
When generate_sql("   ", schema) is called
Then ValueError is raised
And the error message contains "empty"
```
**Expected**: `ValueError("Question cannot be empty.")` — strip applied before check

### Scenario 3: Single-character question accepted
```gherkin
Given a valid schema and configured generator
When generate_sql("?", schema) is called
Then no ValueError is raised
And the OpenAI API is called
```
**Expected**: no exception at validation layer; API call proceeds

### Edge Cases
- Unicode whitespace (e.g. `"\u00a0"`) → stripped → `ValueError`
- Very long question (> 1000 chars) → accepted; no length limit enforced

---

## Pytest Implementation

**File**: `tests/unit/test_sql_generator.py` ✅ **Implemented (20 tests passing)**

| Scenario          | Test method                                                                  |
| ----------------- | ---------------------------------------------------------------------------- |
| TC-001 Sc-1       | `TestSQLGenerator::test_generates_select_for_simple_question`                |
| TC-001 Sc-2       | `TestSQLGenerator::test_strips_markdown_fences_from_response`                |
| TC-001 Sc-3       | `TestSQLGenerator::test_raises_on_empty_openai_response`                     |
| TC-002 Sc-1       | `TestSQLGenerator::test_schema_context_sent_to_openai`                       |
| TC-002 Sc-2       | `TestSQLGenerator::test_raises_value_error_on_empty_schema`                  |
| TC-003 Sc-1       | `TestSQLGenerator::test_raises_sql_generation_error_on_api_failure`          |
| TC-003 Sc-2       | `TestSQLGenerator::test_raises_configuration_error_if_no_api_key`            |
| TC-004 Sc-1       | `TestSQLGenerator::test_raises_value_error_on_empty_question`                |
| TC-004 Sc-2       | `TestSQLGenerator::test_raises_value_error_on_whitespace_question`           |
| TC-002 helpers    | `TestBuildSchemaContext` (4 tests)                                           |
| TC-001 helpers    | `TestCleanSqlResponse` (4 tests)                                             |
| TC-002 Sc-1 param | `TestSQLGenerator::test_generated_sql_references_schema_entities` (3 params) |
