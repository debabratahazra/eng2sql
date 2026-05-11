# BUG-006: MongoDB `localhost` Connection Timeout When App Runs in WSL2 — `directConnection` Not Injected for Embedded-Credential URI

**Severity**: High
**Sprint**: Backlog (reported 2026-05-06)
**Status**: ✅ Fixed (Bug Fix Agent — Strategy E)
**Reported By**: User (manual testing — 2026-05-06 17:35:38)
**Assigned To**: Bug Fix Agent
**Regression Test**: `tests/unit/test_mongo_connector.py::test_bug_006_wsl2_localhost_unreachable_fails_fast_with_hint`
**Linked Story**: US-031 (Connection Input Mode Toggle), US-032 (URI Credential Injection)
**Linked Source**: `src/services/mongo_connector.py`, `src/models/config.py`

---

## Description

When the user launches the Streamlit app from a **WSL2 terminal** (via `scripts/run_app.sh`),
opens the MongoDB configuration panel, selects **"URI + credentials"** input mode,
and enters a full URI that already contains embedded credentials (e.g.
`mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false`),
the connection fails with a `ServerSelectionTimeoutError`.

Two distinct problems compound to produce this failure:

1. **`directConnection=True` is absent from `MongoClient` kwargs** when credentials are
   embedded in the raw URI and no separate username/password fields are filled.  
   The BUG-005 fix added `directConnection=True` for some code paths; this path was missed.

2. **WSL2 network isolation**: when the app runs inside WSL2, `localhost` (resolved to
   `127.0.0.1`) refers to the WSL2 loopback interface — not the Windows host where MongoDB
   is installed. The TCP probe correctly reports `127.0.0.1:27017` unreachable because
   no MongoDB is listening inside WSL2. The app provides no hint that the Windows host IP
   should be used instead of `localhost`.

---

## Error Observed in UI

```
Connection failed: Could not connect to MongoDB at
mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false
- No servers found yet, Timeout: 5.0s,
  Topology Description: <TopologyDescription id: 69fb7beb55525b3f9011e93c,
  topology_type: Unknown,
  servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None>]>
```

> Note: `topology_type: Unknown` (not `Single`) confirms `directConnection=True` was **not** set.

---

## Terminal Log Output

```
2026-05-06 17:35:38 [INFO] services.mongo_connector — ── MongoDB connect START ──────
2026-05-06 17:35:38 [INFO] services.mongo_connector —   mode     : URI
2026-05-06 17:35:38 [INFO] services.mongo_connector —   raw_uri  : mongodb://root:***@localhost:27017/idcauditlog?authSource=admin&ssl=false
2026-05-06 17:35:38 [INFO] services.mongo_connector —   host:port: (from URI):27017
2026-05-06 17:35:38 [INFO] services.mongo_connector —   username : (none)
2026-05-06 17:35:38 [INFO] services.mongo_connector —   timeout  : 5000 ms
2026-05-06 17:35:38 [INFO] services.mongo_connector —   [1/5] resolved URI   : mongodb://root:***@localhost:27017/idcauditlog?authSource=admin&ssl=false
2026-05-06 17:35:38 [INFO] services.mongo_connector —   [2/5] parsed host    : localhost:27017
2026-05-06 17:35:38 [INFO] services.mongo_connector —   [3/5] TCP probe      : resolving localhost …
2026-05-06 17:35:39 [WARNING] services.mongo_connector —   [3/5] TCP probe      : all addresses for localhost:27017 unreachable (tried: ['127.0.0.1']) — MongoDB may not be running or port 27017 is blocked
2026-05-06 17:35:39 [INFO] services.mongo_connector —   [4/5] MongoClient    : kwargs = {'host': 'localhost', 'port': 27017, 'username': 'root', 'password': '***', 'authSource': 'admin', 'serverSelectionTimeoutMS': 5000}
2026-05-06 17:35:44 [ERROR] services.mongo_connector —   FAIL ServerSelectionTimeoutError: No servers found yet, Timeout: 5.0s, Topology Description: <TopologyDescription id: 69fb7beb55525b3f9011e93c, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None>]>
2026-05-06 17:35:44 [WARNING] components.sidebar — UI: MongoDB URI connection failed: Could not connect to MongoDB at mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false - No servers found yet, Timeout: 5.0s, ...
```

### Key diagnostic signals in the log

