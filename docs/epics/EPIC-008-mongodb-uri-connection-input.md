# EPIC-008: MongoDB Flexible Connection Input — URI Mode & Individual Fields

## Goal

Give users a **second way to connect to MongoDB** from the Streamlit sidebar: instead
of filling in individual fields (Host, Port, Username, Password, Auth Source, Auth
Mechanism), they can paste a **base MongoDB URI** (without embedded credentials) and
supply the **Username** and **Password** in separate fields. The connector merges the
URI with the credentials before connecting.

Both input modes produce the same result — a valid, authenticated `MongoClient` — so
all downstream behaviour (database discovery, schema detection, MQL generation) is
completely unchanged.

---

## Business Value

- Users who already have a MongoDB connection string (from Atlas, cloud config, a
  DBA, or a `.env` file) can paste it directly without reverse-engineering the
  individual fields. This reduces friction and copy-paste errors.
- The URI mode supports advanced parameters that the individual-field form cannot
  expose (e.g. `replicaSet=`, `tls=true`, `tlsCAFile=`, `readPreference=`, SRV
  scheme `mongodb+srv://`) without requiring additional form fields.
- Keeping credentials out of the URI input ensures that users never accidentally
  embed plaintext passwords in a string they copy from a config file, log, or
  chat message.
- The existing field-by-field mode remains fully available, so no current user
  workflow is broken.

---

## Scope

### In Scope

- **Two input modes in the MongoDB Step 1 form** (toggle / tab in the sidebar):
  - **Mode A — Individual fields** (current behaviour, unchanged):
    Host, Port, Username, Password, Auth Source, Auth Mechanism.
  - **Mode B — URI + credentials**:
    - Text input: `MongoDB URI` — accepts any `mongodb://` or `mongodb+srv://`
      connection string **without** embedded username/password (e.g.
      `mongodb://localhost:27017/?authSource=admin`).
    - Text input: `Username` — merged into the URI at connect time.
    - Password input: `Password` — percent-encoded and merged into the URI.

- **URI parsing & credential injection** (`src/models/config.py` — `MongoConfig`
  or a new `MongoUriConfig` dataclass):
  - Parse the supplied URI with `urllib.parse.urlparse`.
  - If the URI already contains a username/password component, raise a
    `ValueError` with a clear message asking the user to remove credentials from
    the URI and enter them in the dedicated fields.
  - Inject the percent-encoded credentials into the `netloc` portion of the URI
    before passing it to `MongoClient`.
  - If Username is empty, use the URI as-is (unauthenticated or the URI already
    specifies a mechanism the driver will handle).

- **Sidebar UI** (`src/components/sidebar.py`):
  - Add a `st.radio` or `st.selectbox` labelled **"Connection input mode"** with
    options `"Fields"` and `"URI + credentials"`.
  - When **Fields** is selected: render existing Step 1 form (no change).
  - When **URI + credentials** is selected: render URI text box + Username +
    Password fields only (Auth Source / Auth Mechanism derived from the URI).
  - The **Connect** button behaviour is identical in both modes — it calls
    `MongoDBConnector.connect()` with the resolved `MongoConfig` / URI and
    proceeds to Step 2.
  - Persist the selected input mode in `st.session_state["mongo_input_mode"]`
    so it survives Streamlit rerenders.

- **`MongoDBConnector.connect()` overload** (`src/services/mongo_connector.py`):
  - Accept either a `MongoConfig` (fields mode) or a raw URI string (URI mode)
    via a shared interface or an updated method signature.
  - Alternatively, `MongoConfig` gains an optional `raw_uri: str` field; when
    set, `connection_uri` returns the injected URI directly, bypassing the
    field-based URI builder.

- **Validation** at the UI boundary:
  - URI mode: warn if URI starts with `mongodb+srv://` and `directConnection=True`
    is incompatible (SRV URIs cannot use `directConnection`); in that case omit
    `directConnection`.
  - URI mode: detect embedded credentials in the URI and surface a friendly
    `st.warning` rather than passing them through silently.

- **`MongoConfig` update** (`src/models/config.py`):
  - Add optional `raw_uri: str = ""` field.
  - Update `connection_uri` property: when `raw_uri` is non-empty, inject
    credentials and return the merged URI; otherwise use existing field-based
    logic.

- **Unit tests** (`tests/unit/test_mongo_connector.py`):
  - `MongoConfig.connection_uri` with `raw_uri` set, username set — injects
    credentials.
  - `MongoConfig.connection_uri` with `raw_uri` set, username empty — returns
    URI as-is.
  - `MongoConfig.connection_uri` raises `ValueError` when URI already contains
    embedded credentials.
  - `MongoConfig.connection_uri` with SRV URI (`mongodb+srv://`) — credential
    injection preserves SRV scheme.
  - Sidebar form mode toggle — Fields mode renders host/port fields; URI mode
    renders URI field.

