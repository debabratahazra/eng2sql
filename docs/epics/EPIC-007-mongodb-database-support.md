# EPIC-007: MongoDB Database Support

## Goal

Extend the Streamlit sidebar to support **MongoDB** as a second live-database engine
alongside MySQL. A radio button lets the user choose between MySQL and MongoDB; the
connection form fields update dynamically based on that choice. After connecting, the
app discovers and lists all user-accessible databases in a dropdown, finalises the
connection to the selected database, auto-detects its schema (collections + sampled
fields), and feeds that schema to the SQL/MQL generator so that English queries work
against a live MongoDB instance.

---

## Business Value

- Opens the application to teams and data analysts who work primarily with MongoDB,
  without requiring any changes to their existing infrastructure.
- Single tool for both relational and document databases eliminates the need to
  switch between different query-translation utilities.
- Consistent two-step connection UX (connect to server → pick database) that users
  already know from the MySQL flow reduces the learning curve.
- Provides a natural extension point for additional database engines (PostgreSQL,
  MSSQL, Redis) in future epics.

---

## Scope

### In Scope

- **DB-type radio selector** at the top of the sidebar Configuration section:
  - Options: `MySQL` | `MongoDB`
  - Selecting a different option clears all downstream session-state keys and
    re-renders the connection form immediately.

- **MySQL form** (unchanged from EPIC-006):
  - Fields: Host, Port (default 3306), User, Password → **Connect** button
  - Step 2: database dropdown → **Select Database** button

- **MongoDB form** (new):
  - Fields: Host (default `localhost`), Port (default `27017`), Username,
    Password, Auth Source (default `admin`), Auth Mechanism (selectbox:
    `SCRAM-SHA-256` | `SCRAM-SHA-1` | `MONGODB-X509` | `None / No Auth`)
  - **Connect** button: connects to the MongoDB server without specifying a
    database; calls `MongoDBConnector.list_databases(client)` to retrieve
    available database names.
  - Step 2: dropdown listing discovered databases (system databases `admin`,
    `local`, `config` excluded by default) → **Select Database** button:
    finalises connection, detects collection schema.

- **`MongoConfig` dataclass** in `src/models/config.py`:
  - Fields: `host`, `port`, `username`, `password`, `auth_source`,
    `auth_mechanism`, `connect_timeout_ms`
  - Property `connection_uri` returning a properly-encoded `mongodb://…` URI
    (password percent-encoded via `urllib.parse.quote_plus`).

- **`MongoDBConnector` service** in `src/services/mongo_connector.py`:
  - `connect(config: MongoConfig) -> MongoClient` — creates and validates a
    `pymongo.MongoClient`; raises `DatabaseConnectionError` on failure.
  - `list_databases(client: MongoClient) -> list[str]` — calls
    `client.list_database_names()` and filters out `admin`, `local`, `config`.
  - `get_database(client: MongoClient, name: str) -> Database` — returns the
    named `pymongo.database.Database` object.

- **`MongoSchemaDetector` service** in `src/services/mongo_schema_detector.py`:
  - `detect_schema(db: Database, sample_size: int = 100) -> TableSchema` —
    for each collection, samples up to `sample_size` documents, unions the
    top-level field names, infers a best-effort BSON type string, and returns a
    `TableSchema` (collections are treated as "tables", top-level fields as
    "columns").

- **Sidebar updates** (`src/components/sidebar.py`):
  - Add radio button for `db_type` at the top of the form
    (`st.radio("Database type", ["MySQL", "MongoDB"])`).
  - Branch rendering logic: MySQL path = current two-step flow; MongoDB path =
    new `_render_mongo_step1()` / `_render_mongo_step2()` methods.
  - New session-state keys introduced:
    - `db_type` — `"MySQL"` or `"MongoDB"`
    - `mongo_client` — live `MongoClient` (Step 1)
    - `mongo_available_databases` — `list[str]` (Step 1)
    - `mongo_selected_database` — chosen database name (Step 2)
    - `mongo_db` — `pymongo.database.Database` object (Step 2)
    - `mongo_auth_source`, `mongo_auth_mechanism` — persisted form values