| Signal                                     | Expected  | Actual                                   | Implication                                                  |
| ------------------------------------------ | --------- | ---------------------------------------- | ------------------------------------------------------------ |
| `directConnection` in `MongoClient` kwargs | `True`    | **absent**                               | BUG-005 fix not applied for this code path                   |
| `topology_type`                            | `Single`  | `Unknown`                                | Confirms `directConnection=True` missing                     |
| TCP probe result                           | reachable | **unreachable** (`tried: ['127.0.0.1']`) | WSL2 `localhost` ≠ Windows host                              |
| `username` in logs                         | `root`    | `(none)`                                 | Correct — creds are embedded in URI, separate field is empty |

---

## Steps to Reproduce

1. Install MongoDB on the **Windows** host (not inside WSL2); ensure it listens on `127.0.0.1:27017`.
2. Launch the Streamlit app from a **WSL2 terminal** using `scripts/run_app.sh`.
3. In the sidebar, select **Database type: MongoDB**.
4. Select **"URI + credentials"** input mode.
5. Enter the following in the URI field (credentials embedded, NO separate username/password):
   ```
   mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false
   ```
6. Leave **Username** and **Password** fields blank.
7. Click **🔗 Connect**.

**Expected**: Connection succeeds (MongoDB is running on the Windows host).  
**Actual**: `ServerSelectionTimeoutError — No servers found yet, Timeout: 5.0s`.

---

## Root Cause Analysis

### Cause 1 — `directConnection=True` not injected for embedded-credential URIs

BUG-005 introduced `directConnection=True` to fix topology detection for `mongodb://` (non-SRV) URIs.
The fix targets the code path where credentials are supplied in **separate fields**. When the user
provides a URI with credentials already embedded (e.g. `mongodb://user:pass@host/`), the connector
extracts the credentials from the URI but follows a slightly different kwarg-assembly path that
**does not append `directConnection=True`**.

Evidence: `MongoClient kwargs` in the log contains `host`, `port`, `username`, `password`,
`authSource`, `serverSelectionTimeoutMS` — but no `directConnection`.

### Cause 2 — WSL2 `localhost` isolation

When the Streamlit process runs inside WSL2, `socket.getaddrinfo("localhost", 27017)` resolves
to `[('127.0.0.1', 27017)]` — the WSL2 loopback, **not** the Windows host. MongoDB is installed
on Windows and is unreachable at `127.0.0.1` from within WSL2.

The TCP probe (`[3/5]`) correctly detects this and logs a warning, but the warning message says
_"MongoDB may not be running or port 27017 is blocked"_ — it does not mention the WSL2 /
Windows host IP scenario. The user has no actionable guidance.

The fix on the Windows side is to use the Windows host IP visible from WSL2, e.g.:
```
cat /etc/resolv.conf          # nameserver line = Windows host IP (e.g. 172.22.80.1)
mongodb://root:root@172.22.80.1:27017/idcauditlog?authSource=admin&ssl=false
```
Or use the WSL2 utility `hostname -I` to discover the Windows host address.

---

## What Is Working Correctly

- Credential masking in logs (`password: ***`) ✅
- URI parsing — `authSource=admin`, `ssl=false` extracted ✅
- TCP probe fires and reports unreachability with correct address tried ✅
- `ServerSelectionTimeoutError` surfaced to UI with redacted URI ✅

---

## Proposed Fix (for backlog)

### Fix 1 — Ensure `directConnection=True` for all `mongodb://` URIs regardless of how credentials are supplied

In `src/services/mongo_connector.py`, verify the kwarg-assembly logic always appends
`directConnection=True` when the resolved URI scheme is `mongodb://` (not `mongodb+srv://`),
regardless of whether credentials came from embedded URI fields or from separate form fields.

Add a regression test:
```python
def test_direct_connection_set_for_embedded_credential_uri():
    cfg = MongoConfig(raw_uri="mongodb://user:pass@localhost:27017/db")
    connector = MongoDBConnector(cfg)
    # Stub ping; assert directConnection=True in MongoClient kwargs
```

### Fix 2 — WSL2-aware error hint in TCP probe warning

In `src/services/mongo_connector.py`, detect WSL2 environment
(e.g. check `/proc/version` for `microsoft` or `WSL`) when the TCP probe fails for `localhost`:

```python
import platform, pathlib

def _is_wsl2() -> bool:
    try:
        return "microsoft" in pathlib.Path("/proc/version").read_text().lower()
    except OSError:
        return False
```

If WSL2 is detected and host is `localhost` / `127.0.0.1`, append to the warning:
> "Running inside WSL2? MongoDB on the Windows host is not reachable at localhost.
>  Try the Windows host IP (check /etc/resolv.conf nameserver line) instead."