- **Documentation**:
  - Update `docs/guides/user-guide.md` — add URI input mode walkthrough with
    example.
  - Update `docs/guides/developer-guide.md` — document `raw_uri` field,
    updated `connection_uri` logic, new session-state key.
  - Update `README.md` — mention URI input mode in feature table.

### Out of Scope

- Saving / recalling previously entered URIs or field sets.
- Parsing or validating every possible MongoDB URI option (replicaSet, tls
  certificates, read preferences) beyond credential injection.
- MySQL URI input mode (deferred; MySQL has its own form).
- Showing a parsed breakdown of the supplied URI to the user.
- Supporting `mongodb+srv://` with embedded credentials (not a supported pattern
  by the MongoDB driver anyway).
- Any changes to the MySQL connection flow.

---

## Acceptance Criteria

```gherkin
Feature: MongoDB Flexible Connection Input

  Scenario AC-1: Mode toggle visible in MongoDB Step 1
    Given the sidebar shows the MongoDB connection form
    When the form is rendered
    Then a "Connection input mode" toggle with "Fields" and "URI + credentials" is visible
    And "Fields" is selected by default

  Scenario AC-2: Fields mode renders existing individual inputs
    Given "Fields" mode is selected
    When Step 1 renders
    Then Host, Port, Username, Password, Auth Source, and Auth Mechanism fields are present
    And no URI text box is shown

  Scenario AC-3: URI + credentials mode renders URI box and credential fields
    Given "URI + credentials" mode is selected
    When Step 1 renders
    Then a "MongoDB URI" text input is shown
    And Username and Password fields are shown
    And Host, Port, Auth Source, Auth Mechanism fields are hidden

  Scenario AC-4: Successful connection via URI mode
    Given the user enters URI "mongodb://localhost:27017/?authSource=admin"
    And enters Username "root" and Password "root"
    When the user clicks Connect
    Then the connector merges credentials into the URI
    And the connection succeeds
    And the database dropdown is populated

  Scenario AC-5: URI without credentials connects unauthenticated
    Given the user enters URI "mongodb://localhost:27017/"
    And leaves Username empty
    When the user clicks Connect
    Then the connector uses the URI as-is
    And the connection proceeds without authentication

  Scenario AC-6: URI with embedded credentials shows warning
    Given the user enters "mongodb://root:root@localhost:27017/"
    When the user clicks Connect
    Then a warning is shown: "Remove credentials from the URI — enter them in the Username/Password fields"
    And no connection attempt is made

  Scenario AC-7: Fields mode connection unchanged
    Given "Fields" mode is selected
    And the user fills in all individual fields
    When Connect is clicked
    Then the connection behaves exactly as in EPIC-007

  Scenario AC-8: SRV URI skips directConnection
    Given the user enters a "mongodb+srv://" URI
    When Connect is clicked
    Then directConnection=True is NOT passed to MongoClient
    And the connection uses the SRV scheme as intended

  Scenario AC-9: Input mode persists across Streamlit rerenders
    Given the user selects "URI + credentials" mode
    When the page rerenders (e.g. after typing in another field)
    Then "URI + credentials" mode remains selected
    And the URI and credential fields retain their values

  Scenario AC-10: Downstream flow unchanged in both modes
    Given a successful connection in either mode
    When the user reaches Step 2
    Then the database dropdown shows the same list
    And schema detection, MQL generation, and schema viewer all work as before
```

---

## Dependencies

- Depends on: EPIC-007 (MongoDB connection foundation — `MongoConfig`,
  `MongoDBConnector`, sidebar MongoDB form)
- Blocks: none

---

## Child User Stories

- [ ] US-031 — Connection Input Mode Toggle in MongoDB Sidebar
- [ ] US-032 — URI + Credentials Mode: URI Parsing & Credential Injection in `MongoConfig`
- [ ] US-033 — URI + Credentials Mode: `directConnection` Suppression for SRV URIs
- [ ] US-034 — Unit Tests for URI Injection and Validation
- [ ] US-035 — Documentation Updates for URI Connection Mode

---

## Effort Estimate

| Story     | Points |
| --------- | ------ |
| US-031    | 3      |
| US-032    | 5      |
| US-033    | 2      |
| US-034    | 3      |
| US-035    | 2      |
| **Total** | **15** |

---

## Sprint Assignment

**Proposed Sprint**: Sprint 7
