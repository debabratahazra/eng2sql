# BUG-004: "None / No Auth" Mechanism Ignores Credentials — MongoDB Connection Fails

**Severity**: High
**Sprint**: Sprint 6
**Status**: ✅ Fixed
**Reported By**: User (manual testing)
**Assigned To**: Developer Agent
**Fixed In**: `src/models/config.py` — `MongoConfig.connection_uri`
**Regression Test**: `tests/unit/test_mongo_connector.py::TestMongoConfig::test_connection_uri_credentials_with_no_auth_mechanism`
**Linked Story**: US-027 — `MongoDBConnector` Service
**Linked Source**: `src/models/config.py` — `MongoConfig.connection_uri`

---

## Description

When a user fills in **Username** and **Password** in the MongoDB connection form but
selects **"None / No Auth"** as the Auth Mechanism, the app discards the credentials
entirely and attempts an unauthenticated connection. The MongoDB server rejects the
connection (or the driver times out waiting for a server that requires auth) and the
sidebar shows a connection-failed banner.

The user's intent when selecting *None* is typically "let the driver auto-negotiate the
mechanism" — not "connect without any credentials at all".

---

## Steps to Reproduce

1. Start the Streamlit app: `streamlit run src/app.py`
2. In the sidebar, select **Database type: MongoDB**.
3. Fill in:
   - **Host**: `localhost`
   - **Port**: `27017`
   - **Username**: `root`
   - **Password**: `root`
   - **Auth Source**: `admin`
   - **Auth Mechanism**: `None / No Auth`
4. Click **🔗 Connect**.
5. Observe the error banner.

---

## Expected Behaviour

The connection succeeds. When `username` and `password` are provided alongside
*"None / No Auth"*, the driver should include the credentials in the URI and let
MongoDB auto-negotiate the SASL mechanism (SCRAM-SHA-256 / SCRAM-SHA-1).

Equivalent working URI (entered manually):
```
mongodb://root:root@localhost:27017/?authSource=admin
```

## Actual Behaviour

The sidebar shows:

```
Connection failed: Could not connect to MongoDB at localhost:27017 -
No servers found yet, Timeout: 5.0s,
Topology Description: <TopologyDescription id: 69f612a0bdb225da9f36b90a,
topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017)
server_type: Unknown, rtt: None>]>
```

---

## Root Cause

`src/models/config.py`, `MongoConfig.connection_uri` property (line ~48):

```python
@property
def connection_uri(self) -> str:
    if self.auth_mechanism == "None / No Auth" or not self.username:
        return f"mongodb://{self.host}:{self.port}/"   # ← credentials dropped!
    ...
```

The condition `self.auth_mechanism == "None / No Auth"` short-circuits the whole
expression. When this mechanism is selected the property always returns a bare
`mongodb://host:port/` URI — **even when `self.username` and `self.password` are
non-empty**. The credentials entered by the user are silently discarded.

The server at `localhost:27017` requires authentication (`root` / `root` with
`authSource=admin`), so the unauthenticated client cannot complete the handshake and
the `serverSelectionTimeoutMS` (5 s) expires, producing the topology timeout error.

---

## Proposed Fix

Split the no-auth / with-auth decision on `self.username`, not on `auth_mechanism`.
When credentials are supplied but the mechanism is *"None / No Auth"*, include the
credentials without an `authMechanism` query parameter so the driver can auto-negotiate:

```python
@property
def connection_uri(self) -> str:
    """Return a mongodb:// URI with percent-encoded password."""
    if not self.username:
        # Genuinely unauthenticated — no credentials at all
        return f"mongodb://{self.host}:{self.port}/"

    encoded_pw = urllib.parse.quote_plus(self.password)
    base = f"mongodb://{self.username}:{encoded_pw}@{self.host}:{self.port}/"

    if self.auth_mechanism == "None / No Auth":
        # Credentials present but let the driver auto-negotiate the mechanism;
        # still honour auth_source so the driver knows where to authenticate.
        return f"{base}?authSource={self.auth_source}"

    return (
        f"{base}?authSource={self.auth_source}"
        f"&authMechanism={self.auth_mechanism}"
    )
```

### URI comparison

| Scenario                                     | Before fix                                                                      | After fix                                           |
| -------------------------------------------- | ------------------------------------------------------------------------------- | --------------------------------------------------- |
| `username=""`, mechanism=*None*              | `mongodb://host:27017/`                                                         | `mongodb://host:27017/` (unchanged)                 |
| `username="root"`, mechanism=*None*          | `mongodb://host:27017/` ❌                                                       | `mongodb://root:***@host:27017/?authSource=admin` ✅ |
| `username="root"`, mechanism=*SCRAM-SHA-256* | `mongodb://root:***@host:27017/?authSource=admin&authMechanism=SCRAM-SHA-256` ✅ | (unchanged) ✅                                       |

---

## Affected Tests

The following test must be added / updated in
`tests/unit/test_mongo_connector.py` (`TestMongoConfig`):

```python
def test_connection_uri_with_auth_and_no_mechanism_includes_auth_source(self):
    """Credentials + None mechanism → URI contains credentials and authSource."""
    cfg = MongoConfig(
        host="localhost",
        port=27017,
        username="root",
        password="root",
        auth_source="admin",
        auth_mechanism="None / No Auth",
    )
    uri = cfg.connection_uri
    assert "root:root@localhost:27017" in uri
    assert "authSource=admin" in uri
    assert "authMechanism" not in uri
```

---

## Workaround

Until the fix is deployed, users should select **SCRAM-SHA-256** (or **SCRAM-SHA-1**)
as the Auth Mechanism instead of *None / No Auth* when a username and password are
provided.
