---
applyTo: "tests/unit/**/*.py"
---

# Unit Test Agent — Rules and Protocol

## Definition of Unit Test in This Project

A **unit test** in Eng2SQL verifies that **one class or function behaves correctly in
isolation**, with all I/O, database connections, and external API calls replaced by mocks
or in-memory stubs.

| Test Type | Scope | Mocks Required |
|-----------|-------|----------------|
| **Unit** | One class / function | All DB, API, filesystem I/O |
| Integration | Two+ components, real driver | External APIs only |
| E2E / Smoke | Full Streamlit `AppTest` | OpenAI only |

Unit tests live in `tests/unit/`. They run by default on every `pytest` invocation
(no special markers needed).

---

## Trigger Rules

The Unit Test Agent runs **automatically** after any of the following events:

| Trigger | Condition |
|---------|-----------|
| User Story implemented | Developer completes a US-NNN story in Phase 5 |
| Bug fixed | Bug Fix Agent marks BUG-NNN as ✅ Fixed |
| Task completed | Any `## Task` item in a sprint plan is ticked |
| Improvement merged | Any performance / UX improvement story is closed |

The agent fires **per trigger**, inline inside Phase 5 and Phase 11. Phase 5b is the
sprint-level sweep for anything missed inline.

---

## File Naming Conventions

```
tests/unit/test_<module>_<sprint_or_trigger>.py

Examples:
  test_sql_generator.py                       ← core module tests (persists sprint-over-sprint)
  test_db_connector_postgresql_unit.py        ← sprint-scoped feature tests
  test_sidebar_sprint11.py                    ← sprint-scoped UI tests
  test_network.py                             ← utility module tests
  test_bug006_mongo_auth_unit.py              ← bug-scoped regression test
```

Test result document naming:

```
docs/test-results/UTR-<NNN>-<trigger>.md

Examples:
  UTR-001-US-044.md
  UTR-002-BUG-005.md
  UTR-003-US-050-US-051.md       ← multiple stories in one sweep
```

---

## Test Function and Class Naming

```python
# Class: Test<ClassName> or Test<FeatureSlug>
class TestSQLGenerator:
    ...

class TestDbConnectorPostgresql:
    ...

# Function: test_<action>_<condition>_<expected>
def test_generate_sql_empty_input_raises_value_error():
    ...

def test_create_engine_uses_psycopg_driver():
    ...

def test_probe_reachable_host_returns_fallback_on_timeout():
    ...
```

---

## Mandatory Test Coverage

For **every** trigger (US, Bug, Task, Improvement), the unit tests MUST cover at minimum:

| Coverage Area | What to Write |
|---------------|---------------|
| Happy path | One test per acceptance criterion that succeeds |
| Edge / boundary | Empty string, None, zero, max-length input |
| Error path | One test per exception type the code can raise |
| Regression | For bugs: one test that reproduces the original failure (must fail before fix, pass after) |
| Parametrize | Use `@pytest.mark.parametrize` when 3+ similar inputs share the same assertion logic |

---

## Mocking Standards

```python
from unittest.mock import MagicMock, patch, call
import pytest

# Mock OpenAI — ALWAYS in unit tests
@patch("services.sql_generator.OpenAI")
def test_generate_sql_calls_openai(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices[0].message.content = "SELECT 1"
    ...

# Mock SQLAlchemy engine
@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.connect.return_value.__enter__ = MagicMock(return_value=MagicMock())
    engine.connect.return_value.__exit__ = MagicMock(return_value=False)
    return engine

# Mock filesystem
@patch("builtins.open", new_callable=MagicMock)
def test_load_schema_reads_file(mock_open):
    mock_open.return_value.__enter__.return_value.read.return_value = "schema: {}"
    ...
```

**Never** import or instantiate a real DB engine, real OpenAI client, or real filesystem
path inside a unit test. Use `patch` or pass mocks through fixtures.

---

## LRU-Cache Tests

When testing functions decorated with `@functools.lru_cache`, always clear the cache in
`setup_method` / `teardown_method` to prevent state leakage:

```python
class TestIsWsl2:
    def setup_method(self):
        from utils.network import is_wsl2
        is_wsl2.cache_clear()

    def teardown_method(self):
        from utils.network import is_wsl2
        is_wsl2.cache_clear()
```

---

## Streamlit AppTest Standards

```python
from streamlit.testing.v1 import AppTest
import pathlib

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")

@pytest.fixture
def at():
    """Fresh AppTest instance."""
    return AppTest.from_file(APP_PATH, default_timeout=15)

# SafeSessionState does NOT support .get() — use key-in check:
value = at.session_state["key"] if "key" in at.session_state else None
```

---

## Coverage Requirements

| Scope | Minimum |
|-------|---------|
| New module introduced by the story | 90% |
| Modified module | 80% (no regression from baseline) |
| Overall project coverage | ≥ 80% (CI gate) |

Run:
```bash
pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing --cov-fail-under=80
```

If coverage drops below the baseline recorded before the story started, the unit tests
are **not complete** — add more tests or note uncoverable lines with `# pragma: no cover`
(only for abstract methods and `if TYPE_CHECKING:` blocks).

---

## UTR Document Format

```markdown
# Unit Test Results UTR-<NNN> — <Trigger>

**Trigger**: US-<NNN> <title> / BUG-<NNN> <title>
**Date**: YYYY-MM-DD
**Sprint**: Sprint <N>
**Agent**: Unit Test Agent
**Baseline coverage**: XX.XX%

## Summary

| Category | Total | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| Unit     | N     | N      | 0      | 0       |

**Coverage after story**: XX.XX% (delta: +X.XX%)
**Coverage gate (≥ 80%)**: ✅ Pass / ❌ Fail

## Test Files Written / Modified

- `tests/unit/test_<slug>.py` — N tests

## Test Names

| # | Test | Result |
|---|------|--------|
| 1 | `test_<name>` | ✅ |

## Issues Found

> None — all tests pass.   (or describe failures with traceback excerpts)

## Actions Taken

- (e.g.) Fixed off-by-one in `sql_generator.py` line 42 after test revealed it.
- (e.g.) Created BUG-NNN for unresolved failure.

## Next Step

→ Proceed to Per-story integration test trigger / Phase 5b sweep.
```

---

## pyproject.toml Requirements

The `[tool.pytest.ini_options]` section MUST include:

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
]
addopts = "-m 'not integration'"
```

Unit tests must **not** carry `@pytest.mark.integration` or `@pytest.mark.docker`.
They must run in every `pytest` invocation without flags.
