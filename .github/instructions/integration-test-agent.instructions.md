---
applyTo: "tests/integration/**/*.py"
---

# Integration Test Agent — Rules and Protocol

## Definition of Integration Test in This Project

An **integration test** in Eng2SQL verifies that **two or more components interact
correctly in a configuration that resembles production**, without mocking the boundary
between them.

| Test Type | Scope | Mocks Allowed |
|-----------|-------|---------------|
| Unit | One class/function in isolation | All I/O, DB, API |
| **Integration** | Two or more components together, real driver | External APIs only (OpenAI) |
| E2E / Smoke | Full Streamlit app via `AppTest` | OpenAI only |

Integration tests live in `tests/integration/`. They are **skipped by default** unless
Docker / a real DB is available.

---

## Trigger Rules

The Integration Test Agent runs **automatically** after any of the following events:

| Trigger | Condition |
|---------|-----------|
| User Story implemented | Developer marks US-NNN as ✅ Done |
| Bug fixed | Bug Fix Agent marks BUG-NNN as ✅ Fixed |
| Task completed | Any `## Task` item in a sprint plan is ticked |
| Improvement merged | Any performance / UX improvement story is closed |

The agent MUST run even if only unit tests were written for the trigger event — its job
is to verify the end-to-end system, not duplicate unit test work.

---

## Integration Test Naming Conventions

```
tests/integration/test_<trigger_type>_<scope>.py

Examples:
  test_us040_step2_mysql_connect.py      ← US-040
  test_bug006_mongodb_wsl2_localhost.py  ← BUG-006
  test_db_connector_live_mysql.py        ← persistent fixture-based tests
```

Test function names follow: `test_<action>_<condition>_<expected_result>`

---

## Marker Rules

```python
import pytest

@pytest.mark.integration          # required on ALL integration tests
@pytest.mark.docker               # required if test needs a Docker container
@pytest.mark.live_db              # required if test needs a real DB (not testcontainers)
```

`pyproject.toml` must contain (already present or agent must add):
```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests that require external services",
    "docker: marks tests that require Docker to be running",
    "live_db: marks tests that connect to a real database",
]
addopts = "-m 'not integration'"   # skip integration tests by default
```

---

## Fixture Standards

### Database Fixtures

All integration DB fixtures use `testcontainers-python` or `pytest-docker`.
Fixture scope MUST be `session` (start container once per run):

```python
# tests/conftest.py (integration section)
import pytest
from testcontainers.mysql import MySqlContainer
from testcontainers.mongodb import MongoDbContainer

@pytest.fixture(scope="session")
def mysql_container():
    """Spin up a real MySQL 8.0 container for the test session."""
    with MySqlContainer("mysql:8.0") as container:
        yield container

@pytest.fixture(scope="session")
def mongodb_container():
    """Spin up a real MongoDB 6 container for the test session."""
    with MongoDbContainer("mongo:6.0") as container:
        yield container
```

### Engine / Client Fixtures

```python
@pytest.fixture(scope="session")
def live_mysql_engine(mysql_container):
    from sqlalchemy import create_engine
    url = mysql_container.get_connection_url()
    engine = create_engine(url, pool_pre_ping=True)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def live_mongo_client(mongodb_container):
    from pymongo import MongoClient
    uri = mongodb_container.get_connection_url()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    yield client
    client.close()
```

---

## Test Structure Template

```python
# tests/integration/test_<scope>.py
from __future__ import annotations

import pytest
from src.services.<module> import <Service>


@pytest.mark.integration
@pytest.mark.docker
class Test<Service>Integration:
    """Integration tests for <Service> against a real <DB> instance."""

    def test_<action>_<condition>_<result>(
        self,
        live_<db>_engine,   # or live_<db>_client
    ) -> None:
        """<One-sentence docstring.>"""
        # Arrange
        ...
        # Act
        result = service.<method>()
        # Assert
        assert result ...
```

---

## What to Cover

For every trigger (US, Bug, Task, Improvement), cover at minimum:

| Coverage Area | What to Test |
|---------------|-------------|
| Happy path | The primary use case passes end-to-end with real infrastructure |
| Error path | A real error from the infrastructure (wrong credentials, missing DB) produces the correct exception type and message |
| Boundary conditions | Edge values that are relevant to the trigger (empty collection, 0 rows, max rows) |
| Regression guard | The exact scenario from the bug report (if trigger is a bug fix) |

---

## Verification Record

After running integration tests, record results in
`docs/test-results/ITR-<NNN>-<trigger>.md`:

```markdown
# Integration Test Results — ITR-<NNN>

**Trigger**: US-NNN / BUG-NNN / Task / Improvement
**Date**: <date>
**Infrastructure**: MySQL 8.0 (testcontainers) / MongoDB 6.0 (testcontainers)

## Summary

| Suite | Total | Passed | Failed | Skipped |
|-------|-------|--------|--------|---------|
| Integration | N | N | 0 | 0 |

**Coverage (integration included)**: <X>%

## Test List

| Test | Status | Duration |
|------|--------|----------|
| `test_<name>` | ✅ PASS | 0.3s |

## Observations

- <any environment-specific note>
```

---

## Security Rules

- Never commit real credentials to test fixtures — use container-generated credentials only.
- `testcontainers` auto-generates random passwords; never override with known values.
- If `live_db` tests are used (not testcontainers), credentials MUST come from `.env` via
  `os.getenv()` — never hardcoded.
- Test output must not print connection strings with embedded passwords.

---

## Coverage Obligations

The integration test run MUST NOT drop overall coverage below the unit-test baseline.
If adding integration tests reveals uncovered lines, note them in the ITR file — do not
modify the `--cov-fail-under` gate.

---

## Activity Log Entry Format

Add one row to `PROJECT_PROGRESS.md` per integration test run:

```
| <#> | Integration Test Agent | Ran integration suite for <trigger> | `docs/test-results/ITR-<NNN>-<trigger>.md` — <N> tests, <X>% coverage | <date> |
```
