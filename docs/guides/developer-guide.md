# Eng2SQL — Developer Guide

> **Last Updated**: 2026-05-28
> **Version**: v1.2.0 (Sprint 7)

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
│   │   ├── db_connector.py         ← Engine creation + query execution
│   │   ├── mongo_connector.py      ← pymongo connect + list/get database
│   │   └── mongo_schema_detector.py← MongoDB collection sampling → TableSchema
│   ├── models/
│   │   └── config.py               ← DBConfig, MongoConfig, AppConfig, SchemaColumn dataclasses
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

---

## Adding a New Relational Database Engine (US-051)

Sprint 13 (US-051) introduced `_RelationalDialectConfig` — a frozen dataclass that
consolidates the MySQL and PostgreSQL Step 1 / Step 2 sidebar flows into a single shared
implementation (`_render_relational_step1` / `_render_relational_step2`).

To add a new relational engine (e.g. Oracle, MSSQL, SQLite) you only need ~30 lines:

### 1. Add a new dialect to `DBConfig` (if not already supported)

```python
# src/models/config.py
_DRIVER_SCHEMES: dict[str, str] = {
    "mysql": "mysql+pymysql",
    "postgresql": "postgresql+psycopg",
    "oracle": "oracle+cx_oracle",   # ← add here
}
```

### 2. Add session-state clear keys

```python
# src/components/sidebar.py
_ORACLE_KEYS: tuple[str, ...] = (
    "ora_server_engine", "ora_available_databases", "ora_selected_database",
    "ora_engine", "detected_schema", "_ora_password", "ora_step1_status", "ora_step2_status",
)

def _clear_oracle_state() -> None:
    for key in _ORACLE_KEYS:
        st.session_state.pop(key, None)
```

### 3. Create the dialect config constant

```python
# src/components/sidebar.py
_ORACLE_CFG = _RelationalDialectConfig(
    host_key="ora_host", port_key="ora_port", user_key="ora_user",
    password_key="_ora_password",
    server_engine_key="ora_server_engine", available_dbs_key="ora_available_databases",
    current_db_key="ora_selected_database", engine_key="ora_engine",
    step1_status_key="ora_step1_status", step2_status_key="ora_step2_status",
    host_widget_key="ora_host_input", port_widget_key="ora_port_input",
    user_widget_key="ora_user_input", password_widget_key="ora_password_input",
    connect_btn_key="ora_connect", selectbox_key="ora_db_select", confirm_btn_key="ora_db_confirm",
    default_port=1521, dialect="oracle", log_dialect="Oracle", clear_fn=_clear_oracle_state,
)
```

### 4. Add thin wrappers + wire up in `render()`

```python
# in SidebarComponent
def _render_oracle_step1(self) -> None:
    self._render_relational_step1(_ORACLE_CFG)

def _render_oracle_step2(self) -> None:
    self._render_relational_step2(_ORACLE_CFG)
```

```python
# in SidebarComponent.render()
elif db_type == "Oracle":
    st.subheader("Oracle Live Database")
    self._render_oracle_step1()
    self._render_oracle_step2()
```

### 5. Add the engine option to the radio widget

```python
options=["MySQL", "PostgreSQL", "Oracle", "MongoDB"],
```

That's it — no other files need changing.  The shared renderer handles credentials,
connection, database listing, schema detection, password cleanup, and status display
automatically for any dialect registered with `_RelationalDialectConfig`.

---

### `_RelationalDialectConfig` field reference

| Field                                                   | Description                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------------------ |
| `host_key` / `port_key` / `user_key`                    | Session-state key names for connection data                              |
| `password_key`                                          | Prefixed with `_` by convention (e.g. `_db_password`)                    |
| `server_engine_key`                                     | Server-level SQLAlchemy engine after Step 1                              |
| `available_dbs_key`                                     | List of enumerated database names after Step 1                           |
| `current_db_key`                                        | Chosen database name after Step 2                                        |
| `engine_key`                                            | Database-level engine after Step 2                                       |
| `step1_status_key` / `step2_status_key`                 | Status tuple `(level, msg)`                                              |
| `*_widget_key`                                          | Streamlit widget key (use `None` to auto-generate)                       |
| `connect_btn_key` / `selectbox_key` / `confirm_btn_key` | Button / dropdown keys                                                   |
| `default_port`                                          | Pre-filled port number                                                   |
| `dialect`                                               | Short dialect string for `DBConfig` (`"mysql"`, `"postgresql"`, ...)     |
| `log_dialect`                                           | Human-readable name for log messages                                     |
| `clear_fn`                                              | Module-level function to clear this dialect's session state              |
| `sslmode_*`                                             | PostgreSQL-specific SSL mode fields (leave `None` for other dialects)    |
| `admin_db_*`                                            | PostgreSQL-specific admin-DB enumeration field (leave `None` for others) |

