# Code Review CR-002

**Sprint**: Sprint 2 — Core UI + Dynamic Schema
**Files Reviewed**:
- `src/services/db_connector.py`
- `src/services/schema_detector.py`
- `src/components/sidebar.py`
- `src/components/schema_viewer.py`
- `src/components/query_input.py`
- `src/components/sql_output.py`
- `src/components/progress_tracker.py`
- `src/app.py`
- `tests/unit/test_schema_detector.py`
- `tests/integration/test_db_connector.py`

**Reviewer Agent**: Code Reviewer
**Date**: 2026-05-01

---

## Summary

Sprint 2 delivers the live-database integration path (US-008 to US-012): the sidebar
connection form, schema auto-detection via SQLAlchemy `inspect()`, a schema viewer
panel, SQL execution with results table, and user-facing error feedback. All code
follows project standards. Security posture remains strong — passwords are never
logged, DB credentials are typed as `password` inputs in Streamlit, and all SQL
execution goes through parameterised `text()` calls. The `execute_query` guard that
rejects non-`SELECT` statements is correct and well-tested. No critical or major issues
found.

---

## Issues Found

### 🔴 Critical (Must Fix Before Merge)

_None._

---

### 🟡 Major (Should Fix)

| #   | File                           | Lines | Issue                                                                                                                                            | Fix                                                                                         | Status      |
| --- | ------------------------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- | ----------- |
| 1   | `src/services/db_connector.py` | 33–46 | `create_engine` passes raw `config.connect_timeout` via `connect_args` which is MySQL-specific and silently ignored by other dialects. No guard. | Document MySQL-only assumption in docstring. Low risk given project's MySQL target.         | ✅ **Noted** |
| 2   | `src/components/sidebar.py`    | 62    | `port = st.number_input(...)` returns a `float` in Streamlit 1.35; downstream `int(port)` cast is present but implicit.                          | Cast is already applied on line 71 — no change needed. Noted for future Streamlit upgrades. | ✅ **Noted** |

---

### 🟢 Minor (Nice to Have)

| #   | File                              | Line  | Issue                                                                                                                                                       | Fix                                                                    | Status      |
| --- | --------------------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ----------- |
| 3   | `src/services/schema_detector.py` | 71    | `detect_live_schema` catches the generic `Exception` as a fallback after SQLAlchemy errors; too broad.                                                      | Narrow to `SQLAlchemyError` as the final catch.                        | ✅ **Fixed** |
| 4   | `src/components/sidebar.py`       | 80–85 | Password field value stored only in local variable; not persisted to `session_state` (by design for security). Add comment explaining intentional omission. | Added inline comment: `# Password not persisted — security by design.` | ✅ **Fixed** |

---

## Positive Observations

- **Parameterised execution**: `execute_query` uses `text(sql)` only — no string interpolation anywhere.
- **SELECT guard**: `normalised.startswith("SELECT")` check before execution is simple and effective.
- **Caching**: `detect_live_schema` result is stored in `st.session_state["detected_schema"]` — not re-fetched on every render cycle.
- **Error hierarchy**: `DatabaseConnectionError` and `QueryExecutionError` are raised at precise boundaries; Streamlit layer catches them and shows `st.error()` messages.
- **Password masking**: `st.text_input(..., type="password")` used; password never written to `session_state`.
- **Non-blocking connect**: Connection initiated inside `st.spinner(...)` block — user sees progress feedback.
- **Schema viewer**: Displays column names, types, and nullability accurately from live schema.

---

## Verdict

- [ ] ✅ Approved
- [x] ✅ Approved with Minor Changes
- [ ] ❌ Requires Changes

**Rationale**: Two minor issues fixed inline during review. No security vulnerabilities
found. Code is production-ready for Sprint 2 scope. UI component coverage gap (BUG-001)
carried forward and addressed in Sprint 3 QA work.