- **App updates** (`src/app.py`):
  - Read `db_type` from session state to determine which schema + engine
    object to forward to the SQL generator.
  - When `db_type == "MongoDB"`: pass `detected_schema` (populated by
    `MongoSchemaDetector`) to `SQLGenerator`; indicate in the prompt that the
    target dialect is MQL / MongoDB aggregation pipeline rather than MySQL.
  - All existing MySQL code paths remain unchanged.

- **SQL Generator prompt update** (`src/services/sql_generator.py`):
  - Accept an optional `dialect: str` parameter (default `"MySQL"`).
  - When `dialect == "MongoDB"`, instruct the LLM to return a MongoDB
    aggregation pipeline or `db.collection.find()` statement instead of SQL.

- **Documentation**:
  - Update `docs/guides/user-guide.md` — add MongoDB connection walkthrough.
  - Update `docs/guides/developer-guide.md` — document `MongoConfig`,
    `MongoDBConnector`, `MongoSchemaDetector`, session-state keys, and
    dialect parameter.
  - Update `README.md` — list `pymongo` as a new dependency and add MongoDB
    connection example.
  - Update `requirements.txt` — add `pymongo>=4.7`.

### Out of Scope

- MongoDB Atlas (SRV connection strings) — deferred to a future epic.
- TLS / SSL client-certificate authentication for MongoDB.
- Saving or recalling previously used MongoDB connection profiles.
- Execution of generated MQL against the live MongoDB connection (query
  execution for MySQL is already implemented; MongoDB execution deferred).
- Support for nested / embedded document fields beyond the top level in schema
  detection.
- PostgreSQL, MSSQL, Oracle, Redis, or other database engines.
- Schema caching to disk.

---

## Acceptance Criteria

```gherkin
Feature: MongoDB Database Support — Sidebar Radio Selector & Connection Flow

  Scenario AC-1: Radio button renders in sidebar
    Given the Streamlit app is loaded
    When the sidebar is rendered
    Then a "Database type" radio with options "MySQL" and "MongoDB" is visible
    And the default selection is "MySQL"

  Scenario AC-2: Switching to MongoDB updates the connection form
    Given the sidebar shows the MySQL form
    When the user selects "MongoDB" in the radio
    Then the Port field changes to 27017
    And Auth Source and Auth Mechanism fields appear
    And the MySQL-specific fields (Port 3306) are replaced by MongoDB-specific fields

  Scenario AC-3: Switching database type clears downstream state
    Given the user is connected to a MySQL server with databases listed
    When the user switches the radio to "MongoDB"
    Then all MySQL session-state keys are cleared
    And the database dropdown disappears until a new MongoDB connection is made

  Scenario AC-4: MongoDB Step 1 — Connect and list databases
    Given the user selects "MongoDB" and fills in host, port, username, password
    When the user clicks "Connect"
    Then the app connects to the MongoDB server
    And a dropdown listing all non-system databases appears
    And a status message shows "✅ Connected to <host> — <N> databases found"

  Scenario AC-5: MongoDB Step 1 — Connection failure shows error
    Given the user provides invalid MongoDB credentials
    When the user clicks "Connect"
    Then an error message is displayed
    And no database dropdown appears

  Scenario AC-6: MongoDB Step 2 — Select database and detect schema
    Given the MongoDB server is connected and databases are listed
    When the user selects a database and clicks "Select Database"
    Then the app connects to that specific database
    And the schema viewer displays the collections and sampled fields
    And a status message shows "✅ <database> selected — <N> collections detected"

  Scenario AC-7: No-auth MongoDB connection
    Given the user selects "None / No Auth" in Auth Mechanism
    When the user clicks "Connect" with host and port filled
    Then the app connects without credentials
    And database discovery proceeds normally

  Scenario AC-8: SQL Generator uses MongoDB dialect
    Given the user is connected to a MongoDB database with schema detected
    When the user types an English query and submits
    Then the LLM is prompted with MongoDB dialect instructions
    And the output panel displays a MongoDB find() or aggregation pipeline
    And the step-by-step progress tracker reflects the MongoDB query generation

  Scenario AC-9: MySQL flow is unaffected
    Given the radio is set to "MySQL"
    Then the existing two-step MySQL flow behaves exactly as before
    And no MongoDB session-state keys are written

  Scenario AC-10: System databases excluded from MongoDB dropdown
    Given the MongoDB server has databases: admin, local, config, mydb, analytics
    When the user connects and databases are listed
    Then only "mydb" and "analytics" appear in the dropdown
    And "admin", "local", "config" are excluded
```