---



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

### `MongoDBConnector`

**Module**: `src/services/mongo_connector.py`

```python
class MongoDBConnector:
    def connect(self, config: MongoConfig) -> object:
        """Create and verify a pymongo MongoClient.

        Verifies connectivity via admin.command("ping").

        Raises:
            DatabaseConnectionError: pymongo not installed, or cannot connect
        """

    def list_databases(self, client: object) -> list[str]:
        """Return non-system MongoDB database names (sorted).

        Filters out admin, local, config.

        Raises:
            DatabaseConnectionError: driver failure
        """

    def get_database(self, client: object, name: str) -> object:
        """Return a pymongo Database object for the given name."""
```

#### WSL2 + MongoDB networking (BUG-006)

> **Sprint 11 update (US-050)** — the WSL2 fail-fast helper has been
> **extracted to `src/utils/network.py`**. `MongoDBConnector` now imports
> `LOOPBACK_HOSTS`, `is_wsl2`, and `probe_reachable_host` from there.
> `DBConnector.create_engine` (relational engines) applies the same guard
> before SQLAlchemy connects, so PostgreSQL and MySQL get equivalent
> WSL2 protection. Existing class attributes `_LOOPBACK_HOSTS`,
> `_is_wsl2`, and `_probe_reachable_host` on `MongoDBConnector` are retained
> as backward-compat thin wrappers and the BUG-005 invariant test still
> passes.

When the Streamlit app runs inside **WSL2** and the user supplies a MongoDB
URI with a loopback host (`localhost`, `127.0.0.1`, `::1`), the WSL2 loopback
interface does **not** see services bound to the Windows host. Prior to the
BUG-006 fix this produced a 5-second `ServerSelectionTimeoutError` with no
actionable guidance.

`MongoDBConnector.connect()` now performs a **WSL2-aware fail-fast**:

1. The TCP probe (`_probe_reachable_host`) attempts every address returned
   by `socket.getaddrinfo()` and falls back to the original host when none
   accept a connection.
2. Immediately after the probe call, `connect()` checks three conditions:
   probe failed (`returned host == requested host`), the requested host is
   in `_LOOPBACK_HOSTS`, and `_is_wsl2()` returns `True` (detected via the
   `microsoft` marker in `/proc/version`).
3. If all three are true the connector raises `DatabaseConnectionError`
   immediately with a hint that points the user at `/etc/resolv.conf`'s
   `nameserver` line (= the Windows host IP) or `host.docker.internal`.

This avoids the `MongoClient` call entirely in the WSL2 case so the user
sees the remediation hint within ~1 s instead of after a 5 s timeout.

> **Important**: do **not** "fix" loopback timeouts by forcing
> `directConnection=True`. The BUG-005 final decision was to never set this
> flag because it triggers hello-handshake failures on Windows + pymongo
> 4.16. The invariant is enforced by
> `test_connect_does_not_force_direct_connection`.

---

### `MongoSchemaDetector`

**Module**: `src/services/mongo_schema_detector.py`

```python
class MongoSchemaDetector:
    def detect_schema(
        self,
        db: object,
        sample_size: int = 100,
    ) -> TableSchema:
        """Sample MongoDB collections and infer a TableSchema.

        Unions field names across sampled documents.
        Uses "Mixed" when the same field has conflicting types.
        Marks _id as primary_key=True; all fields nullable=True.

        Raises:
            SchemaDetectionError: list_collection_names() or find() fails
        """
```

**Type mapping** (`_BSON_TYPE_MAP`):

| Python type    | Schema type |
| -------------- | ----------- |
| `int`, `float` | `Number`    |
| `str`          | `String`    |
| `bool`         | `Boolean`   |
| `dict`         | `Object`    |
| `list`         | `Array`     |
| `NoneType`     | `Null`      |
| `ObjectId`     | `ObjectId`  |
| conflicting    | `Mixed`     |

---

### Session State Keys (Sprint 6 — MongoDB)