---

## Priority / Backlog Notes

- **Status**: Backlog — not assigned to any sprint yet.
- **Effort estimate**: Medium (3–5 points): `directConnection` fix is 1–2 pts; WSL2 hint is 2–3 pts.
- **Workaround**: Replace `localhost` with the Windows host IP visible from WSL2:
  ```bash
  WIN_HOST=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
  # Use $WIN_HOST instead of localhost in the MongoDB URI
  ```
- **Related**: BUG-005 (URI mode topology timeout — IPv4/IPv6 mismatch), US-031, US-032.

---

## Fix Attempts

### Attempt 1 — Strategy E (UX / fail-fast) — ✅ PASS (2026-05-07)

**Strategy**: Detect WSL2, intercept loopback probe failures, and raise a
`DatabaseConnectionError` with an actionable hint BEFORE invoking
`MongoClient`. This both gives the user clear remediation guidance AND
avoids the 5-second `serverSelectionTimeoutMS` wait for the unavoidable
`ServerSelectionTimeoutError`.

**Why Strategy A (force `directConnection=True`) was rejected**:
While the bug report's first-pass analysis suggested injecting
`directConnection=True`, the existing test
`test_connect_does_not_force_direct_connection` (added by the BUG-005
final fix) explicitly forbids this. Its docstring records that
"MongoDB Compass (which works) does not use `directConnection=True`.
Forcing it caused hello-handshake failures in pymongo 4.16 on Windows."
The real failure in BUG-006 is **TCP-level unreachability** (WSL2 ↔
Windows host networking), not topology selection. Adding
`directConnection=True` would break Windows users without helping WSL2
users — the host is genuinely unreachable in the reported scenario.

**Files changed**:
- `src/services/mongo_connector.py` — added `_is_wsl2()` static helper,
  `_LOOPBACK_HOSTS` frozenset, and a fail-fast guard inside `connect()`
  that runs immediately after `_probe_reachable_host()`.
- `tests/unit/test_mongo_connector.py` — added two regression tests
  (`test_bug_006_wsl2_localhost_unreachable_fails_fast_with_hint` and
  `test_bug_006_non_wsl2_localhost_probe_failure_still_calls_mongoclient`).
- `docs/test-cases/TC-040-bug-006-wsl2-localhost-fail-fast.md` — BDD
  test case with three scenarios.
- `docs/guides/developer-guide.md` — added "WSL2 + MongoDB networking"
  note documenting the fail-fast behaviour.

---

## Verification Record

### Verification 1 — 2026-05-07 — ✅ PASS

| Check                                                                   |             Baseline |            After fix | Result                                |
| ----------------------------------------------------------------------- | -------------------: | -------------------: | ------------------------------------- |
| Unit + integration tests                                                |           134 passed |           136 passed | ✅ +2 regression tests, no regressions |
| Coverage (overall)                                                      |              93.84 % |              93.97 % | ✅ improved                            |
| Coverage (`src/services/mongo_connector.py`)                            |                 95 % |                 95 % | ✅ stable                              |
| AppTest UI smoke (`test_sidebar_ui.py`)                                 |            10 passed |            10 passed | ✅ no UI regression                    |
| `test_connect_does_not_force_direct_connection` (BUG-005 invariant)     |                 PASS |                 PASS | ✅ preserved                           |
| `test_bug_006_wsl2_localhost_unreachable_fails_fast_with_hint`          |                  n/a |                 PASS | ✅ regression test green               |
| `test_bug_006_non_wsl2_localhost_probe_failure_still_calls_mongoclient` |                  n/a |                 PASS | ✅ negative test green                 |
| ruff                                                                    | not installed in env | not installed in env | ⚠ skipped (CI handles)                |
| mypy                                                                    | not installed in env | not installed in env | ⚠ skipped (CI handles)                |

**Pytest summary**:

```
tests\integration\test_db_connector.py .......                           [  5%]
tests\unit\test_db_connector.py ........                                 [ 11%]
tests\unit\test_mongo_connector.py .....................................
.....................                                                    [ 53%]
tests\unit\test_mongo_schema_detector.py ....................            [ 68%]
tests\unit\test_schema_detector.py ...........                           [ 76%]
tests\unit\test_sidebar_ui.py ..........                                 [ 83%]
tests\unit\test_sql_generator.py ......................                  [100%]

Required test coverage of 80% reached. Total coverage: 93.97%
============================ 136 passed in 26.37s =============================
```

**Outcome**: All gates green. Bug closed.
