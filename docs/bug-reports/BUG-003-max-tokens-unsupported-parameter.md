# BUG-003: `max_tokens` Unsupported Parameter — SQL Generation Fails on Generate SQL

**Severity**: Critical
**Sprint**: Sprint 2 (discovered post-Sprint 4)
**Status**: ✅ Fixed
**Reported By**: User (manual testing)
**Assigned To**: Developer Agent
**Linked Story**: US-002 — OpenAI SQL Generation Service
**Linked Source**: `src/services/sql_generator.py`

---

## Description

Clicking the **Generate SQL** button in the Streamlit UI raises a `SQLGenerationError`
and shows the following error banner:

```
SQL generation failed: Failed to generate SQL — OpenAI API error:
Error code: 400 - {'error': {'message': "Unsupported parameter: 'max_tokens' is not
supported with this model. Use 'max_completion_tokens' instead.",
'type': 'invalid_request_error', 'param': 'max_tokens',
'code': 'unsupported_parameter'}}
```

The application is completely unusable — no SQL is generated for any input.

---

## Steps to Reproduce

1. Start the Streamlit app: `streamlit run src/app.py`
2. Open `http://localhost:8501`
3. Enter any plain-English question (e.g. *"show all customers"*)
4. Click **Generate SQL**
5. Observe the red error banner with the message above

---

## Expected Behaviour

A valid SQL `SELECT` statement is generated and displayed in the SQL output panel.

## Actual Behaviour

OpenAI returns HTTP 400 with `unsupported_parameter` error. The UI shows:

```
SQL generation failed: Failed to generate SQL — OpenAI API error: Error code: 400
```

No SQL is produced.

---

## Root Cause

`src/services/sql_generator.py`, `SQLGenerator.generate_sql()`, lines 138–143:

```python
response = self._client.chat.completions.create(
    model=self._config.model_name,
    messages=[...],
    max_tokens=self._config.max_tokens,   # ← deprecated parameter
    temperature=self._config.temperature,
)
```

The OpenAI API deprecated `max_tokens` for newer models (o-series and GPT-4o variants
released after late 2024). These models require `max_completion_tokens` instead.
Passing `max_tokens` to such a model results in a 400 `unsupported_parameter` error.

**Reference**: [OpenAI API changelog — max_completion_tokens](https://platform.openai.com/docs/api-reference/chat/create#chat-create-max_completion_tokens)

---

## Fix Applied

**File**: `src/services/sql_generator.py`

Replaced `max_tokens` with `max_completion_tokens` in the
`client.chat.completions.create()` call:

```python
# Before
max_tokens=self._config.max_tokens,

# After
max_completion_tokens=self._config.max_tokens,
```

The `AppConfig.max_tokens` field name is kept unchanged (it is an internal config
field, not an API parameter name). Only the kwarg passed to the OpenAI SDK is updated.

---

## Verification

After applying the fix:

1. `streamlit run src/app.py` — enter any question → SQL is generated correctly.
2. `pytest tests/ -q --cov=src` — all 38 tests pass, 91% coverage maintained.
3. The mock in `tests/unit/test_sql_generator.py` is updated to match the new kwarg.

---

## Affected Versions

| Component  | Version                                  |
| ---------- | ---------------------------------------- |
| openai SDK | ≥ 1.30 (models that reject `max_tokens`) |
| Python     | 3.11+                                    |
| Model      | Any o-series or GPT-4o variant post-2024 |
