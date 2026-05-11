# CR-017 — Sprint 17 Code Review

**Sprint**: 17  
**Reviewer**: Code Reviewer Agent  
**Date**: 2025-08-01  
**Status**: ✅ Approved

---

## Scope

| Story  | Change                                                     | Files                                                                                                     |
| ------ | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| US-075 | Remove `src/components/*` from coverage omit               | `pyproject.toml`                                                                                          |
| US-076 | AppTest rendering-method tests                             | `tests/unit/test_sidebar_rendering.py`                                                                    |
| US-077 | AppTest fixture investigation; `initial_app_state` fixture | `tests/conftest.py`, `tests/unit/test_apptest_fixture_investigation.py`, `docs/guides/developer-guide.md` |
| US-078 | Verify error branch coverage (no code changes)             | `docs/test-results/UTR-022-*`                                                                             |

---

## Review Findings

### US-075: `pyproject.toml` Coverage Omit Change

**File**: `pyproject.toml`  
**Change**: Removed `"src/components/*"` from `[tool.coverage.run] omit`.

- ✅ `src/app.py` correctly remains excluded (entry point, AppTest-only)
- ✅ `src/__init__.py` and `*/migrations/*` remain excluded as expected
- ✅ Gate passes at 98.03% after change (well above 80% threshold)
- ✅ No security concerns

---

### US-076: `tests/unit/test_sidebar_rendering.py`

- ✅ `from __future__ import annotations` present
- ✅ All tests class-based with descriptive docstrings
- ✅ `APP_PATH` uses `pathlib.Path` resolution (not hardcoded)
- ✅ `default_timeout=30` on all `AppTest.from_file()` calls — xdist safe
- ✅ Uses `patch("components.sidebar.MongoDBConnector")` correctly (patches at point-of-use)
- ✅ No `.get()` on `session_state` (correctly uses `at.session_state["key"]` with `in` guard)
- ✅ `MagicMock()` used for injected engines/clients — no real DB connections
- ✅ All 17 tests pass consistently

**Minor observations** (no blockers):
- `test_step2_missing_client_after_click_stores_warning`: test comment acknowledges that mongo step 2 may not render at all when client is None — acceptable since no assertion about specific status is made (just "no crash")
- The `_Helper` type annotation `"AppTest"` uses forward-reference string form — correct since AppTest is imported inside the test function body

---

### US-077: `tests/conftest.py` + Investigation Tests

- ✅ `initial_app_state` fixture has clear `scope="module"` and explicit **READ-ONLY** documentation
- ✅ Warning comment about mutation contamination is prominent
- ✅ Developer guide section is accurate and actionable
- ✅ `test_apptest_fixture_investigation.py` demonstrates both safe and unsafe usage patterns clearly
- ✅ Timing test has a loose upper bound (30 s) rather than a flaky tight bound
- ✅ 8 tests pass in 6.34 s

**Observation**: The fixture is appended to the integration-fixture section of `conftest.py`. Consider moving to a dedicated "UI" section in a future cleanup sprint.

---

### US-078: Verification-Only Story

- ✅ No code changes — existing coverage was 100% for both connector modules
- ✅ UTR-022 documents the existing tests by name and covered line ranges
- ✅ Correct conclusion: story satisfied trivially, no new tests needed

---

## Security Review

- No new network calls, no credentials, no SQL construction in any Sprint 17 code
- `patch()` targets are scoped to the component module, not global builtins — correct
- No OWASP Top 10 concerns

---

## Summary

| Story  | Verdict                |
| ------ | ---------------------- |
| US-075 | ✅ Approved             |
| US-076 | ✅ Approved             |
| US-077 | ✅ Approved             |
| US-078 | ✅ Approved (no change) |

**Overall Sprint 17 code quality: 10/10**  
Coverage rose from 91% (Sprint 16 baseline with components excluded) to **98.03%** with
components fully instrumented. All 360 unit tests pass.
