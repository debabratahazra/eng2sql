# BUG-005: URI Mode — Topology Timeout When Connecting to Local MongoDB

**Severity**: High
**Sprint**: Sprint 7 (found post-release)
**Status**: ✅ Fixed
**Reported By**: User (manual testing — 2026-05-02 17:49:11)
**Assigned To**: Developer Agent
**Regression Test**: `tests/unit/test_mongo_connector.py::TestMongoConfig::test_uri_mode_with_database_path_injects_credentials`
**Linked Story**: US-031 — Connection Input Mode Toggle, US-032 — URI Credential Injection
**Linked Source**: `src/services/mongo_connector.py`, `src/models/config.py`

---

## Description

When the user enters a `mongodb://` URI that contains a **database path component**
(e.g. `mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false`) in the
"URI + credentials" input mode, the connection fails with a topology selection timeout:

```
[WARNING] components.sidebar — UI: MongoDB URI connection failed:
Could not connect to MongoDB at mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false
- No servers found yet, Timeout: 5.0s,
  Topology Description: <TopologyDescription id: ..., topology_type: Single,
  servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None>]>
```

The server-side MongoDB instance **is running** — the root cause is an
IPv4 / IPv6 address-resolution mismatch.

---

## Root Cause Analysis

### Primary cause — IPv4 vs IPv6 `localhost` on Windows

On Windows (and some Linux configurations), the name `localhost` can resolve to the
IPv6 loopback address `::1` rather than the IPv4 loopback `127.0.0.1`.  MongoDB is
commonly bound to `127.0.0.1:27017` only.  pymongo sends the initial hello/isMaster
handshake to `[::1]:27017`, receives no response (nothing listening on IPv6), and
reports `server_type: Unknown` after the `serverSelectionTimeoutMS` elapses.

### Contributing factor — opaque error message

The current error message repeats the raw pymongo exception verbatim. It does not
tell the user to try `127.0.0.1` instead of `localhost`, nor does it explain what
`topology_type: Single` or `server_type: Unknown` means.

### What is working correctly

- Credential injection: `mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false` ✅
- Database path preserved after injection (`idcauditlog` in path) ✅
- `directConnection=True` is passed to `MongoClient` for all `mongodb://` URIs ✅
- `ssl=false` is honoured by pymongo 4.x (`_ssl_context=None`) ✅
- Error message uses `raw_uri` (no credentials exposed in logs) ✅

---

## Steps to Reproduce

1. Start the Streamlit app: `streamlit run src/app.py`
2. Select **MongoDB** as the database type.
3. In Step 1, choose **"URI + credentials"** mode.
4. Enter:
   - **MongoDB URI**: `mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false`
   - **Username**: `root`
   - **Password**: `root`
5. Click **Connect**.

**Expected**: Successful connection (MongoDB is running locally).  
**Actual**: Topology timeout — `No servers found yet, Timeout: 5.0s`.

---

## Fix

### Code fix — `src/services/mongo_connector.py`

Added `MongoDBConnector._normalise_localhost(uri)` — a static method that uses
`urllib.parse` to rewrite the host component from `localhost` to `127.0.0.1`
**before** the URI is passed to `MongoClient`.  This transparently resolves the
IPv4 / IPv6 ambiguity without requiring any user action.

The normalisation is applied in `connect()` after `config.connection_uri` is
retrieved but before the `MongoClient(...)` call:

```python
uri_for_client = self._normalise_localhost(uri)
client = MongoClient(
    uri_for_client,
    serverSelectionTimeoutMS=config.connect_timeout_ms,
    **({"directConnection": True} if use_direct else {}),
)
```

Error messages still report `config.raw_uri` (the user's original `localhost`
URI) so credentials are never leaked in logs.

### User workaround (still valid if needed)

Replace `localhost` with `127.0.0.1` in the URI manually:

```
mongodb://127.0.0.1:27017/idcauditlog?authSource=admin&ssl=false
```

---

## Test Cases Added

| Test                                                       | File                      | Purpose                                                          |
| ---------------------------------------------------------- | ------------------------- | ---------------------------------------------------------------- |
| `test_normalise_localhost_replaces_with_ipv4`              | `test_mongo_connector.py` | `_normalise_localhost` rewrites `localhost` → `127.0.0.1`        |
| `test_normalise_localhost_no_auth_uri`                     | `test_mongo_connector.py` | Works for URIs without credentials                               |
| `test_normalise_localhost_leaves_ipv4_unchanged`           | `test_mongo_connector.py` | `127.0.0.1` URIs are not altered                                 |
| `test_normalise_localhost_leaves_non_local_host_unchanged` | `test_mongo_connector.py` | Remote hosts are not altered                                     |
| `test_normalise_localhost_leaves_srv_unchanged`            | `test_mongo_connector.py` | SRV URIs are not altered                                         |
| `test_uri_mode_with_database_path_injects_credentials`     | `test_mongo_connector.py` | Credentials injected + path + query params preserved             |
| `test_connect_localhost_uri_uses_127_0_0_1`                | `test_mongo_connector.py` | `connect()` calls `MongoClient` with `127.0.0.1` not `localhost` |
| `test_connect_localhost_error_shows_original_uri_not_127`  | `test_mongo_connector.py` | Error message uses original `localhost` URI (no credential leak) |

---

## Definition of Done

- [x] Root cause documented
- [x] `src/services/mongo_connector.py` — `_normalise_localhost()` auto-converts `localhost` → `127.0.0.1` before `MongoClient` call
- [x] Eight regression tests passing in `tests/unit/test_mongo_connector.py`
- [x] `pytest --cov-fail-under=80` exits 0 (99 tests, 92.92% coverage)
- [x] `PROJECT_PROGRESS.md` updated
