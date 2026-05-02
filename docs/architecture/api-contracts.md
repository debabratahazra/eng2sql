# API Contracts — Eng2SQL Internal Interfaces

> **Purpose**: Defines the precise signatures, inputs, outputs, and error contracts
> for all service and component interfaces. This document is the authoritative reference
> for developers implementing or consuming these interfaces.

---

## Data Models (`src/models/config.py`)

```python
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class DBConfig:
    """Database connection parameters."""
    host: str
    port: int
    user: str
    password: str
    database: str
    dialect: str = "mysql+pymysql"
    connect_timeout: int = 5

    @property
    def connection_url(self) -> str:
        """SQLAlchemy connection URL (password URL-encoded)."""
        ...

@dataclass
class AppConfig:
    """Application-level configuration."""
    openai_api_key: str
    openai_base_url: str = "https://gpt4ifx.icp.infineon.com"
    openai_cert_path: str = "cert/ca-bundle.crt"
    model_name: str = "gpt-5.2"
    schema_config_path: str = "config/database_config.yaml"
    max_tokens: int = 500
    temperature: float = 0.1

@dataclass
class SchemaColumn:
    """A single database column definition."""
    name: str           # Column name (e.g. "customer_id")
    type: str           # Human-readable type string (e.g. "INT", "VARCHAR(200)")
    nullable: bool      # True if NULL values are permitted
    primary_key: bool   # True if column is part of the primary key
    default: str | None = None  # Default value expression, or None

# TableSchema maps table name → ordered list of column definitions
TableSchema = dict[str, list[SchemaColumn]]

@dataclass
class GenerationResult:
    """Result of a SQL generation attempt."""
    sql: str            # The generated SQL SELECT statement
    question: str       # The original English question
    schema_used: TableSchema   # The schema context used during generation
```

---

## Service Interfaces

### `SQLGenerator` (`src/services/sql_generator.py`)

```python
class SQLGenerator:
    def generate_sql(
        self,
        question: str,           # Plain-English question (non-empty)
        schema: TableSchema,     # At least one table required
        dialect: str = "MySQL",  # SQL dialect hint passed to the LLM
    ) -> str:
        """Generate a SQL SELECT statement from a plain-English question.

        Returns:
            A valid SQL SELECT statement with no markdown code fences.

        Raises:
            ValueError: If ``question`` is empty/whitespace or ``schema`` is empty.
            SQLGenerationError: If the OpenAI API call fails, times out, or returns
                                 an empty response.
        """
```

**Notes**:
- The OpenAI client is constructed lazily inside `generate_sql` using `AppConfig`
  sourced from `st.session_state["app_config"]`.
- SQL is stripped of markdown code fences (` ```sql ... ``` `) before returning.
- `temperature=0.1` produces near-deterministic SQL output.

---

### `SchemaDetector` (`src/services/schema_detector.py`)

```python
class SchemaDetector:
    def load_static_schema(
        self,
        config_path: str,   # Path to YAML file (e.g. "config/database_config.yaml")
    ) -> TableSchema:
        """Load schema from a YAML configuration file.

        Returns:
            TableSchema mapping each table name to its ordered column list.

        Raises:
            FileNotFoundError: If the file does not exist at ``config_path``.
            SchemaDetectionError: If the YAML is malformed or missing the "tables" key.
        """

    def detect_live_schema(
        self,
        engine: Engine,     # Active SQLAlchemy engine (MySQL or SQLite)
    ) -> TableSchema:
        """Introspect a live database using SQLAlchemy inspect().

        Returns:
            TableSchema with all tables and columns in the connected database.
            Returns an empty dict if the database has no tables (no error).

        Raises:
            SchemaDetectionError: If table listing or column inspection fails.
        """
```

**Notes**:
- Both methods return the identical `TableSchema` type — the SQL generator treats
  static and live schemas interchangeably.
- `detect_live_schema` uses `inspector.get_pk_constraint()` to populate `primary_key`.
- Column `type` field is always `str(col["type"])` — a human-readable string.

---

### `DBConnector` (`src/services/db_connector.py`)

