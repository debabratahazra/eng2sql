# BUG-007: MongoDB Multi-Host (Replica Set) URI Fails with `Port could not be cast to integer value` Error

**Severity**: High
**Sprint**: Backlog (reported 2026-05-07)
**Status**: ✅ Fixed (Bug Fix Agent)
**Reported By**: User (manual testing — 2026-05-07)
**Assigned To**: Bug Fix Agent
**Regression Test**: `tests/unit/test_mongo_connector.py::TestMultiHostURI`
**Linked Story**: US-031 (Connection Input Mode Toggle), US-032 (URI Credential Injection)
**Linked Source**: `src/services/mongo_connector.py`

---

## Description

When the user selects **"URI + credentials"** input mode for MongoDB and provides a
**multi-host (replica set seed-list)** URI such as

```
mongodb://idcauditlog_admin:aLo5UrEabld8MbmL@rbglv0905.rbg.infineon.com:27017,rbglv0906.rbg.infineon.com:27017,rbglv0907.rbg.infineon.com:27017/?authSource=idcauditlog&replicaSet=rs&readPreference=primary&tls=false
```

the connection fails immediately (no network round-trip is even attempted) with the
following error surfaced in the Streamlit UI:

```
Connection failed: Could not connect to MongoDB at
mongodb://rbglv0905.rbg.infineon.com:27017,rbglv0906.rbg.infineon.com:27017,rbglv0907.rbg.infineon.com:27017/?authSource=idcauditlog&replicaSet=rs&readPreference=primary&tls=false
- Port could not be cast to integer value as
  '27017,rbglv0906.rbg.infineon.com:27017,rbglv0907.rbg.infineon.com:27017'
```

The same URI works correctly in MongoDB Compass and the `mongosh` shell — proving the
URI itself is valid and the credentials/network/server are all reachable. The failure is
purely a client-side parsing bug in our connector.

---

## Steps to Reproduce

1. In the sidebar, select **Database type: MongoDB**.
2. Select **"URI + credentials"** input mode.
3. Enter a multi-host replica-set URI (any URI containing comma-separated hosts in the
   netloc):
   ```
   mongodb://user:pass@host1:27017,host2:27017,host3:27017/?replicaSet=rs
   ```
4. Click **🔗 Connect**.

**Expected**: Connection succeeds and the database list populates (or fails with a real
network/auth error if the hosts are unreachable).
**Actual**: Connection fails immediately with `Port could not be cast to integer value
as '27017,host2:27017,host3:27017'`.

---

## Root Cause Analysis

`MongoDBConnector.connect()` routes every URI starting with `mongodb://` (i.e. anything
that is not `mongodb+srv://`) through `_uri_to_kwargs()`, which parses the URI with
`urllib.parse.urlparse` and then accesses `parsed.port`.

For a multi-host seed-list URI, `urlparse` does NOT split the hosts list — `parsed.netloc`
contains the entire `user:pass@host1:27017,host2:27017,host3:27017` string. When code
then accesses `parsed.port`, Python tries to cast everything after the **first** colon in
the host portion (`27017,host2:27017,host3:27017`) to an integer and raises:

```
ValueError: Port could not be cast to integer value as
'27017,host2:27017,host3:27017'
```

This `ValueError` is caught by the broad `except Exception` block in `connect()` and
re-raised as a `DatabaseConnectionError` with the deceptive prefix
`Could not connect to MongoDB at …`, which made the bug look like a network problem.

The keyword-arguments code path was added in BUG-005 specifically to bypass pymongo's
own URI-string parser (which had a separate `ssl=false` quirk). That path is correct for
single-host URIs but cannot represent multi-host seed lists at all — `MongoClient(host=...,
port=...)` only accepts one host. Multi-host URIs MUST be passed as a URI string so that
pymongo's seed-list-aware parser can handle them.

`mongodb+srv://` URIs already correctly take the URI-string branch. Multi-host
`mongodb://` URIs were the missing case.

---

## Fix Applied

**File**: `src/services/mongo_connector.py`

1. Added a new static helper:
   ```python
   @staticmethod
   def _is_multi_host(uri: str) -> bool:
       """Return True when the URI lists more than one comma-separated host."""
   ```
   It strips any `user:pass@` prefix from `parsed.netloc` and checks for a `,` in the
   remaining hosts portion. Returns `False` for `mongodb+srv://` URIs (single-host by
   spec).

2. Changed the routing condition in `connect()` from
   ```python
   if resolved_uri.startswith("mongodb://"):
   ```
   to
   ```python
   if resolved_uri.startswith("mongodb://") and not self._is_multi_host(resolved_uri):
   ```
   Multi-host URIs now fall through to the `else` branch which already handles
   `mongodb+srv://` and passes the URI string directly to `MongoClient(...)`.

The existing log line in the else branch already says
`"SRV" if resolved_uri.startswith("mongodb+srv") else "multi-host"`, so multi-host URIs
are now logged correctly without further changes.

---

## Tests Added

**File**: `tests/unit/test_mongo_connector.py` — new `TestMultiHostURI` class

| Test                                                                            | Purpose                                                               |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `test_is_multi_host_true_for_replica_set_seed_list`                             | Detects comma-separated hosts                                         |
| `test_is_multi_host_false_for_single_host`                                      | Single host returns False                                             |
| `test_is_multi_host_false_for_srv_uri`                                          | SRV URIs always return False                                          |
| `test_is_multi_host_with_credentials_in_netloc`                                 | `user:pass@` does not confuse detector                                |
| `test_connect_multi_host_uri_uses_uri_string_form`                              | `MongoClient` receives positional URI string, NOT kwargs              |
| `test_connect_multi_host_uri_skips_tcp_probe`                                   | `_probe_reachable_host` is NOT called for multi-host                  |
| `test_bug_007_regression_multi_host_replica_set_uri_does_not_raise_value_error` | Exact failing URI shape from the report — must not raise `ValueError` |

---

## Verification

```
pytest tests/unit/test_mongo_connector.py -k "MultiHost or bug_007" -v
```

All new tests pass. Full test suite remains green.