| Key                         | Type                  | Set By                 | Description                                                 |
| --------------------------- | --------------------- | ---------------------- | ----------------------------------------------------------- |
| `db_type`                   | `str`                 | Sidebar radio          | `"MySQL"`, `"PostgreSQL"`, or `"MongoDB"`                   |
| `mongo_client`              | `MongoClient \| None` | Sidebar Step 1 (Mongo) | Server-level MongoClient                                    |
| `mongo_available_databases` | `list[str]`           | Sidebar Step 1 (Mongo) | Non-system databases on the server                          |
| `mongo_selected_database`   | `str`                 | Sidebar Step 2 (Mongo) | Database name chosen in dropdown                            |
| `mongo_db`                  | `Database \| None`    | Sidebar Step 2 (Mongo) | pymongo Database object                                     |
| `pg_server_engine`          | `Engine \| None`      | Sidebar Step 1 (PG)    | Server-level SQLAlchemy engine (EPIC-009)                   |
| `pg_available_databases`    | `list[str]`           | Sidebar Step 1 (PG)    | Non-template databases                                      |
| `pg_engine`                 | `Engine \| None`      | Sidebar Step 2 (PG)    | Database-level engine                                       |
| `pg_selected_database`      | `str`                 | Sidebar Step 2 (PG)    | Database chosen in dropdown                                 |
| `pg_sslmode`                | `str`                 | Sidebar Step 1 (PG)    | One of `disable/allow/prefer/require/verify-ca/verify-full` |

> Sprint 7 added `mongo_input_mode` and `mongo_raw_uri` — see section above.

---

## PostgreSQL Support (EPIC-009 / Sprint 10)

### Dialect dispatch

`DBConfig` now carries a short-form `dialect` attribute (`"mysql"` or `"postgresql"`) and
builds the SQLAlchemy URL from a `_DRIVER_SCHEMES` lookup:

```python
_DRIVER_SCHEMES = {
    "mysql":      "mysql+pymysql",
    "postgresql": "postgresql+psycopg",
}
```

Backwards compatibility: legacy long-form `dialect="mysql+pymysql"` is auto-normalised to
`"mysql"` in `__post_init__`. Existing code passing the long form continues to work.

### sslmode whitelist

`_VALID_SSLMODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}`
is enforced in `__post_init__`. Unknown sslmodes raise `ValueError` at construction time
(not at connect time) so misconfiguration surfaces immediately.

PostgreSQL URLs always include `?sslmode=<value>` (default `prefer`). MySQL URLs ignore
the field.

### `list_databases` dispatch

```python
_LIST_DB_QUERIES = {
    "mysql":      "SHOW DATABASES",
    "postgresql": "SELECT datname FROM pg_database WHERE datistemplate = false",
}
```

`DBConnector.list_databases` reads `engine.dialect.name` and dispatches. Unknown dialects
raise `NotImplementedError`. The `_SYSTEM_DATABASES` filter set was extended with
`postgres`, `template0`, `template1`.

### LLM dialect tips

`SQLGenerator` now reads `_DIALECT_TIPS` and appends a PostgreSQL-specific block to the
system prompt (`ILIKE`, `::` casting, `LIMIT N OFFSET M`, mixed-case identifier
quoting). MySQL prompts are unchanged. The dialect string is plumbed end-to-end from the
sidebar (`db_type`) through `app.py` into `generate_sql(..., dialect=...)`.

### `psycopg3` driver

We use `psycopg[binary]>=3.2,<4` (NOT `psycopg2-binary`). Rationale captured in
`docs/architecture/postgresql-epic-evaluation.md` §2: native asyncio support, modern
COPY API, smaller binary footprint, and active upstream maintenance.

### `postgres_container` integration fixture

`tests/conftest.py` exposes a session-scoped `postgres_container` fixture mirroring
`mysql_container`. It uses `testcontainers[postgres]>=4.7.0` with image
`postgres:16-alpine` and `username/password/dbname = testroot/testroot/testdb`. Skip
semantics are identical to the MySQL fixture (ImportError → skip; DockerException →
skip). Tests using the fixture must carry the `[integration, docker]` markers.

The `DBConfig` yielded by the fixture sets `dialect="postgresql"` and `sslmode="disable"`
(plaintext local container).



### `MongoConfig`

**Module**: `src/models/config.py`

```python
@dataclass
class MongoConfig:
    host: str
    port: int = 27017
    username: str = ""
    password: str = ""
    auth_source: str = "admin"
    auth_mechanism: str = "SCRAM-SHA-256"
    connect_timeout_ms: int = 5000
    raw_uri: str = ""          # Sprint 7: optional full URI (URI mode)

    @property
    def connection_uri(self) -> str:
        """Build a pymongo connection URI.

        URI mode (raw_uri non-empty):
        - Raises ValueError if the URI already contains embedded credentials.
        - Injects username:encoded_pw into the netloc when username is set.
        - Returns raw_uri unchanged when username is empty.

        Field mode (raw_uri == ""):
        - Uses urllib.parse.quote_plus to percent-encode the password.
        - Returns a no-auth URI when username is empty.
        - Includes credentials without authMechanism when mechanism is
          "None / No Auth" (BUG-004 fix).
        """
```