---

## Dependencies

- Depends on: EPIC-006 (MySQL two-step connection flow, which this epic extends)
- Blocks: none

---

## New Dependencies (Python Packages)

| Package   | Version          | Purpose                                                      |
| --------- | ---------------- | ------------------------------------------------------------ |
| `pymongo` | `>=4.7`          | MongoDB driver — client, database listing, collection access |
| `motor`   | optional, future | Async MongoDB driver (deferred)                              |

---

## New Files

| File                                       | Description                                |
| ------------------------------------------ | ------------------------------------------ |
| `src/models/config.py`                     | Add `MongoConfig` dataclass                |
| `src/services/mongo_connector.py`          | New — `MongoDBConnector` class             |
| `src/services/mongo_schema_detector.py`    | New — `MongoSchemaDetector` class          |
| `tests/unit/test_mongo_connector.py`       | New — unit tests for `MongoDBConnector`    |
| `tests/unit/test_mongo_schema_detector.py` | New — unit tests for `MongoSchemaDetector` |

## Modified Files

| File                             | Change                                                    |
| -------------------------------- | --------------------------------------------------------- |
| `src/components/sidebar.py`      | Add radio, MongoDB step 1 & 2 render methods              |
| `src/app.py`                     | Branch on `db_type` for schema/engine selection + dialect |
| `src/services/sql_generator.py`  | Add `dialect` parameter to generation method              |
| `requirements.txt`               | Add `pymongo>=4.7`                                        |
| `docs/guides/user-guide.md`      | MongoDB connection walkthrough                            |
| `docs/guides/developer-guide.md` | New services, models, session-state keys                  |
| `README.md`                      | New dependency note + MongoDB usage example               |

---

## Session-State Key Reference

| Key                         | Type          | Set by         | Description                          |
| --------------------------- | ------------- | -------------- | ------------------------------------ |
| `db_type`                   | `str`         | Sidebar radio  | `"MySQL"` or `"MongoDB"`             |
| `mongo_client`              | `MongoClient` | Step 1 Connect | Server-level client (no DB selected) |
| `mongo_available_databases` | `list[str]`   | Step 1 Connect | Filtered database names              |
| `mongo_selected_database`   | `str`         | Step 2 Select  | Chosen database name                 |
| `mongo_db`                  | `Database`    | Step 2 Select  | `pymongo.database.Database` object   |
| `mongo_auth_source`         | `str`         | Step 1 form    | Persisted auth source value          |
| `mongo_auth_mechanism`      | `str`         | Step 1 form    | Persisted auth mechanism value       |

---

## Estimated Size

**T-Shirt Size**: L
**Estimated Sprints**: 1 (Sprint 6)

---

## Child User Stories

<!-- User Story Writer will populate this section -->
- [ ] US-025: MongoDB Connection Form in Sidebar (radio + Step 1 fields + Connect)
- [ ] US-026: MongoDB Database Discovery & Selection (Step 2 dropdown + Select)
- [ ] US-027: MongoDBConnector Service (`connect`, `list_databases`, `get_database`)
- [ ] US-028: MongoSchemaDetector Service (collection sampling → `TableSchema`)
- [ ] US-029: SQL Generator MongoDB Dialect (dialect param + MQL prompt)
- [ ] US-030: Unit & Integration Tests for MongoDB Services

---

## Status

- [x] Draft
- [ ] Reviewed
- [ ] Accepted
