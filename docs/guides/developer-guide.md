# Eng2SQL — Developer Guide

> **Last Updated**: 2026-05-02
> **Version**: [v1.0.0](../deployment/RELEASE-1.0.0.md)

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Adding a New Feature](#adding-a-new-feature)
5. [Service API Reference](#service-api-reference)
6. [Configuration Reference](#configuration-reference)
7. [Testing Guide](#testing-guide)
8. [Linting & Type Checking](#linting--type-checking)
9. [Multi-Agent Workflow](#multi-agent-workflow)
10. [Contributing Guidelines](#contributing-guidelines)
11. [Deployment Reference](#deployment-reference)

---

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Docker Desktop (optional, for full stack testing)
- An OpenAI API key

### Quick Start

```bash
git clone https://github.com/your-org/eng2sql.git
cd eng2sql

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install all dependencies (including dev tools)
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

# Run the app
streamlit run src/app.py
```

### Running Tests

```bash
# All tests with coverage report
pytest --cov=src --cov-report=term-missing

# Unit tests only (fast, no external services)
pytest tests/unit/ -v

# Integration tests (uses SQLite in-memory)
pytest tests/integration/ -v -m integration

# Coverage gate check (must be ≥ 80%)
pytest --cov=src --cov-fail-under=80
```

---

## Project Structure

```
eng2sql/
├── src/
│   ├── app.py                      ← Streamlit entry point
│   ├── components/                 ← Thin UI-only components
│   │   ├── sidebar.py              ← Mode selection + DB connection form
│   │   ├── query_input.py          ← English text input + button
│   │   ├── sql_output.py           ← Syntax-highlighted SQL block
│   │   ├── schema_viewer.py        ← Collapsible table/column list
│   │   └── progress_tracker.py     ← Step-by-step status display
│   ├── services/                   ← Business logic (no Streamlit imports)
│   │   ├── sql_generator.py        ← OpenAI GPT-5.2 SQL generation
│   │   ├── schema_detector.py      ← YAML + SQLAlchemy schema loading
│   │   └── db_connector.py         ← Engine creation + query execution
│   ├── models/
│   │   └── config.py               ← DBConfig, AppConfig, SchemaColumn dataclasses
│   └── utils/
│       ├── exceptions.py           ← Custom exception hierarchy
│       └── logger.py               ← Structured logging setup
├── tests/
│   ├── conftest.py                 ← Shared fixtures (schema, mocks, SQLite engine)
│   ├── unit/                       ← Unit tests with mocked dependencies
│   └── integration/                ← Integration tests using SQLite
├── docs/
│   ├── guides/
│   │   ├── user-guide.md           ← End-user documentation ← YOU ARE HERE
│   │   └── developer-guide.md      ← Developer documentation
│   ├── architecture/               ← ADRs, system design, API contracts
│   ├── epics/                      ← Epic definitions (agent output)
│   ├── user-stories/               ← Sprint-organised user stories
│   ├── test-cases/                 ← BDD test scenarios
│   ├── bug-reports/                ← Filed by Tester agent
│   └── deployment/                 ← Runbooks, release notes
├── config/
│   └── database_config.yaml        ← Static schema definition
├── .github/
│   ├── copilot-instructions.md     ← Multi-agent system rules
│   ├── prompts/                    ← Agent prompt files (00–10)
│   ├── instructions/               ← Role-scoped coding standards
│   └── workflows/ci-cd.yml        ← GitHub Actions pipeline
└── PROJECT_PROGRESS.md             ← Live project Kanban board
```

---

## Architecture Overview

See [docs/architecture/system-design.md](../architecture/system-design.md) for the full
component diagram and data flow diagrams.

**Design principles:**
- **Services are stateless** — no instance variables that change after `__init__`
- **Components are thin** — UI components call services; never contain business logic
- **Dependency injection** — services receive `AppConfig`/`DBConfig` as constructor args
- **No Streamlit in services** — `src/services/` can be tested without a browser

---

## Adding a New Feature

Follow this checklist for every new feature:

### 1. Read the user story

```
docs/user-stories/<sprint>/US-XXX-<slug>.md
```

### 2. Implement the service (if needed)

All business logic goes in `src/services/`. Example:

```python
# src/services/my_service.py
from __future__ import annotations

from models.config import AppConfig
from utils.exceptions import MyServiceError
from utils.logger import get_logger

logger = get_logger(__name__)


class MyService:
    """One-line description."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def do_thing(self, input_value: str) -> str:
        """Do the thing.

        Args:
            input_value: Description.

        Returns:
            Description of return value.

        Raises:
            MyServiceError: When the thing fails.
        """
        if not input_value.strip():
            raise ValueError("input_value cannot be empty")
        # ... implementation
        return result
```

### 3. Implement the component (if UI change needed)

```python
# src/components/my_component.py
from __future__ import annotations
import streamlit as st

class MyComponent:
    def render(self) -> str | None:
        """Render the component and return user input or None."""
        ...
```

### 4. Wire into app.py

Add the component/service call in `src/app.py`. Keep `app.py` thin — delegate to components and services.

### 5. Write unit tests

```python
# tests/unit/test_my_service.py
from __future__ import annotations
import pytest
from unittest.mock import patch
from services.my_service import MyService

class TestMyService:
    def test_raises_on_empty_input(self, app_config):
        svc = MyService(app_config)
        with pytest.raises(ValueError, match="empty"):
            svc.do_thing("")
```

### 6. Update the guides

After the story is done, update **both** guide files:

| Guide                            | What to update                                                               |
| -------------------------------- | ---------------------------------------------------------------------------- |
| `docs/guides/user-guide.md`      | Add the feature to the relevant section; add example questions if applicable |
| `docs/guides/developer-guide.md` | Update Service API Reference and any new patterns                            |

### 7. Update the user story status

In `docs/user-stories/<sprint>/US-XXX.md`, set status to `✅ DONE`.
Update `PROJECT_PROGRESS.md` sprint board.

---

## Service API Reference

### `SQLGenerator`

**Module**: `src/services/sql_generator.py`

```python
class SQLGenerator:
    def __init__(self, config: AppConfig) -> None: ...

    def generate_sql(
        self,
        question: str,
        schema: TableSchema,
        dialect: str = "MySQL",
    ) -> str:
        """Generate a SQL SELECT from plain English.

        Raises:
            ValueError: question is empty / schema is empty
            SQLGenerationError: OpenAI API failure
        """
```

**Environment variables read**: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_MAX_TOKENS`, `OPENAI_TEMPERATURE`

---

### `SchemaDetector`

**Module**: `src/services/schema_detector.py`

```python
class SchemaDetector:
    def load_static_schema(self, config_path: str) -> TableSchema:
        """Load schema from YAML file.

        Raises:
            FileNotFoundError: file missing
            SchemaDetectionError: YAML malformed or missing 'tables' key
        """

    def detect_live_schema(self, engine: Engine) -> TableSchema:
        """Introspect live database via SQLAlchemy inspect().

        Raises:
            SchemaDetectionError: introspection fails
        """
```

---

### `DBConnector`

**Module**: `src/services/db_connector.py`

```python
class DBConnector:
    def create_engine(self, config: DBConfig) -> Engine:
        """Create and verify a SQLAlchemy engine.

        Raises:
            DatabaseConnectionError: cannot connect
        """

    def test_connection(self, engine: Engine) -> bool:
        """Ping the database. Returns True/False (never raises)."""

    def execute_query(self, engine: Engine, sql: str) -> pd.DataFrame:
        """Execute a SELECT and return results as DataFrame.

        Raises:
            ValueError: sql is not a SELECT statement
            QueryExecutionError: database-level failure
        """

    def list_databases(self, engine: Engine) -> list[str]:
        """Return non-system MySQL database names (sorted).

        Executes SHOW DATABASES on a server-level engine and filters out
        information_schema, performance_schema, mysql, and sys.

        Raises:
            DatabaseConnectionError: query or connection fails
        """
```

### Session State Keys (Sprint 5)

The two-step sidebar flow uses the following `st.session_state` keys:

| Key                   | Type             | Set By         | Description                                          |
| --------------------- | ---------------- | -------------- | ---------------------------------------------------- |
| `db_server_engine`    | `Engine \| None` | Sidebar Step 1 | Server-level engine (no database selected)           |
| `available_databases` | `list[str]`      | Sidebar Step 1 | Non-system databases discovered via `list_databases` |
| `_db_password`        | `str`            | Sidebar Step 1 | Password in-memory only — never persisted            |
| `selected_database`   | `str`            | Sidebar Step 2 | Database name chosen in the Step 2 dropdown          |
| `db_engine`           | `Engine \| None` | Sidebar Step 2 | Full database-level engine                           |
| `detected_schema`     | `TableSchema`    | Sidebar Step 2 | Result of `SchemaDetector.detect_live_schema()`      |
| `db_host`             | `str`            | Sidebar Step 1 | Persisted non-sensitive field                        |
| `db_port`             | `int`            | Sidebar Step 1 | Persisted non-sensitive field                        |
| `db_user`             | `str`            | Sidebar Step 1 | Persisted non-sensitive field                        |

---

## Configuration Reference

### Static Schema YAML

File: `config/database_config.yaml`

```yaml
tables:
  <table_name>:
    - name: <column_name>
      type: <SQL type string>   # e.g. INT, VARCHAR(100), DECIMAL(10,2)
      nullable: true | false    # default: true
      primary_key: true | false # default: false
      default: "<value>"        # optional
```

### Environment Variables

| Variable             | Required | Default                            | Used By             |
| -------------------- | -------- | ---------------------------------- | ------------------- |
| `OPENAI_API_KEY`     | ✅        | —                                  | `SQLGenerator`      |
| `OPENAI_MODEL`       | ❌        | `gpt-5.2`                          | `SQLGenerator`      |
| `OPENAI_BASE_URL`    | ❌        | `https://gpt4ifx.icp.infineon.com` | `SQLGenerator`      |
| `OPENAI_CERT_PATH`   | ❌        | `cert/ca-bundle.crt`               | `SQLGenerator`      |
| `OPENAI_MAX_TOKENS`  | ❌        | `500`                              | `SQLGenerator`      |
| `OPENAI_TEMPERATURE` | ❌        | `0.1`                              | `SQLGenerator`      |
| `LOG_LEVEL`          | ❌        | `INFO`                             | `utils/logger.py`   |
| `DB_HOST`            | ❌        | —                                  | Docker Compose only |
| `DB_PORT`            | ❌        | `3306`                             | Docker Compose only |

---

## Testing Guide

### Fixture Reference (`tests/conftest.py`)

| Fixture               | Scope    | Description                                          |
| --------------------- | -------- | ---------------------------------------------------- |
| `sample_schema`       | function | Minimal customers + orders `TableSchema`             |
| `app_config`          | function | `AppConfig` with dummy API key                       |
| `sample_db_config`    | function | `DBConfig` pointing at localhost (never connects)    |
| `mock_openai_success` | function | Patches `OpenAI`; returns `SELECT * FROM customers;` |
| `mock_openai_error`   | function | Patches `OpenAI`; raises `OpenAIError`               |
| `sqlite_engine`       | session  | In-memory SQLite with customers + orders tables      |

### Test Markers

| Marker                     | Description             | Run command             |
| -------------------------- | ----------------------- | ----------------------- |
| *(none)*                   | Unit test — always runs | `pytest tests/unit/`    |
| `@pytest.mark.integration` | Requires SQLite engine  | `pytest -m integration` |
| `@pytest.mark.slow`        | Long-running tests      | `pytest -m slow`        |

### Coverage Requirements

- **Minimum**: 80% across all `src/` modules
- **Excluded**: `if TYPE_CHECKING:` blocks, `@abstractmethod`, `# pragma: no cover`
- **Run coverage**: `pytest --cov=src --cov-report=html` → open `htmlcov/index.html`

---

## Linting & Type Checking

```bash
# Lint (auto-fix where possible)
ruff check --fix src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/

# All checks in one command (mirrors CI)
ruff check src/ tests/ && ruff format --check src/ tests/ && mypy src/
```

**Configuration**: `pyproject.toml` — `[tool.ruff]` and `[tool.mypy]` sections.

Pre-commit hooks run all checks automatically on `git commit`.

---

## Multi-Agent Workflow

This project uses GitHub Copilot agents for all SDLC activities. Each agent has a
prompt file under `.github/prompts/`. The Orchestrator decides what happens next.

**Full step-by-step guide**: [docs/guides/multi-agent-sdlc-guide.md](multi-agent-sdlc-guide.md)

**To start or resume work:**
```
@workspace #file:.github/prompts/00-orchestrator.prompt.md
```

**Documentation rule**: Every agent that completes a user story MUST update:
- `docs/guides/user-guide.md` (user-facing changes)
- `docs/guides/developer-guide.md` (API / pattern changes)
- `README.md` (if the feature changes setup, usage, or env vars)

---

## Contributing Guidelines

1. **Branch naming**: `feature/US-XXX-short-description` or `fix/BUG-XXX-short-description`
2. **Commit messages**: `feat(US-XXX): short description` / `fix(BUG-XXX): short description`
3. **PR checklist**:
   - All tests pass (`pytest --cov=src --cov-fail-under=80`)
   - Linting clean (`ruff check src/ tests/`)
   - Type check clean (`mypy src/`)
   - Guide files updated if feature is user-facing
   - User story status set to ✅ DONE
   - `PROJECT_PROGRESS.md` sprint board updated
4. **No secrets in code** — ever
5. **No direct pushes to `main`** — always via PR
---

## Deployment Reference

### Docker Image

- **Registry**: `ghcr.io/your-org/eng2sql`
- **Tags**: `1.0.0`, `latest`, `sha-<commit>`
- **Pushed by**: GitHub Actions `publish` job (main branch only)

```bash
# Build locally
docker build -t eng2sql:local .

# Run (mounts cert and config volumes)
docker compose up
```

### CI/CD Stages

| Stage   | Tool            | Gate                          |
| ------- | --------------- | ----------------------------- |
| Lint    | `ruff` + `mypy` | Zero errors                   |
| Test    | `pytest --cov`  | ≥ 80% service-layer coverage  |
| Audit   | `pip-audit`     | No critical CVEs              |
| Docs    | `test -s`       | Guide files must be non-empty |
| Build   | `docker build`  | Image builds successfully     |
| Publish | GHCR push       | `main` branch only            |

### Coverage Scope (Sprint 1–2)

`src/app.py` and `src/components/*` are excluded from coverage measurement until Sprint 3
(see BUG-001). The 80% gate applies to:
- `src/services/` — SQLGenerator, SchemaDetector, DBConnector
- `src/models/` — AppConfig, DBConfig, dataclasses
- `src/utils/` — exceptions, logger

### Full Runbook

See [docs/deployment/runbook.md](../deployment/runbook.md) for local development,
Docker deployment, cloud deployment outlines, scaling, and rollback procedures.

### Release Notes

See [docs/deployment/RELEASE-1.0.0.md](../deployment/RELEASE-1.0.0.md) for the Sprint 1
changelog.