**Sprint 7 changes**: Added `raw_uri: str = ""` field and `_connection_uri_from_raw()`
private method. When `raw_uri` is set, `connection_uri` calls `_connection_uri_from_raw()`
which uses `urllib.parse.urlparse` to parse the URI, validates no embedded credentials
(`@` in netloc), injects `username:quote_plus(password)@` into the netloc, and returns
`urllib.parse.urlunparse(injected)`. SRV URIs (`mongodb+srv://`) are handled correctly
because `urlparse` preserves the scheme.

---

### Session State Keys (Sprint 7 additions — MongoDB)

| Key                | Type  | Set By             | Description                         |
| ------------------ | ----- | ------------------ | ----------------------------------- |
| `mongo_input_mode` | `str` | Sidebar mode radio | `"Fields"` or `"URI + credentials"` |
| `mongo_raw_uri`    | `str` | Sidebar URI field  | Persisted raw URI (non-sensitive)   |

All Sprint 6 MongoDB keys (`mongo_client`, `mongo_available_databases`,
`mongo_selected_database`, `mongo_db`, `detected_schema`) are unchanged.

> **State clearing**: `mongo_input_mode` and `mongo_raw_uri` are included in
> `_MONGO_KEYS` so they are cleared on reconnect or when switching the database type.

---

### `MongoDBConnector.connect()` — SRV URI handling (Sprint 7)

`directConnection=True` is required for standalone MongoDB servers (topology timeout fix
from Sprint 6) but is **incompatible** with `mongodb+srv://` URIs (Atlas, replica sets
using SRV discovery).

The connector detects the SRV scheme and conditionally passes `directConnection`:

```python
uri = config.connection_uri
use_direct = not uri.startswith("mongodb+srv://")
client = MongoClient(
    uri,
    serverSelectionTimeoutMS=config.connect_timeout_ms,
    **({"directConnection": True} if use_direct else {}),
)
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

| Fixture                | Scope    | Description                                                  |
| ---------------------- | -------- | ------------------------------------------------------------ |
| `sample_schema`        | function | Minimal customers + orders `TableSchema`                     |
| `app_config`           | function | `AppConfig` with dummy API key                               |
| `sample_db_config`     | function | `DBConfig` pointing at localhost (never connects)            |
| `mongo_config`         | function | `MongoConfig` with SCRAM-SHA-256 auth, pointing at localhost |
| `mongo_config_no_auth` | function | `MongoConfig` with `auth_mechanism="None / No Auth"`         |
| `mock_openai_success`  | function | Patches `OpenAI`; returns `SELECT * FROM customers;`         |
| `mock_openai_error`    | function | Patches `OpenAI`; raises `OpenAIError`                       |
| `sqlite_engine`        | session  | In-memory SQLite with customers + orders tables              |

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

### Streamlit AppTest Known Quirks

Streamlit's `AppTest` harness (introduced in Streamlit 1.28) is the only
supported way to test Streamlit components without a browser. It has several
non-obvious limitations that have caused multiple debugging cycles in this
project. **Read this section before adding or modifying any test under
`tests/unit/test_sidebar*.py` or `tests/unit/test_*_ui.py`.** The canonical
working examples are
[tests/unit/test_sidebar_ui.py](../../tests/unit/test_sidebar_ui.py) and
[tests/unit/test_sidebar_step2.py](../../tests/unit/test_sidebar_step2.py).

#### Quick-reference table

| Quirk                        | ❌ Wrong                                                                  | ✅ Correct                                                                 |
| ---------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| Chaining `set_value` / `run` | `at.text_input[0].set_value("x").run()`                                  | `at.text_input[0].set_value("x"); at.run()` (separate)                    |
| `session_state` access       | `at.session_state.get("key")`                                            | `if "key" in at.session_state: at.session_state["key"]`                   |
| `session_state.pop` / `.get` | `at.session_state.pop("k", None)`                                        | `del at.session_state["k"]` (after checking `in`)                         |
| First-run timeout            | `AppTest.from_file("src/app.py")`                                        | `AppTest.from_file("src/app.py", default_timeout=10)`                     |
| Widget index round-trips     | `at.radio[0].set_value("MongoDB"); ... ; at.radio[0].set_value("MySQL")` | Run **one direction per test**; assert state after each switch separately |
| Mocking imports inside app   | `patch("src.components.sidebar.DBConnector")`                            | `patch("services.db_connector.DBConnector.create_engine")` (class-level)  |

#### 1. Chaining `.set_value()` and `.run()` is forbidden

`set_value()` returns `None`, not the widget. The intuitive
`at.button(key="x").click().run()` will raise `AttributeError`. Always split:

```python
# ❌ Broken — set_value returns None, .run() fails on NoneType
at.text_input[0].set_value("hello").run()

