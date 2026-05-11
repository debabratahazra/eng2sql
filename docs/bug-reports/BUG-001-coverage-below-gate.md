# BUG-001: Coverage Below 80% Gate — UI Components Untested

**Severity**: High
**Sprint**: Sprint 1
**Status**: ✅ Fixed (resolved Sprint 3 — coverage reached 91% via Streamlit AppTest UI tests; current 93.97% as of Sprint 9)
**Reported By**: Tester Agent
**Assigned To**: Developer Agent (Sprint 3)
**Linked Test Result**: TR-001 (filed) / TR-003 (resolved) / TR-009 (current 93.97%)
**Linked Test Cases**: TC-005–010 + TC-038/039 (AppTest)

---

## Description

The project's coverage gate (`--cov-fail-under=80` in `pyproject.toml`) fails when
running the full test suite. Total combined coverage is **45%** against a required
**80%**. The entire shortfall comes from the Streamlit UI layer:

| Module                               | Coverage |
| ------------------------------------ | -------- |
| `src/app.py`                         | 0%       |
| `src/components/progress_tracker.py` | 0%       |
| `src/components/query_input.py`      | 0%       |
| `src/components/schema_viewer.py`    | 0%       |
| `src/components/sidebar.py`          | 0%       |
| `src/components/sql_output.py`       | 0%       |

Services and utilities are well-covered (90–100%); the gap is exclusively in the
Streamlit rendering layer.

---

## Steps to Reproduce

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

Observe: `FAIL Required test coverage of 80.0% not reached. Total coverage: 45.00%`

---

## Expected Behaviour

`pytest --cov=src` exits with code 0 and reports ≥ 80% total coverage.

## Actual Behaviour

`pytest` exits with code 1:
```
FAIL Required test coverage of 80.0% not reached. Total coverage: 45.00%
```

---

## Root Cause

Streamlit components use `st.*` calls at module level and in `render()` methods that
require a running Streamlit server context. Standard `pytest` cannot import and execute
these without a Streamlit `AppTest` harness or heavy mocking of `st.*`.

No Streamlit component tests were written in Sprint 1 because the `AppTest` harness
work was deferred to Sprint 3 (QA epic).

---

## Proposed Fix

In Sprint 3, add tests using `streamlit.testing.v1.AppTest`:

```python
from streamlit.testing.v1 import AppTest

def test_app_loads():
    at = AppTest.from_file("src/app.py")
    at.run()
    assert not at.exception
    assert at.title[0].value == "🗄️ Eng2SQL — English to SQL Generator"
```

Alternatively, exclude UI components from the coverage gate and enforce 80% on
`src/services/` and `src/models/` only via `pyproject.toml` `omit` config.

---

## Workaround

Run coverage only on services layer to confirm service-level quality:

```bash
pytest tests/ --cov=src/services --cov=src/models --cov=src/utils --cov-report=term-missing
```

Expected: ~90% coverage on the service layer.

---

## Priority Justification

Marked **High** (not Critical) because:
- All 38 tests pass — no functional regression
- Service logic (the core value) is 90–100% covered
- The gap is a tooling/test-harness gap, not a code quality gap
- Sprint 3 QA epic is specifically scoped to address this
