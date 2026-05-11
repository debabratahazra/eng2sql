# TC-036-039: Sprint 8 — Quality Hardening Test Cases

**Sprint**: 8
**Agent**: Test Case Writer
**Date**: 2026-05-06
**Stories Covered**: US-036, US-037, US-038, US-039

---

## TC-036: `urllib.parse` Import Location Verification

**Story**: US-036
**Type**: Static Analysis / Inspection

| #    | Scenario                                  | Steps                                                     | Expected Result               | Pass Criteria             |
| ---- | ----------------------------------------- | --------------------------------------------------------- | ----------------------------- | ------------------------- |
| 36.1 | No local urllib import in sidebar.py      | `grep -n "import urllib" src/components/sidebar.py`       | No output (0 matches)         | ✅ No local import present |
| 36.2 | Module-level import in config.py          | `grep -n "import urllib" src/models/config.py`            | Line 4: `import urllib.parse` | ✅ Module-level            |
| 36.3 | Module-level import in mongo_connector.py | `grep -n "import urllib" src/services/mongo_connector.py` | Line 8: `import urllib.parse` | ✅ Module-level            |

---

## TC-037: MongoConfig Coverage Gaps

**Story**: US-037
**Type**: Unit

### TC-037.1 — `__repr__` output

| Field     | Value                                                                                                |
| --------- | ---------------------------------------------------------------------------------------------------- |
| **Given** | A `MongoConfig` instance with `host="myhost"`, `username="myuser"`, `auth_mechanism="SCRAM-SHA-256"` |
| **When**  | `repr(config)` is called                                                                             |
| **Then**  | Result contains `"MongoConfig("`, `"myhost"`, `"myuser"`, and `"SCRAM-SHA-256"`                      |
| **Test**  | `test_mongo_config_repr` in `tests/unit/test_mongo_connector.py`                                     |

### TC-037.2 — `_connection_uri_from_raw` else-branch (empty netloc)

| Field     | Value                                                                                                    |
| --------- | -------------------------------------------------------------------------------------------------------- |
| **Given** | `MongoConfig` with `raw_uri="mongodb:localhost:27017/"`, `username="user"`, `password="pass"`            |
| **When**  | `config.connection_uri` is accessed                                                                      |
| **Then**  | The result contains `"user"` and `"pass"` (credentials injected via path-based netloc fallback)          |
| **Note**  | URI lacking `//` causes `urlparse` to set `netloc=""` and host in `path`; the `else` branch handles this |
| **Test**  | `test_connection_uri_raw_uri_no_netloc_falls_back_to_path`                                               |

---

## TC-038: Streamlit AppTest Sidebar UI Tests

**Story**: US-038
**Type**: UI / Integration (no live DB)

### TC-038.1 — App renders without exception

| Field     | Value                             |
| --------- | --------------------------------- |
| **Given** | `AppTest.from_file("src/app.py")` |
| **When**  | `at.run()` is called              |
| **Then**  | `at.exception` is `None`          |

### TC-038.2 — MySQL is the default DB type

| Field     | Value                          |
| --------- | ------------------------------ |
| **Given** | Fresh `AppTest` instance       |
| **When**  | `at.run()`                     |
| **Then**  | `at.radio[0].value == "MySQL"` |

### TC-038.3 — Connect button visible for MySQL

| Field     | Value                                                 |
| --------- | ----------------------------------------------------- |
| **Given** | Fresh `AppTest` with MySQL selected                   |
| **When**  | `at.run()`                                            |
| **Then**  | A button with label `"Connect"` exists in `at.button` |

### TC-038.4 — Empty MySQL credentials → warning

| Field     | Value                                              |
| --------- | -------------------------------------------------- |
| **Given** | Fresh `AppTest` rendered                           |
| **When**  | `at.button(key="mysql_connect").click().run()`     |
| **Then**  | `at.session_state["step1_status"][0] == "warning"` |

### TC-038.5 — Switch to MongoDB updates db_type

| Field     | Value                                      |
| --------- | ------------------------------------------ |
| **Given** | Rendered app (MySQL)                       |
| **When**  | `at.radio[0].set_value("MongoDB").run()`   |
| **Then**  | `at.session_state["db_type"] == "MongoDB"` |

### TC-038.6 — MongoDB shows connection mode radio

| Field     | Value                                                   |
| --------- | ------------------------------------------------------- |
| **Given** | App with MongoDB selected                               |
| **When**  | `at.run()`                                              |
| **Then**  | A radio with label `"Connection input mode"` is present |

### TC-038.7 — URI mode toggle updates session state

| Field     | Value                                                                         |
| --------- | ----------------------------------------------------------------------------- |
| **Given** | MongoDB mode active                                                           |
| **When**  | `at.radio(key="mongo_input_mode_radio").set_value("URI + credentials").run()` |
| **Then**  | `at.session_state["mongo_input_mode"] == "URI + credentials"`                 |

### TC-038.8 — MongoDB Fields mode is default

| Field     | Value                                                            |
| --------- | ---------------------------------------------------------------- |
| **Given** | App just switched to MongoDB                                     |
| **When**  | `at.run()`                                                       |
| **Then**  | `at.session_state.get("mongo_input_mode", "Fields") == "Fields"` |

### TC-038.9 — Round-trip DB type switch

| Field     | Value                                                |
| --------- | ---------------------------------------------------- |
| **Given** | MySQL → MongoDB → MySQL sequence                     |
| **When**  | Three sequential `at.run()` calls with radio updates |
| **Then**  | Final `at.session_state["db_type"] == "MySQL"`       |

---

## TC-039: `_db_password` Session State Security

**Story**: US-039
**Type**: Security / Unit

### TC-039.1 — Password cleared after successful Step 2

| Field     | Value                                                                               |
| --------- | ----------------------------------------------------------------------------------- |
| **Given** | `_db_password` is set in session state, Step 2 `Select Database` button clicked     |
| **When**  | `create_engine()` and `detect_live_schema()` succeed                                |
| **Then**  | `st.session_state["_db_password"]` is absent (`None` or key not present)            |
| **Note**  | Verified by code inspection of `_render_step2`; test via AppTest + mocked connector |

### TC-039.2 — Password retained after Step 2 failure (retry support)

| Field     | Value                                                                     |
| --------- | ------------------------------------------------------------------------- |
| **Given** | `_db_password` is set, `create_engine()` raises `DatabaseConnectionError` |
| **When**  | Step 2 button clicked                                                     |
| **Then**  | `_db_password` is still present in session state (user can retry)         |

### TC-039.3 — Session expiry warning if password absent at Step 2

| Field     | Value                                                                                       |
| --------- | ------------------------------------------------------------------------------------------- |
| **Given** | `_db_password` is absent from session state, available databases exist                      |
| **When**  | Step 2 `Select Database` button clicked                                                     |
| **Then**  | `step2_status` = `("warning", "Session credentials expired - please reconnect in Step 1.")` |
| **Note**  | Existing behaviour — regression guard                                                       |

---

## Test Execution Checklist

```
pytest tests/unit/test_mongo_connector.py::TestMongoConfig::test_mongo_config_repr -v
pytest tests/unit/test_mongo_connector.py::TestMongoConfig::test_connection_uri_raw_uri_no_netloc_falls_back_to_path -v
pytest tests/unit/test_sidebar_ui.py -v
pytest tests/ -q --cov=src --cov-report=term-missing
```

Expected outcome: all tests pass, coverage ≥ 93%.
