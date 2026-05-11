# CR-020 — Sprint 20: Query History & CSV Export Code Review

**Document**: CR-020  
**Sprint**: 20  
**Date**: 2026-05-09  
**Reviewer**: Code Reviewer Agent  
**Status**: ✅ Approved

---

## Scope

Files introduced or modified in Sprint 20:

| File                               | Change                                                                   |
| ---------------------------------- | ------------------------------------------------------------------------ |
| `src/components/query_history.py`  | NEW — US-085 query history component                                     |
| `src/components/csv_export.py`     | NEW — US-086 CSV export component                                        |
| `src/components/query_input.py`    | MOD — added `key="query_text"` to `st.text_area`                         |
| `src/app.py`                       | MOD — imports, session state, history update, history render, CSV render |
| `tests/unit/test_query_history.py` | NEW — 15 unit tests for US-085                                           |
| `tests/unit/test_csv_export.py`    | NEW — 14 unit tests for US-086                                           |

---

## Review Checklist

### Correctness

- [x] `_append_to_history` correctly prepends, deduplicates by question, and caps at
  `max_entries`. Edge cases (empty list, max_entries=1, duplicate) all tested.
- [x] `_truncate` correctly handles short, exact-length, and long strings; Unicode
  characters truncated by character count, not bytes.
- [x] `_result_to_csv` serialises DataFrame without index column; UTF-8 encoding
  preserves Unicode values and correctly quotes comma-containing fields.
- [x] `_export_filename` produces the exact `eng2sql_results_<YYYYMMDD>.csv` pattern.
- [x] `app.py` history update placed after successful SQL generation, before `st.rerun()`.
- [x] `app.py` CSV export renders after `st.dataframe(...)` in the query results block.
- [x] `query_input.py` `key="query_text"` enables Re-use pre-population via
  `st.session_state["query_text"]`.

### Security (OWASP)

- [x] No new user-controlled SQL construction — CSV export operates only on already-
  executed result DataFrames; no injection vectors introduced.
- [x] No secrets or credentials in new files.
- [x] `pandas.DataFrame.to_csv()` is a library call; no shell execution or file writes.
- [x] Download filenames are constructed from `datetime.date.today()` only — no
  user input reaches the filename, preventing path traversal.

### Style & Standards

- [x] `from __future__ import annotations` in all new Python files.
- [x] Full type hints on all public functions and methods.
- [x] Google-style docstrings on every public function, class, and method.
- [x] Module-level docstrings present in both new components.
- [x] PEP 8 compliant (verified by ruff; 0 errors).

### ADR-007 Compliance (Widget Extraction Pattern)

- [x] `query_history.py`: `_append_to_history` and `_truncate` are pure helpers with
  no `st.*` calls. `render()` contains all widget calls and is under `# pragma: no cover`.
- [x] `csv_export.py`: `_result_to_csv` and `_export_filename` are pure helpers.
  `render()` contains all widget calls and is under `# pragma: no cover`.
- [x] Both pragmas have justification in the method docstring within ±5 lines
  (passes `scripts/pragma_audit.py`).

### Test Quality

- [x] 15 tests for US-085 cover all boundary conditions (empty list, max_entries,
  deduplication, mutation safety, ordering, Unicode).
- [x] 14 tests for US-086 cover bytes type, UTF-8, header row, no index, data rows,
  empty DF, Unicode, comma quoting, filename format.
- [x] No mocking of pure helpers — tests use real function calls.
- [x] Total unit suite: 407 tests, 100.00% coverage (962 stmts, 0 miss).

### Documentation

- [x] `docs/guides/user-guide.md` — US-085 and US-086 user-facing features documented.
- [x] `docs/guides/developer-guide.md` — component patterns documented.

---

## Issues Found

None. All new code follows the ADR-007 extraction pattern, full type hints are present,
pure helpers are fully covered, and the pragma audit passes.

---

## Verdict

**✅ Approved — no changes required.**
