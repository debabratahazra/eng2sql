# EPIC-006: Live Database Connection — Database Discovery & Selector

## Goal

Replace the static-vs-live schema radio button with a **MySQL-only live connection
flow** in the Streamlit sidebar. After the user supplies host, port, username, and
password and clicks **Connect**, the application fetches the list of databases
available on that MySQL server and presents them in a dropdown. Clicking
**Select Database** finalises the connection to the chosen database, invalidates
any previously cached schema, and makes the main window ready for English-to-SQL
generation against the live schema.

---

## Business Value

- Removes the static YAML schema concept from the UI, eliminating confusion about
  which mode is active and reducing maintenance burden.
- Users no longer need to know or type the exact database name before connecting —
  they browse the live list and pick from real names.
- Provides a natural two-step flow (connect to server → pick database) that matches
  how DBAs and analysts think about MySQL connections.
- Lays the groundwork for multi-database support and future additional database
  engines (PostgreSQL, MSSQL — deferred to future epics).

---

## Scope

### In Scope

- Remove the `"Static Schema"` radio option from the sidebar; the only option is
  **MySQL Live Database**.
- Two-step connection flow in the sidebar:
  1. **Step 1 — Server credentials**: host, port, username, password →
     **Connect** button → fetches available database names.
  2. **Step 2 — Database selection**: dropdown listing all discovered databases →
     **Select Database** button → connects engine to the chosen database.
- `DBConnector.list_databases(engine)` new method: executes `SHOW DATABASES;` and
  returns a `list[str]` (filtered to exclude system databases:
  `information_schema`, `performance_schema`, `mysql`, `sys`).
- `DBConfig` no longer requires `database` at engine-creation time for Step 1
  (connect without a named database to enumerate, then reconnect to the chosen one).
- Session-state keys introduced: `db_server_engine`, `available_databases`,
  `selected_database`.
- Remove dead code paths in `app.py` and `sidebar.py` related to static schema
  mode (YAML loading on the main page).
- Update `docs/guides/user-guide.md` to reflect the new two-step connection flow.
- Update `docs/guides/developer-guide.md` to document the new service method and
  session-state keys.
- Update `README.md` to remove static schema references.

### Out of Scope

- Support for PostgreSQL, MSSQL, Oracle, SQLite as live connection targets
  (deferred to a future epic — the radio button placeholder is removed now).
- User authentication beyond username/password (SSL client certs, IAM tokens).
- Saving / remembering previously used connection profiles.
- Showing or filtering database names beyond excluding the four system schemas.
- Schema caching to disk.

---

## Acceptance Criteria

```gherkin
Feature: Live Database Connection — Database Discovery & Selector

  Scenario AC-1: Static Schema option is removed
    Given the Streamlit sidebar is rendered
    Then there is no "Static Schema" radio option
    And the sidebar shows only "MySQL Live Database" as the connection type

  Scenario AC-2: Step 1 — Connect to server and discover databases
    Given the user fills in host, port, username, and password
    When the user clicks "Connect"
    Then the application connects to the MySQL server without specifying a database
    And a dropdown appears listing all non-system databases available on the server
    And a status message shows "✅ Connected to <host> — <N> databases found"

  Scenario AC-3: Step 2 — Select a database and activate it
    Given a list of databases is shown in the dropdown
    When the user selects a database name and clicks "Select Database"
    Then a new engine is created connected to the chosen database
    And the selected database name is saved in session state
    And the schema is auto-detected for the selected database
    And the main window shows the schema viewer and is ready for SQL generation

  Scenario AC-4: Invalid credentials show an error
    Given the user supplies wrong username or password
    When the user clicks "Connect"
    Then an error message appears: "❌ Connection failed: …"
    And no dropdown is shown

  Scenario AC-5: No accessible databases shows an informational message
    Given the MySQL user has no SHOW DATABASES privilege or no non-system DBs exist
    When the user clicks "Connect"
    Then a warning shows "⚠️ No accessible databases found for this user"
    And the Select Database button is disabled

  Scenario AC-6: Changing server credentials resets the database selection
    Given the user has already selected a database
    When the user modifies the host, port, user, or password field
    Then the database dropdown and selected database are cleared from session state
    And the user must click "Connect" again

  Scenario AC-7: list_databases excludes system databases
    Given a MySQL server with databases: information_schema, performance_schema,
      mysql, sys, myapp_db, analytics_db
    When DBConnector.list_databases(engine) is called
    Then the returned list contains only ["myapp_db", "analytics_db"]
    And system databases are excluded
```

---

## Technical Design Notes

### New `DBConnector.list_databases(engine)` method

```python
def list_databases(self, engine: Engine) -> list[str]:
    """Return non-system database names from the connected MySQL server."""
    _SYSTEM_DBS = frozenset({"information_schema", "performance_schema", "mysql", "sys"})
    with engine.connect() as conn:
        rows = conn.execute(text("SHOW DATABASES")).fetchall()
    return [row[0] for row in rows if row[0] not in _SYSTEM_DBS]
```

### `DBConfig` change for Step 1

`DBConfig.database` defaults to `""` (empty string). When empty, the SQLAlchemy
URL becomes `mysql+pymysql://user:pass@host:port/` — valid for a server-level
connection that can execute `SHOW DATABASES`.

### Sidebar session-state keys

| Key                   | Type                  | Description                                                                    |
| --------------------- | --------------------- | ------------------------------------------------------------------------------ |
| `db_server_engine`    | `Engine \| None`      | Engine connected at server level (Step 1 result)                               |
| `available_databases` | `list[str]`           | Databases returned by `list_databases()`                                       |
| `selected_database`   | `str`                 | Database name chosen in the dropdown                                           |
| `db_engine`           | `Engine \| None`      | Engine connected to the chosen database (Step 2 result — existing key, reused) |
| `detected_schema`     | `TableSchema \| None` | Schema of the selected database (existing key, reused)                         |

### Removed session-state keys

| Key    | Reason                           |
| ------ | -------------------------------- |
| `mode` | No longer needed — only one mode |

---

## Dependencies

- **Depends on**: EPIC-003 (live schema detection, `DBConnector`, `SchemaDetector`)
- **Depends on**: EPIC-002 (Streamlit sidebar component)
- **Blocks**: None (standalone UX improvement)

---

## Estimated Size

**T-Shirt Size**: M
**Estimated Sprints**: 1 (Sprint 5)

---

## Child User Stories

- [x] US-021: Remove Static Schema Mode & MySQL-Only Sidebar
- [x] US-022: Step 1 — Server Connect & Database Discovery
- [x] US-023: Step 2 — Database Selector & Engine Activation
- [x] US-024: `DBConnector.list_databases()` Service Method & Unit Tests

---

## Status

- [x] Draft
- [x] Reviewed
- [x] Accepted
- [x] ✅ Complete — Sprint 5 (2026-05-02)
