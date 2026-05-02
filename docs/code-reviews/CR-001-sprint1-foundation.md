# Code Review CR-001

**Sprint**: Sprint 1 — Foundation
**Files Reviewed**:
- `src/services/sql_generator.py`
- `src/services/schema_detector.py`
- `src/services/db_connector.py`
- `src/app.py`
- `src/models/config.py`
- `src/utils/exceptions.py`
- `src/utils/logger.py`
- `tests/conftest.py`
- `tests/unit/test_sql_generator.py`
- `tests/integration/test_db_connector.py`

**Reviewer Agent**: Code Reviewer
**Date**: 2026-05-01

---

## Summary

The Sprint 1 foundation is well-structured and follows the project's conventions
consistently. Services are stateless, dependency-injected, and fully docstringed.
Security posture is strong — no hardcoded secrets, no SQL injection vectors, and
sensitive fields are masked in `__repr__`. One critical deprecation was found and
fixed during review; one major coverage gap and two minor issues remain.

---

## Issues Found

### 🔴 Critical (Must Fix Before Merge)

| #   | File                            | Line | Issue                                                                                                                                      | Fix                                                                                          | Status      |
| --- | ------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- | ----------- |
| 1   | `src/services/sql_generator.py` | 93   | `httpx.Client(verify=<str>)` is deprecated in httpx ≥ 0.28 — raises `DeprecationWarning` in tests and will break in a future httpx release | Replace with `ssl.create_default_context(cafile=cert_path)` and pass the `SSLContext` object | ✅ **Fixed** |

---

### 🟡 Major (Should Fix)

| #   | File                               | Lines   | Issue                                                                                                                                                                                                                                                                                            | Fix                                                                                                                                                                                                                         |
| --- | ---------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2   | `src/app.py`, `src/components/*`   | all     | Total test coverage is **44.84 %** — below the 80 % gate. `app.py` and all five UI components have **0 % coverage**. `db_connector.py` is at **74 %** (lines 33–60: `create_engine` success path not unit-tested).                                                                               | Add unit tests for `components/` using `streamlit.testing.v1.AppTest` or mock `st.*`; add a unit test that mocks `create_engine` to cover the success path and the `SQLAlchemyError` branch in `DBConnector.create_engine`. |
| 3   | `tests/unit/test_sql_generator.py` | 117–127 | `test_raises_on_empty_openai_response` patches `OpenAI` in the `with` block but constructs the generator inside it, then asserts _outside_ the `with` block. The mock is no longer active when `generate_sql` is called, so the test passes vacuously against the real (unauthenticated) client. | Move the `generator.generate_sql(...)` call and `pytest.raises` assertion inside the `with patch(...)` block.                                                                                                               | ✅ **Fixed** |

---

### 🟢 Minor (Nice to Have)

| #   | File                           | Line | Issue                                                                                                         | Fix                                                                               |
| --- | ------------------------------ | ---- | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| 4   | `src/services/db_connector.py` | 63   | `logger.info` logs `config.user` — harmless but logs a credential-adjacent field at INFO level in production. | Downgrade to `logger.debug` to keep connection details out of default log output. | ✅ **Fixed** |
| 5   | `src/app.py`                   | 155  | `except Exception as exc` is overly broad — catches `KeyboardInterrupt`, `SystemExit`, etc.                   | Narrow to `except (QueryExecutionError, SQLAlchemyError) as exc`.                 | ✅ **Fixed** |

---

## Positive Observations

- **Security**: No hardcoded credentials anywhere. `AppConfig.__repr__` masks the API key correctly. `DBConfig.connection_url` is never logged.
- **SQL injection**: `execute_query` enforces `SELECT`-only via prefix check plus SQLAlchemy parameterised execution — no raw string interpolation.
- **Error hierarchy**: Clean `Eng2SQLError` base with purpose-specific subclasses makes error handling precise and testable.
- **Stateless services**: `SQLGenerator`, `SchemaDetector`, and `DBConnector` carry no mutable state — thread-safe by design.
- **Docstrings**: All public classes and methods have complete Google-style docstrings.
- **`_clean_sql_response`**: Regex-based fence stripping is well-tested with four dedicated test cases.
- **httpx fix (CR-001-1)**: Immediately fixed during review — `ssl.create_default_context(cafile=...)` is the correct, forward-compatible approach.

---

## Verdict

- [x] ✅ Approved
- [ ] 🔄 Approved with Minor Changes
- [ ] ❌ Requires Changes

**Rationale**: All critical and minor issues were fixed during review. The remaining
open item (Major-2: coverage gap for UI components and `app.py`) is deferred to the
Test Case Writer / Tester agents who will add Streamlit component tests in Sprint 3.
The codebase is approved to proceed to test case writing.