```python
class DBConnector:
    def create_engine(
        self,
        config: DBConfig,   # Connection parameters including dialect and timeout
    ) -> Engine:
        """Create and verify a SQLAlchemy Engine.

        Executes "SELECT 1" to confirm the connection is live before returning.

        Returns:
            A configured, live SQLAlchemy Engine.

        Raises:
            DatabaseConnectionError: If the connection cannot be established
                                     (wraps OperationalError or SQLAlchemyError).
        """

    def test_connection(
        self,
        engine: Engine,
    ) -> bool:
        """Ping the database with "SELECT 1".

        Returns:
            True if the database responds; False otherwise (never raises).
        """

    def execute_query(
        self,
        engine: Engine,
        sql: str,           # Must be a SELECT statement
    ) -> pd.DataFrame:
        """Execute a read-only SELECT and return results as a DataFrame.

        Returns:
            DataFrame with column names from the query result.
            Returns an empty DataFrame (with column headers) if no rows returned.

        Raises:
            ValueError: If ``sql`` does not start with "SELECT" (case-insensitive).
            QueryExecutionError: If the query fails at the database level.
        """
```

**Notes**:
- `pool_pre_ping=True` ensures stale connections are detected before use.
- `pool_size=2, max_overflow=2` limits concurrent connections to 4 per app instance.
- The engine is stored in `st.session_state["db_engine"]`; callers must not dispose it
  between requests.

---

## Component Interfaces (`src/components/`)

### `SidebarComponent` (`sidebar.py`)

```python
class SidebarComponent:
    def render(self) -> DBConfig | None:
        """Render the sidebar with mode selector and optional DB connection form.

        Returns:
            DBConfig if the user clicked "Connect" and connection succeeded.
            None if in Static Schema mode or connection has not been attempted.

        Side effects:
            Sets st.session_state["db_engine"] on successful connection.
            Calls st.error() on DatabaseConnectionError.
        """
```

### `QueryInputComponent` (`query_input.py`)

```python
class QueryInputComponent:
    def render(self) -> str | None:
        """Render the English query text area and "Generate SQL" button.

        Returns:
            The trimmed question string when "Generate SQL" is clicked and input
            is non-empty.
            None if the button has not been clicked or the text area is empty.
        """
```

### `SQLOutputComponent` (`sql_output.py`)

```python
class SQLOutputComponent:
    def render(self, sql: str) -> None:
        """Render the generated SQL in a syntax-highlighted code block.

        Also renders a "🗑️ Clear" button that resets st.session_state["generated_sql"].
        """
```

### `SchemaViewerComponent` (`schema_viewer.py`)

```python
class SchemaViewerComponent:
    def render(self, schema: TableSchema) -> None:
        """Render a collapsible expander listing all tables and columns.

        Shows a "🔄 Refresh Schema" button that clears st.session_state["detected_schema"]
        and calls st.rerun().
        """
```

### `ProgressTracker` (`progress_tracker.py`)

```python
class ProgressTracker:
    def reset(self) -> None:
        """Clear the current st.status widget from session state."""

    def update(self, message: str) -> None:
        """Append a step message to the active st.status widget."""
```

---

## Exception Hierarchy (`src/utils/exceptions.py`)

```python
Eng2SQLError(Exception)
├── SQLGenerationError      # OpenAI API failure or empty response
├── SchemaDetectionError    # YAML parse failure or SQLAlchemy introspection error
├── QueryExecutionError     # SQL execution failure at the database level
├── DatabaseConnectionError # Engine creation or connection failure
└── ConfigurationError      # Missing or invalid AppConfig / env vars
```

All service boundary exceptions are subclasses of `Eng2SQLError`, allowing callers to
catch `Eng2SQLError` for broad handling or specific subclasses for targeted recovery.

---

## Session State Keys (`st.session_state`)

| Key               | Type                   | Set By                    | Consumed By                             |
| ----------------- | ---------------------- | ------------------------- | --------------------------------------- |
| `app_config`      | `AppConfig`            | `app.py` (startup)        | `SQLGenerator`                          |
| `db_engine`       | `Engine \| None`       | `SidebarComponent`        | `SchemaDetector`, `DBConnector`         |
| `detected_schema` | `TableSchema \| None`  | `app.py` after connection | `SQLGenerator`, `SchemaViewerComponent` |
| `generated_sql`   | `str \| None`          | `app.py` after generation | `SQLOutputComponent`                    |
| `query_result`    | `pd.DataFrame \| None` | `app.py` after execution  | `app.py` (`st.dataframe`)               |
| `mode`            | `str`                  | `SidebarComponent`        | `app.py` (branch logic)                 |