# ✅ Correct — separate statements
at.text_input[0].set_value("hello")
at.run()
```

---

## AppTest Fixture Scoping (US-077)

*Investigated in Sprint 17. Results recorded in
[UTR-021](../test-results/UTR-021-us077-apptest-fixture-sharing.md) and
[test_apptest_fixture_investigation.py](../../tests/unit/test_apptest_fixture_investigation.py).*

### Problem

Each `AppTest.from_file()` call incurs a ~1–5 s cold-start penalty. With 352 unit tests
(many using AppTest), this adds up. Can a shared, module-scoped fixture reduce overhead?

### Benchmark Results (dev machine, Python 3.14.3, 12 workers)

| Fixture scope      | AppTest cold starts | Total smoke suite | Safe for mutations? |
| ------------------ | ------------------- | ----------------- | ------------------- |
| Function (default) | 1 per test          | 44.6 s (71 tests) | ✅ Yes               |
| Module (shared)    | 1 per module        | —                 | ❌ No                |

### Why Module Scope Is Unsafe for Interactive Tests

`AppTest` is **stateful** — widget state and `session_state` persist between `at.run()`
calls on the same instance. An interactive test that calls `at.radio[0].set_value("MongoDB")`
leaves the shared instance with `db_type = "MongoDB"`. Any subsequent test in the same
module that expects `db_type = "MySQL"` (the default) will fail. This creates **order-dependent
failures** — the worst category of test flakiness.

### Safe Pattern: `initial_app_state` Fixture

`tests/conftest.py` exposes a module-scoped `initial_app_state` fixture for **read-only**
initial-state checks:

```python
def test_no_crash_on_startup(initial_app_state) -> None:
    assert not initial_app_state.exception

def test_default_db_type(initial_app_state) -> None:
    assert initial_app_state.session_state["db_type"] == "MySQL"
```

**Rules for using `initial_app_state`:**
- ✅ Call `at.run()` if you need a fresh render — but then use a function-scoped AT
- ✅ Read widget values or session_state defaults
- ❌ Never call `set_value()`, `click()`, or write to `session_state`
- ❌ Never use for multi-step interaction tests

### Recommendation

Keep **function-scoped** AppTest for all interactive tests. Use `initial_app_state`
only for trivial "does the app boot" or "is this widget present" checks. The marginal
speedup (~1–5 s per module) does not justify the fragility risk for interactive tests.
```

#### 2. `at.session_state` is a `SafeSessionState`, not a dict

The `SafeSessionState` proxy raises `AttributeError` on `.get()` and `.pop()`.
Use indexed access plus an `in` check:

```python
# ❌ Broken — AttributeError: get not found in session_state
val = at.session_state.get("detected_schema")

# ❌ Broken — AttributeError: pop not found in session_state
at.session_state.pop("_db_password", None)

# ✅ Correct
if "detected_schema" in at.session_state:
    val = at.session_state["detected_schema"]

# ✅ Correct (delete pattern)
if "_db_password" in at.session_state:
    del at.session_state["_db_password"]
```

#### 3. Default timeout is 3 seconds — too short for first run

The first `at.run()` compiles and executes `src/app.py` end-to-end. On a cold
import (Pylance warm cache, fresh venv) this can take 5–8 seconds. The default
3-second timeout produces sporadic `RuntimeError: AppTest hit the timeout`.
Always pass `default_timeout=10`:

```python
# ✅ Correct
at = AppTest.from_file("src/app.py", default_timeout=10)
at.run()
```

#### 4. Widget tree indices change between app states

`at.radio[0]`, `at.button[2]` etc. are positional indices into the widget tree
**as it currently exists**. Switching DB type / connection mode reorders the
sidebar widgets, so an index that was valid on the first render may point at a
different widget after the second `at.run()`.

Two safe patterns:
- **Test each state in its own test** — never round-trip MongoDB → MySQL → MongoDB
  in a single test. One direction per test, asserted after each transition.
- **Use `key=` lookups** — every interactive widget in `src/components/sidebar.py`
  has an explicit `key=` (e.g. `key="mysql_connect"`, `key="mysql_db_select"`).
  Look up by key:

```python
# ✅ Stable across widget tree changes
at.button(key="mysql_connect").click()
at.run()

# ❌ Fragile — index 9 may not always be the Connect button
at.button[9].click()
```

#### 5. Mock at the import-source path, not the consumer path

`SidebarComponent` imports `DBConnector` like this:
`from services.db_connector import DBConnector`. To mock `create_engine` for
**every** instance the app may construct, patch the class on its source module:

```python
# ✅ Correct — patches every instance in the process
with patch("services.db_connector.DBConnector.create_engine", return_value=fake_engine):
    at.run()

# ❌ Often broken — depends on whether sidebar.py kept the symbol bound
with patch("src.components.sidebar.DBConnector") as mock_cls:
    ...
```

Reference: [tests/unit/test_sidebar_step2.py](../../tests/unit/test_sidebar_step2.py)
patches `services.db_connector.DBConnector.create_engine` and
`services.schema_detector.SchemaDetector.detect_live_schema` at the class
level — both work for any instance the app constructs.

#### 6. `detected_schema` must be injected as `SchemaColumn` objects — NEVER plain strings

When a test or smoke test pre-populates `session_state["detected_schema"]`,
the value **must** use `SchemaColumn` dataclass instances.  If plain strings
are injected instead, `schema_viewer.py` will crash with
`AttributeError: 'str' object has no attribute 'name'` because the viewer
calls `col.name`, `col.type`, etc.

```python
# ❌ Broken — SchemaViewerComponent calls col.name on every item
app.session_state["detected_schema"] = {
    "users": ["id", "name", "active"]   # ← plain strings
}

# ✅ Correct — use SchemaColumn dataclass
from models.config import SchemaColumn

app.session_state["detected_schema"] = {
    "users": [
        SchemaColumn(name="id",     type="INT",      nullable=False, primary_key=True),
        SchemaColumn(name="name",   type="VARCHAR",  nullable=True,  primary_key=False),
        SchemaColumn(name="active", type="TINYINT",  nullable=False, primary_key=False),
    ]
}
```

The same pattern applies for MongoDB-style schemas — use the same dataclass,
setting `type` to the BSON type string (e.g. `"ObjectId"`, `"str"`, `"bool"`):

```python
from models.config import SchemaColumn

app.session_state["detected_schema"] = {
    "orders": [
        SchemaColumn(name="_id",    type="ObjectId", nullable=False, primary_key=True),
        SchemaColumn(name="total",  type="float",    nullable=True,  primary_key=False),
        SchemaColumn(name="status", type="str",      nullable=True,  primary_key=False),
    ]
}
```

This requirement is verified in all Sprint 11 and Sprint 12 smoke tests
([tests/smoke/](../../tests/smoke/)).

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

| Stage             | Tool                     | Gate                                                |
| ----------------- | ------------------------ | --------------------------------------------------- |
| Lint              | `ruff` + `mypy`          | Zero errors                                         |
| Test              | `pytest --cov`           | ≥ 80% service-layer coverage                        |
| Coverage (Docker) | `pytest -m docker --cov` | `coverage-docker.xml` artifact uploaded (see below) |
| Audit             | `pip-audit`              | No critical CVEs                                    |
| Docs              | `test -s`                | Guide files must be non-empty                       |
| Build             | `docker build`           | Image builds successfully                           |
| Publish           | GHCR push                | `main` branch only                                  |

#### `coverage-docker` Job (US-053 / US-070)

The `coverage-docker` job in `.github/workflows/ci-cd.yml` runs integration tests that
require a live Docker daemon (marked `@pytest.mark.docker`). It executes after the `lint`
job and produces a `coverage-docker.xml` artifact uploaded to the Actions run summary.

Key configuration details verified in Sprint 15 (US-070):
- Runs `pytest -m docker -v --cov=src --cov-report=xml:coverage-docker.xml`
- Uses `if-no-files-found: warn` on the artifact upload step — the job passes cleanly
  even when no `docker`-marked tests exist (safe for branches without Docker tests)
- `OPENAI_API_KEY` is set to a placeholder value for test isolation
- `timeout-minutes: 10` prevents runaway jobs

Sprint 16 (US-073) re-verified the `coverage-docker` YAML is structurally correct and
unchanged.  No GitHub Actions self-hosted runner is available in the local dev environment;
the verification is YAML-level (the workflow file is correct) and is confirmed functional
via Sprint 15's successful CI run records.

---

### Parallel Test Execution with pytest-xdist (US-074 — Sprint 16)

`pytest-xdist` (≥ 3.5.0) is now a required dev dependency.  The default `addopts` in
`pyproject.toml` includes `-n auto`, which spawns one worker per logical CPU core.

**Benchmark (Windows, 12 logical cores, 335 unit tests):**

| Mode                            | pytest time | Wall-clock time |
| ------------------------------- | ----------- | --------------- |
| Sequential (baseline)           | 87.85 s     | ~94 s           |
| Parallel `-n auto` (12 workers) | 47.98 s     | ~53 s           |
| **Speedup**                     | **~41 %**   | **~44 %**       |

All 335 unit tests and 54 smoke tests are xdist-compatible (no global singleton state
or module-reload conflicts).  Coverage collection (`--cov`) still works alongside xdist.

