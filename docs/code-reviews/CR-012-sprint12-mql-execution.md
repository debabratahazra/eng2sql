# CR-012 — Sprint 12 Code Review: MQL Query Execution (EPIC-010)

**Sprint**: 12
**Reviewer**: Code Reviewer Agent
**Date**: 2026-05-07
**Status**: ✅ Approved

---

## Files Reviewed

| File                                       | Change Type        | Lines                          |
| ------------------------------------------ | ------------------ | ------------------------------ |
| `src/services/mongo_query_executor.py`     | NEW                | 190                            |
| `src/services/sql_generator.py`            | Modified           | +15 dialect-tip lines          |
| `src/components/sql_output.py`             | Modified           | +10 label/lang lines           |
| `src/app.py`                               | Modified           | +12 import + Execute MQL block |
| `src/services/mongo_connector.py`          | Modified (BUG-007) | +12                            |
| `src/services/mongo_schema_detector.py`    | Modified (BUG-008) | +18                            |
| `tests/unit/test_mongo_query_executor.py`  | NEW                | 205                            |
| `tests/unit/test_sql_output_label.py`      | NEW                | 100                            |
| `tests/unit/test_mongo_connector.py`       | Extended (BUG-007) | +8 tests                       |
| `tests/unit/test_mongo_schema_detector.py` | Extended (BUG-008) | +7 tests                       |
| `tests/smoke/test_sprint_11_smoke.py`      | NEW                | 130                            |
| `pyproject.toml`                           | Modified           | smoke marker + addopts         |

---

## Review Checklist

### Correctness

- [x] `MongoQueryExecutor.execute()` path: JSON parse → validate collection → validate pipeline → auto-limit → aggregate → DataFrame. All branches tested.
- [x] `_needs_auto_limit()` correctly identifies terminal stages (`$limit`, `$count`, `$group`, `$facet`, `$bucketAuto`, `$bucket`).
- [x] Auto-limit creates a *copy* of the pipeline list (`[*pipeline, …]`) — original caller list is never mutated.
- [x] ObjectId / BSON type coercion: `isinstance` guard uses `(str, int, float, bool, type(None))`; anything else becomes `str(value)` — correct and safe.
- [x] `sql_output.py` `render()` backward-compat: default `db_type="MySQL"` leaves all existing callers unaffected.
- [x] `app.py` Execute MQL block: guards `mongo_db is not None` before creating executor — no NoneType access.
- [x] BUG-007 fix: `_is_multi_host()` strips credentials from netloc before checking for comma — correct for `user:pass@h1:27017,h2:27017` URIs.
- [x] BUG-008 fix: `system.` pre-filter runs before the loop; per-collection auth guard uses `continue` not `raise` — correct two-layer defence.

### Security

- [x] **No `eval()` or `exec()`** anywhere in `MongoQueryExecutor` — `json.loads()` only. OWASP A03 (Injection) requirement met.
- [x] Collection name validated against `_SAFE_COLLECTION_RE = r"^[a-zA-Z0-9_.\-]+$"` before being passed to pymongo — prevents collection-name injection.
- [x] Auto-limit caps at 1 000 documents — prevents unbounded result-set exfiltration.
- [x] `_UNAUTHORIZED_MARKERS` in schema detector checked by substring match, not broad exception swallow — still raises on unexpected errors.
- [x] No new secrets or credentials introduced in any file.

### Style & Standards

- [x] `from __future__ import annotations` present in all new/modified Python files.
- [x] Full type hints on all public functions and class methods.
- [x] Google-style docstrings on module, class, and all public methods.
- [x] `ruff` compliant — no `ANN` violations on changed lines.
- [x] Logger uses `%`-style placeholders (not f-strings in `logging.debug/info`).
- [x] Module-level constants follow `UPPER_SNAKE_CASE` convention.

### Tests

- [x] 30 tests for `MongoQueryExecutor` with 100 % line coverage.
- [x] 9 tests for `SQLOutputComponent` dynamic label (all branches covered).
- [x] 8 BUG-007 regression tests; 7 BUG-008 regression tests.
- [x] 10 Sprint-11 smoke tests all pass.
- [x] Total unit suite: 238 passed / 0 failed.
- [x] Coverage gate (≥ 80 % overall, ≥ 90 % new module) satisfied.

### Documentation

- [x] `mongo_query_executor.py` module docstring documents the security contract.
- [x] `sql_output.py` docstring updated with `db_type` parameter description.
- [x] `app.py` inline comments explain the MongoDB execute block.

---

## Issues Found and Resolved Inline

| #   | File                                  | Issue                                                                                                                                            | Resolution                                                                   |
| --- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| 1   | `tests/smoke/test_sprint_11_smoke.py` | Injected `detected_schema` as plain `dict[str, list[str]]` — caused `AttributeError: 'str' object has no attribute 'name'` in `schema_viewer.py` | Fixed: use `SchemaColumn` dataclass instances                                |
| 2   | `pyproject.toml`                      | `addopts` did not exclude `smoke` tests                                                                                                          | Fixed: updated to `-m 'not integration and not smoke'`; `smoke` marker added |

---

## Outstanding Notes (Sprint 13 backlog)

- US-051 (`RelationalConnectorSidebar` mixin) deferred from Sprint 11 — sidebar.py remains ~600 LoC.
- US-054 (`pyproject.toml` optional deps) deferred from Sprint 11.
- No integration test for MQL execution path (requires live MongoDB connection) — ITR document covers justification.

---

**Decision**: ✅ **APPROVED** — All Sprint 12 user stories and bug fixes meet the DoD. Code quality, security, and coverage gates all satisfied.
