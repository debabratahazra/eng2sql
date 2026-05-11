# Sprint 7 Plan

**Goal**: Add URI + credentials input mode to the MongoDB connection form — users can paste a full `mongodb://` or `mongodb+srv://` URI alongside separate username/password fields, removing the need to decompose connection strings into individual fields.
**Duration**: 2026-05-15 → 2026-05-28 (2 weeks)
**Velocity Target**: 15 points
**Epic**: EPIC-008 — MongoDB Flexible Connection Input

---

## Committed Stories

| Story ID | Title                                                      | Points | Assignee (Agent) |
| -------- | ---------------------------------------------------------- | ------ | ---------------- |
| US-031   | Connection Input Mode Toggle in MongoDB Sidebar            | 3      | Developer        |
| US-032   | URI + Credentials Mode: URI Parsing & Credential Injection | 5      | Developer        |
| US-033   | URI Mode: `directConnection` Suppression for SRV URIs      | 2      | Developer        |
| US-034   | Unit Tests for URI Injection and Validation                | 3      | Developer        |
| US-035   | Documentation Updates for URI Connection Mode              | 2      | Developer        |

**Total**: 15 points

---

## Definition of Done

- [x] `MongoConfig.raw_uri` field added to `src/models/config.py`
- [x] `MongoConfig.connection_uri` branches on `raw_uri`: injects credentials when set, falls back to field-based logic when empty
- [x] Embedded-credentials guard in `connection_uri` raises `ValueError`
- [x] `MongoDBConnector.connect()` omits `directConnection=True` for SRV URIs
- [x] `_render_mongo_step1()` in `src/components/sidebar.py` shows mode radio; URI branch renders URI + Username + Password only
- [x] `st.session_state["mongo_input_mode"]` persisted across rerenders
- [x] All new unit tests pass (`test_mongo_connector.py`)
- [x] `pytest --cov=src --cov-fail-under=80` passes
- [x] `docs/guides/user-guide.md` updated — URI mode walkthrough added
- [x] `docs/guides/developer-guide.md` updated — `raw_uri`, `mongo_input_mode`, SRV note documented
- [x] `README.md` capability table updated

---

## Sprint Risks

| Risk                                                                                   | Likelihood | Impact | Mitigation                                                           |
| -------------------------------------------------------------------------------------- | ---------- | ------ | -------------------------------------------------------------------- |
| `urllib.parse.urlparse` behaves differently for `mongodb+srv://` (non-standard scheme) | Medium     | Medium | Test SRV URIs explicitly; use string prefix check for SRV detection  |
| Users paste URIs with embedded credentials despite the warning                         | Low        | Low    | ValueError + `st.warning` block the connect; no connection attempted |
| `directConnection=True` + SRV causes driver error on Atlas                             | Medium     | High   | Detect SRV in `connect()` and suppress `directConnection`            |
| Existing field-mode tests break if `raw_uri` default changes `connection_uri` output   | Low        | Medium | Default `raw_uri=""` preserves existing path; regression tests added |

---

## Session State Changes

### Added in Sprint 7

| Key                | Type  | Set By             | Description                             |
| ------------------ | ----- | ------------------ | --------------------------------------- |
| `mongo_input_mode` | `str` | Sidebar mode radio | `"Fields"` or `"URI + credentials"`     |
| `mongo_raw_uri`    | `str` | Sidebar URI field  | Persisted raw URI value (non-sensitive) |

### Unchanged

All Sprint 6 keys (`mongo_client`, `mongo_available_databases`, `mongo_selected_database`, `mongo_db`, `detected_schema`, `db_type`) unchanged.