To run sequentially (e.g. when debugging output order):

```bash
pytest tests/unit -p no:xdist
```

### AppTest + pytest-xdist Compatibility (US-081 — Sprint 18)

AppTest rendering tests in `tests/unit/test_sidebar_rendering.py` and
`tests/unit/test_apptest_fixture_investigation.py` are **NOT safe to run under
`-n auto`** because:

1. AppTest spawns its own Streamlit process internally; multiple xdist workers
   competing for the same Streamlit state can cause flaky timeouts and assertion
   failures.
2. Process-level Streamlit singleton state is shared across workers on the same
   machine, making test isolation unreliable.

**Rule**: AppTest tests that mutate widget state (click buttons, fill inputs,
switch radio options) **must** run sequentially.

The `pyproject.toml` default `addopts` includes `-n auto` for the full suite.
To run only rendering tests without xdist interference:

```bash
pytest tests/unit/test_sidebar_rendering.py -v --tb=short \
    --override-ini="addopts=-v --tb=short -m 'not integration and not smoke'"
```

Or strip `-n auto` from all unit tests for a coverage run:

```bash
pytest tests/unit/ --cov=src --cov-report=term-missing \
    --override-ini="addopts=--tb=short -m 'not integration and not smoke'"
```

The `--override-ini="addopts=..."` flag completely replaces the `pyproject.toml`
`addopts` value for that invocation — it does not append.

---

### Optional-Import `# pragma: no cover` Pattern (US-081 — Sprint 18)

Some source lines are **architecturally unreachable** in the standard test environment
because they depend on optional packages that are not declared as project dependencies.
These lines are annotated with `# pragma: no cover` to exclude them from measurement
without falsely inflating the "miss" count.

#### Current annotations

| File                                 | Location                                                       | Reason                                                                                                      |
| ------------------------------------ | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `src/components/sidebar.py`          | `return pathlib.Path(certifi.where()).is_file()`               | `certifi` is not a project dependency; `import certifi` always raises `ImportError` in CI                   |
| `src/components/sidebar.py`          | `if client is None:` block in `_render_mongo_step2`            | Step-2 only renders after a successful connect — `client` is never `None` at this point in the AppTest flow |
| `src/components/progress_tracker.py` | `def reset()` and `def update()`                               | Entire methods are `st.` widget calls; require a live Streamlit widget tree, not reachable via AppTest      |
| `src/components/query_input.py`      | `if clicked:` block                                            | Button-click path with empty-input guard; not exercised by current AppTest fixtures                         |
| `src/components/schema_viewer.py`    | `if not schema:` block and `if st.button("🔄 Refresh Schema"):` | Empty-schema branch and refresh-button click; test fixtures always provide non-empty schemas                |

#### Annotation format

Always add a short inline comment explaining WHY the line is excluded:

```python
# ✅ Correct — with justification
return pathlib.Path(certifi.where()).is_file()  # pragma: no cover

# ✅ Correct — block exclusion with comment above
if client is None:  # pragma: no cover
    # Guard unreachable: step-2 renders only after successful connect.
    st.session_state["status"] = ("warning", "Session expired.")

# ❌ Wrong — no justification; reader cannot tell why this is excluded
if foo:  # pragma: no cover
    do_something()
```

**Do NOT add `# pragma: no cover` to lines that are merely inconvenient to test.**
Reserve it for lines that are genuinely unreachable given the project's declared
dependency set and AppTest architecture constraints.

---

## Widget-Component Extraction Guideline (US-084 — Sprint 19)

> **Decision**: [ADR-007 — Widget-Component Extraction Pattern](../architecture/ADR-007-widget-extraction-pattern.md)

`progress_tracker.py`, `query_input.py`, and similar *widget-only* components currently
contain only `st.*` widget calls and are excluded from coverage via `# pragma: no cover`.
If future sprints add **business logic** to these files (input validation, rate limiting,
step-count caps, etc.) that logic **must** be extracted into a pure helper function before
it is implemented, so it remains testable without a live Streamlit runtime.

### The Pattern (established in Sprint 16, confirmed in Sprint 19)

Split every component method into two layers:

| Layer                                                     | What it contains                              | Testable without Streamlit? |
| --------------------------------------------------------- | --------------------------------------------- | --------------------------- |
| **Pure helper** (`_validate_*`, `_build_*`, `_compute_*`) | All business logic; no `st.*` calls           | ✅ Yes — standard `pytest`   |
| **Rendering method** (`render`, `update`, etc.)           | Only `st.*` calls that delegate to the helper | ❌ No — `# pragma: no cover` |

### Worked example — adding a step-count limit to `ProgressTracker`

**Before** (all logic would be inside `# pragma: no cover`):

