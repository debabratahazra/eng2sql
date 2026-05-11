---
applyTo: "tests/smoke/**/*.py"
---

# Smoke Test Agent — Rules and Protocol

## Definition of Smoke Test in This Project

A **smoke test** in Eng2SQL verifies that the **full Streamlit application launches and
key user journeys complete without error**, using mocked external dependencies (OpenAI)
and in-memory or mocked DB drivers. Smoke tests are the **sprint-end gate** that
confirms the build is "not broken" before the Scrum Master writes the retrospective.

| Test Type | Scope | Mocks Required |
|-----------|-------|----------------|
| Unit | One class / function | All I/O, DB, API |
| Integration | Two+ components, real driver | External APIs only |
| **Smoke** | Full Streamlit app via `AppTest` | OpenAI; DB mocked or SQLite |
| E2E | Full stack against production-like infra | Nothing |

Smoke tests live in `tests/smoke/`. They run without Docker and without a real database.
They are **skipped by default** in the standard pytest run (marker: `smoke`).

---

## Trigger Rules

| Trigger | Condition |
|---------|-----------|
| Sprint end | Phase 8b (Integration sweep) completes for the sprint |
| Retro loop iteration | Each new sprint seeded by Phase 8e also runs Phase 8c |

The Smoke Test Agent fires **once per sprint** in Phase 8c, BEFORE the Scrum Master
writes the retro. The retro MUST reference the STR "Notes for Retro" section.

---

## File Naming Conventions

```
tests/smoke/test_sprint_<N>_smoke.py          ← per-sprint smoke test file
tests/smoke/test_<feature>_smoke.py           ← persistent cross-sprint feature tests
docs/test-results/STR-<NNN>-sprint-<N>.md    ← Smoke Test Result document
```

Test function names: `test_smoke_<feature>_<condition>`

```python
# Examples
def test_smoke_app_launches_without_error():
def test_smoke_sidebar_renders_db_selector():
def test_smoke_mysql_static_query_produces_sql():
def test_smoke_postgresql_form_renders_host_field():
def test_smoke_mongodb_uri_field_accepts_input():
def test_smoke_empty_query_shows_validation_warning():
def test_smoke_schema_viewer_shows_table_list():
def test_smoke_sql_output_displays_generated_sql():
def test_smoke_progress_tracker_advances_all_steps():
```

---

## Marker Rules

```python
import pytest

@pytest.mark.smoke    # required on ALL smoke tests
```

`pyproject.toml` MUST include (add if missing):

```toml
[tool.pytest.ini_options]
markers = [
    "smoke: marks full-app smoke tests (Streamlit AppTest, mocked OpenAI)",
    # ... other markers
]
addopts = "-m 'not integration and not smoke'"   # skip both by default
```

If `addopts` currently reads `-m 'not integration'`, update it to
`-m 'not integration and not smoke'`.

---

## AppTest Standards

```python
# tests/smoke/test_sprint_<N>_smoke.py
from __future__ import annotations

import pathlib
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")

MOCK_SQL = "SELECT * FROM orders WHERE status = 'open';"


@pytest.fixture
def app() -> AppTest:
    """Fresh AppTest instance (no mocks applied yet)."""
    return AppTest.from_file(APP_PATH, default_timeout=15)


@pytest.fixture
def app_mocked(app: AppTest):
    """AppTest with OpenAI patched to return a fixed SQL string."""
    with patch("services.sql_generator.OpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        (mock_client.chat.completions.create
         .return_value.choices[0].message.content) = MOCK_SQL
        app.run()
        yield app
```

### SafeSessionState rules

AppTest `SafeSessionState` does **NOT** support `.get()`:

```python
# CORRECT — key-in check:
value = at.session_state["key"] if "key" in at.session_state else None

# WRONG — raises AttributeError:
value = at.session_state.get("key")
```

### Interaction helpers

