# BUG-008: Schema Detection Fails with `Unauthorized` Error When MongoDB Database Contains `system.*` Collections

**Severity**: High
**Sprint**: Backlog (reported 2026-05-07)
**Status**: ✅ Fixed (Bug Fix Agent)
**Reported By**: User (manual testing — 2026-05-07 07:47:26)
**Assigned To**: Bug Fix Agent
**Regression Test**: `tests/unit/test_mongo_schema_detector.py::TestSystemCollectionsAndAuthZ`
**Linked Story**: US-026 (MongoDB Schema Detection), US-031 (URI Connection Input)
**Linked Source**: `src/services/mongo_schema_detector.py`

---

## Description

After successfully connecting to a MongoDB cluster using a multi-host replica-set URI
with credentials (BUG-007 fix), the user sees the database list populate. Selecting a
database (e.g. `idcauditlog`) and clicking **"Select Database"** then fails with a
`SchemaDetectionError` whose root cause is the schema detector trying to sample the
internal `system.profile` collection, for which the application user is not authorised:

```
Failed to sample collection 'system.profile': not authorized on idcauditlog to execute
command { find: "system.profile", filter: {}, limit: 100, ... }
'code': 13, 'codeName': 'Unauthorized'
```

The connection itself is fully healthy — `admin.ping` and `list_collection_names()`
both succeed. Only the per-collection `find()` against `system.profile` is rejected
because reading that collection requires the `dbAdmin` role, which a typical
application user does not have.

This aborts schema detection for the entire database, even though every user-owned
collection in `idcauditlog` is fully readable.

---

## Steps to Reproduce

1. Connect to a MongoDB deployment where the application user has
   `read`/`readWrite` on a database but NOT the `dbAdmin` role, AND
   profiling has been enabled at some point so `system.profile` exists.
2. Use a URI such as
   `mongodb://user:pass@h1:27017,h2:27017,h3:27017/?authSource=db&replicaSet=rs`.
3. Connect successfully — the database list populates.
4. Select the user database from the dropdown.
5. Click **"Select Database"**.

**Expected**: Schema detection completes, listing all user collections and their fields.
**Actual**: `Failed to sample collection 'system.profile': not authorized on <db> …`.

---

## Terminal Log (relevant portion)

```
2026-05-07 07:46:16 [INFO] services.mongo_connector — [5/5] ping : OK ✓ — connected to mongodb://...
2026-05-07 07:46:16 [INFO] components.sidebar — UI: connected to MongoDB via URI; 1 databases found
2026-05-07 07:47:26 [WARNING] components.sidebar — UI: MongoDB database selection failed:
  Failed to sample collection 'system.profile': not authorized on idcauditlog to execute command
  { find: "system.profile", filter: {}, limit: 100, ... } 'code': 13, 'codeName': 'Unauthorized'
```

---

## Root Cause Analysis

`MongoSchemaDetector.detect_schema()` iterates **every** name returned by
`db.list_collection_names()` and calls `db[name].find({}, limit=sample_size)` on each.

MongoDB exposes a number of internal "system" collections under the `system.*` prefix:

| Collection        | Purpose                             | Required role to read |
| ----------------- | ----------------------------------- | --------------------- |
| `system.profile`  | Slow-query profiling output         | `dbAdmin`             |
| `system.views`    | View definitions                    | varies                |
| `system.js`       | Stored server-side JavaScript       | `dbAdmin`             |
| `system.sessions` | Logical session metadata (admin DB) | system                |

A typical `read` / `readWrite` user is **not** authorised to issue `find` against
`system.profile`. When the detector hit `system.profile` it received an
`OperationFailure` with `code: 13 (Unauthorized)`, which the broad `except Exception`
block re-raised as a fatal `SchemaDetectionError`, aborting the entire database load.

A secondary, related risk: if the user lacks read privileges on **any** single
non-system collection, the same fail-fast behaviour would prevent them from working
with the rest of the database.

---

## Fix Applied

**File**: `src/services/mongo_schema_detector.py`

1. **Skip system collections** — added a constant
   `_SYSTEM_COLLECTION_PREFIX = "system."` and filtered the result of
   `list_collection_names()` so any name starting with `system.` is dropped before
   the sampling loop. Skipped names are logged at INFO level for visibility.

2. **Tolerate per-collection authorisation failures** — added
   `_UNAUTHORIZED_MARKERS = ("not authorized", "Unauthorized", "requires authentication")`
   and updated the per-collection `except` branch to detect those markers in the error
   message. When matched, the collection is skipped with a WARNING log and detection
   continues. Any other exception is re-raised as before, preserving fail-fast behaviour
   for genuine errors (driver bugs, network drops, etc.).

This matches MongoDB Compass behaviour, which displays accessible collections and
silently ignores ones the user cannot read.

---

## Tests Added

**File**: `tests/unit/test_mongo_schema_detector.py` — new
`TestSystemCollectionsAndAuthZ` class

| Test                                                                                  | Purpose                                                                                                                                     |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_detect_schema_skips_system_profile`                                             | `system.profile` is filtered out and never sampled                                                                                          |
| `test_detect_schema_skips_all_system_prefixed_collections`                            | All `system.*` names are dropped                                                                                                            |
| `test_detect_schema_user_collections_processed_alongside_system`                      | User collections still processed when `system.*` present                                                                                    |
| `test_detect_schema_skips_collection_on_unauthorized_error`                           | Per-collection "not authorized" → warning + skip, no raise                                                                                  |
| `test_detect_schema_skips_collection_on_lowercase_unauthorized_error`                 | Marker match is substring, not exact                                                                                                        |
| `test_detect_schema_still_raises_on_non_authz_find_failure`                           | Generic find errors still raise `SchemaDetectionError` (no behaviour regression for the existing test)                                      |
| `test_bug_008_regression_system_profile_unauthorized_does_not_block_user_collections` | Exact failing scenario from the report — `system.profile` exists, user has only `read` on user collections, schema is returned successfully |

---

## Verification

```
pytest tests/unit/test_mongo_schema_detector.py -v
```

All new tests pass. Full unit suite remains green. `mongo_schema_detector.py` coverage
remains ≥ 90%.
