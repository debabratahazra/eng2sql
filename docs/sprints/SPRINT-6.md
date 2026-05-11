# Sprint 6 Plan

**Goal**: Add MongoDB as a second live-database engine — radio selector in sidebar, two-step MongoDB connection flow, MongoDBConnector and MongoSchemaDetector services, MongoDB dialect in query generator
**Duration**: 2026-07-15 → 2026-07-28 (2 weeks)
**Velocity Target**: 28 points
**Epic**: EPIC-007 — MongoDB Database Support

---

## Committed Stories

| Story ID | Title                                         | Points | Assignee (Agent) |
| -------- | --------------------------------------------- | ------ | ---------------- |
| US-025   | MongoDB Connection Form in Sidebar            | 5      | Developer        |
| US-026   | MongoDB Database Discovery & Selection        | 5      | Developer        |
| US-027   | `MongoDBConnector` Service                    | 5      | Developer        |
| US-028   | `MongoSchemaDetector` Service                 | 5      | Developer        |
| US-029   | SQL Generator MongoDB Dialect                 | 3      | Developer        |
| US-030   | Unit & Integration Tests for MongoDB Services | 5      | Developer        |

**Total**: 28 points

---

## Definition of Done

- [x] `MongoConfig` dataclass added to `src/models/config.py`
- [x] `src/services/mongo_connector.py` implemented: `connect()`, `list_databases()`, `get_database()`
- [x] `src/services/mongo_schema_detector.py` implemented: `detect_schema()`
- [x] Sidebar radio "Database type" with MySQL / MongoDB options
- [x] MongoDB Step 1: credentials form + Connect → database list
- [x] MongoDB Step 2: database dropdown + Select Database → schema detected
- [x] `app.py` branches on `db_type`; passes `dialect="MongoDB"` to generator when MongoDB active
- [x] Execute SQL button hidden when `db_type == "MongoDB"`
- [x] `tests/unit/test_mongo_connector.py` — all tests pass
- [x] `tests/unit/test_mongo_schema_detector.py` — all tests pass
- [x] `ruff check` and `mypy src/` both exit 0
- [x] `pytest --cov=src --cov-fail-under=80` passes
- [x] `docs/guides/user-guide.md` updated — MongoDB connection walkthrough added
- [x] `docs/guides/developer-guide.md` updated — new services, models, session-state keys
- [x] `README.md` updated — `pymongo` dependency noted, MongoDB usage example added
- [x] `requirements.txt` updated — `pymongo>=4.7` added
- [x] Code review completed (CR-006)

---

## Sprint Risks

| Risk                                                           | Likelihood | Impact | Mitigation                                                                             |
| -------------------------------------------------------------- | ---------- | ------ | -------------------------------------------------------------------------------------- |
| `pymongo` not installed in dev environment                     | Medium     | High   | Add `pymongo>=4.7` to `requirements.txt`; raise clear `ImportError` message if missing |
| MongoDB Atlas SRV strings not supported                        | Low        | Medium | Document limitation in user guide; defer Atlas support to future epic                  |
| `list_database_names()` requires `listDatabases` privilege     | Medium     | Medium | Show `st.warning("⚠️ No accessible databases found")` on empty result                   |
| Switching db_type mid-session leaves stale schema in state     | Medium     | Low    | `_clear_all_state()` clears both MySQL and MongoDB keys on type switch                 |
| Schema detection on large collections is slow (many documents) | Low        | Medium | Default `sample_size=100`; show `st.spinner` during detection                          |
| Unit tests for pymongo require careful MagicMock setup         | Medium     | Low    | Use `spec=MongoClient` in MagicMock to catch attribute errors early                    |

---

## Session State Changes

### Added in Sprint 6

| Key                         | Type                  | Set By                          | Description                               |
| --------------------------- | --------------------- | ------------------------------- | ----------------------------------------- |
| `db_type`                   | `str`                 | Sidebar radio                   | `"MySQL"` or `"MongoDB"`                  |
| `mongo_client`              | `MongoClient \| None` | US-026 — Step 1 Connect click   | Server-level MongoClient (no DB selected) |
| `mongo_available_databases` | `list[str]`           | US-026 — after list_databases() | Non-system databases on the server        |
| `mongo_selected_database`   | `str`                 | US-026 — Step 2 Select click    | Database name chosen in dropdown          |
| `mongo_db`                  | `Database \| None`    | US-026 — Step 2 Select click    | pymongo Database object                   |
| `mongo_auth_source`         | `str`                 | US-025 — form persistence       | Persisted auth source value               |
| `mongo_auth_mechanism`      | `str`                 | US-025 — form persistence       | Persisted auth mechanism selection        |

### Unchanged

| Key               | Used By                                             |
| ----------------- | --------------------------------------------------- |
| `db_engine`       | MySQL flow — full SQLAlchemy engine (Step 2 result) |
| `detected_schema` | Both flows — shared schema key for SQL generator    |
| `generated_sql`   | app.py                                              |
| `query_result`    | app.py (MySQL only)                                 |

---

## Architecture Notes

```
Sidebar
  └── radio: db_type
        ├── "MySQL"  → _render_step1() / _render_step2()   [existing]
        └── "MongoDB"→ _render_mongo_step1() / _render_mongo_step2()  [new]

MongoDBConnector
  ├── connect(MongoConfig) -> MongoClient
  ├── list_databases(MongoClient) -> list[str]
  └── get_database(MongoClient, str) -> Database

MongoSchemaDetector
  └── detect_schema(Database, sample_size) -> TableSchema

app.py
  ├── db_type == "MySQL"  → engine=db_engine, dialect="MySQL"
  └── db_type == "MongoDB"→ schema from mongo detection, dialect="MongoDB"
```

## Outcome
_To be filled after sprint completion._