```python
def update(self, message: str) -> None:  # pragma: no cover
    steps = st.session_state.get(self._SESSION_KEY, [])
    if len(steps) >= 10:           # ← business logic — untestable!
        return
    steps.append(message)
    st.session_state[self._SESSION_KEY] = steps
    with st.status("Generating SQL…", expanded=True) as status:
        for step in steps:
            st.write(step)
```

**After** (pure helper extracted — fully unit-testable):

```python
def _append_step(steps: list[str], message: str, max_steps: int = 10) -> list[str]:
    """Return updated steps list, capped at *max_steps* entries.

    Args:
        steps: Current step messages.
        message: New message to append.
        max_steps: Maximum list length.

    Returns:
        Updated list (unchanged if already at cap).
    """
    if len(steps) >= max_steps:
        return steps
    return steps + [message]


class ProgressTracker:
    def update(self, message: str) -> None:  # pragma: no cover
        """Append step and re-render.

        Excluded from coverage: all statements are ``st.`` calls.
        """
        steps = st.session_state.get(self._SESSION_KEY, [])
        steps = _append_step(steps, message)   # ← delegates to pure helper
        st.session_state[self._SESSION_KEY] = steps
        with st.status("Generating SQL…", expanded=True) as status:
            for step in steps:
                st.write(step)
```

Unit test (no Streamlit required):

```python
from components.progress_tracker import _append_step

def test_append_step_under_cap() -> None:
    result = _append_step(["a", "b"], "c", max_steps=10)
    assert result == ["a", "b", "c"]

def test_append_step_at_cap() -> None:
    result = _append_step(["a"] * 10, "overflow", max_steps=10)
    assert result == ["a"] * 10   # capped — no change
```

### Files currently covered by this guideline

| File                                 | Status                                                | Note                           |
| ------------------------------------ | ----------------------------------------------------- | ------------------------------ |
| `src/components/progress_tracker.py` | Widget-only; no business logic                        | Extract if logic is added      |
| `src/components/query_input.py`      | Widget-only; no business logic                        | Extract if logic is added      |
| `src/components/schema_viewer.py`    | Widget-only; no business logic                        | Extract if logic is added      |
| `src/components/sidebar.py`          | Already extracted (`_validate_*`, `_build_*` helpers) | ✅ Pattern applied in Sprint 16 |
| `src/components/sql_output.py`       | Widget-only; no business logic                        | Extract if logic is added      |
| `src/components/query_history.py`    | `_append_to_history`, `_truncate` extracted           | ✅ Pattern applied in Sprint 20 |
| `src/components/csv_export.py`       | `_result_to_csv`, `_export_filename` extracted        | ✅ Pattern applied in Sprint 20 |

---

## Sprint 20 Components (US-085, US-086)

### `query_history.py` — Session-Scoped Query History

**Pure helpers** (fully unit-tested, no Streamlit dependency):

| Helper               | Signature                                                | Description                                          |
| -------------------- | -------------------------------------------------------- | ---------------------------------------------------- |
| `_append_to_history` | `(history, question, sql, max_entries=10) -> list[dict]` | Prepend, deduplicate by question, cap at max_entries |
| `_truncate`          | `(text, max_len=80) -> str`                              | Truncate text, append '…' if shortened               |

**Widget class**: `QueryHistoryComponent.render(history)` — `# pragma: no cover`  
Renders a `st.expander` with the last N queries and Re-use buttons.

**Session state key**: `st.session_state["query_text"]` is set by Re-use buttons to
pre-populate the `st.text_area(key="query_text")` in `QueryInputComponent`.

### `csv_export.py` — CSV Export

**Pure helpers** (fully unit-tested, no Streamlit dependency):

| Helper             | Signature                     | Description                                       |
| ------------------ | ----------------------------- | ------------------------------------------------- |
| `_result_to_csv`   | `(df: pd.DataFrame) -> bytes` | Serialise DataFrame to UTF-8 CSV bytes (no index) |
| `_export_filename` | `(date_str: str) -> str`      | Build `eng2sql_results_<YYYYMMDD>.csv` filename   |

**Widget class**: `CSVExportComponent.render(df)` — `# pragma: no cover`  
Renders `st.download_button` (or disabled button if DF is empty).


### Pre-commit checklist for widget component changes

Before committing a change to any widget-heavy component:

- [ ] Is new business logic inside a `# pragma: no cover` block? → **Extract it.**
- [ ] Does the extracted helper have a corresponding unit test? → **Add it.**
- [ ] Is the `# pragma: no cover` annotation still the smallest possible scope? → **Verify.**
- [ ] Does `python scripts/pragma_audit.py` still pass? → **Run it.**

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