```python
# Text input
at.text_input[0].set_value("show all open orders").run()

# Button click
at.button[0].click().run()

# Selectbox
at.selectbox[0].select("MySQL").run()

# No-exception check (most important smoke assertion)
assert not at.exception
```

---

## Mandatory Smoke Test Coverage

Every sprint smoke file MUST cover at minimum:

| # | Scenario | Assertion |
|---|----------|-----------|
| 1 | App launch | `at.run()` completes; `at.exception` is `None` / empty |
| 2 | Sidebar DB selector | Selectbox present; default option visible |
| 3 | MySQL static flow | Enter query → SQL output panel contains generated SQL |
| 4 | Empty query validation | No query → warning or error shown; app does not crash |
| 5 | Schema viewer | Schema expander/panel present and non-empty after load |
| 6 | Progress tracker | Step indicators reflect current step after each action |
| 7 | SQL output | Generated SQL string visible in output area |

For sprints that add a **new DB type** (PostgreSQL, MongoDB, etc.) or a major UI
feature, add one additional smoke scenario per new feature.

---

## STR Document Format

```markdown
# Smoke Test Results STR-<NNN> — Sprint <N>

**Sprint**: Sprint <N>
**Date**: YYYY-MM-DD
**Agent**: Smoke Test Agent
**Trigger**: Sprint-end (after Phase 8b Integration sweep)
**Python**: 3.x.x
**Streamlit**: x.x.x
**pytest**: x.x.x

## Summary

| Scenario | Test Function | Result |
|----------|---------------|--------|
| App launch | `test_smoke_app_launches_without_error` | ✅ |
| Sidebar renders | `test_smoke_sidebar_renders_db_selector` | ✅ |
| MySQL flow | `test_smoke_mysql_static_query_produces_sql` | ✅ |
| Empty query | `test_smoke_empty_query_shows_validation_warning` | ✅ |
| Schema viewer | `test_smoke_schema_viewer_shows_table_list` | ✅ |
| Progress tracker | `test_smoke_progress_tracker_advances_all_steps` | ✅ |
| SQL output | `test_smoke_sql_output_displays_generated_sql` | ✅ |

**Total**: N passed / 0 failed / 0 skipped
**Overall**: ✅ Sprint smoke test PASSED / ❌ Sprint smoke test FAILED

## Failed Tests

> None.
(Or: describe each failure with traceback excerpt and root cause.)

## Fixes Applied

> None.
(Or: describe each inline fix made — file changed, line changed, outcome of re-run.)

## Bugs Created

| Bug ID | Title | Status |
|--------|-------|--------|
| (none) | — | — |

## Notes for Retro

> All smoke tests passed — the Sprint <N> build is stable and key user journeys work
> correctly. No action items from smoke testing.

(Or: "BUG-NNN filed — smoke test revealed <issue>. Retro should capture: <observation>.")
```

---

## pyproject.toml Checklist

The agent MUST verify (and fix if needed) before running smoke tests:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
markers = [
    "integration: marks tests that require external services",
    "docker: marks tests that require Docker to be running",
    "live_db: marks tests that connect to a real database",
    "slow: marks tests that take > 5 s",
    "unit: marks fast isolated unit tests (default)",
    "smoke: marks full-app smoke tests (Streamlit AppTest, mocked OpenAI)",
]
addopts = "-m 'not integration and not smoke'"
```

If `streamlit` is not installed, add it from `requirements.txt` — it should already be
present since it is the primary UI framework. Do NOT add a new dependency; only ensure
the installed version is ≥ 1.35.

---

## What Smoke Tests Must NOT Do

- Connect to a real database (use mocked engines or `sqlite:///:memory:`)
- Call the real OpenAI API (always patch `services.sql_generator.OpenAI`)
- Require Docker to be running
- Take longer than 15 seconds per test (AppTest default timeout)
- Use `@pytest.mark.integration` or `@pytest.mark.docker` (those are for different layers)
