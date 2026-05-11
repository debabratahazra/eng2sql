# TC-084–095 — Test Cases: Sprint 15 — Coverage Completeness & CI Hardening

**Epic**: EPIC-012  
**Sprint**: 15  
**Author**: Test Case Writer Agent  
**Date**: 2025-07-17

---

## US-066 — `mongo_connector.py` Coverage Uplift

### TC-084 — Import-time fallback when pymongo is absent

**Format**: BDD  
**Priority**: High

```gherkin
Given  pymongo is not installed (sys.modules["pymongo"] = None)
When   the mongo_connector module is freshly imported
Then   _PYMONGO_AVAILABLE is set to False
And    no ImportError propagates to the caller
```

**Expected**: `_PYMONGO_AVAILABLE == False`

---

### TC-085 — connect() raises when pymongo unavailable

**Format**: BDD  
**Priority**: High

```gherkin
Given  _PYMONGO_AVAILABLE is patched to False
When   MongoDBConnector().connect(config) is called
Then   a DatabaseConnectionError("pymongo is not installed") is raised
And    no MongoClient is created
```

**Expected**: `DatabaseConnectionError` with message containing "pymongo is not installed"

---

### TC-086 — client.close() called and exception swallowed on ServerSelectionTimeoutError cleanup

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  a MongoClient mock whose admin.command raises ServerSelectionTimeoutError
And    mock_client.close raises RuntimeError
When   MongoDBConnector().connect(config) is called
Then   DatabaseConnectionError is raised (outer exception propagated)
And    client.close() was called exactly once
And    the RuntimeError from close() was swallowed
```

**Expected**: `DatabaseConnectionError` raised; `close()` called once; no RuntimeError leaks

---

### TC-087 — client.close() called and exception swallowed on generic Exception cleanup

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  a MongoClient mock whose admin.command raises ValueError
And    mock_client.close raises RuntimeError
When   MongoDBConnector().connect(config) is called
Then   DatabaseConnectionError is raised
And    client.close() was called exactly once
And    the RuntimeError from close() was swallowed
```

**Expected**: `DatabaseConnectionError` raised; `close()` called once; no RuntimeError leaks

---

## US-067 — `models/config.py` Coverage Uplift

### TC-088 — DBConfig repr does not expose password

**Format**: BDD  
**Priority**: High (security)

```gherkin
Given  a DBConfig with password="s3cr3t"
When   repr(config) is called
Then   the string "s3cr3t" does NOT appear in the result
And    the result contains the host value
And    the result contains the dialect value
```

**Expected**: Password not present in repr; host and dialect present

---

### TC-089 — AppConfig repr masks API key

**Format**: BDD  
**Priority**: High (security)

```gherkin
Given  an AppConfig with openai_api_key="sk-abcdefghijklmnop"
When   repr(config) is called
Then   the result contains only the first 8 characters of the key followed by "..."
And    the full key "sk-abcdefghijklmnop" does NOT appear
```

**Expected**: `"sk-abcde..."` in repr; full key absent

---

### TC-090 — AppConfig repr handles None API key

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  an AppConfig with openai_api_key=None
When   repr(config) is called
Then   no exception is raised
And    the result contains the model name
```

**Expected**: No exception; model name present in repr

---

### TC-091 — AppConfig repr does not truncate short API key

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  an AppConfig with openai_api_key="short"  (fewer than 8 chars)
When   repr(config) is called
Then   no exception is raised
And    the full key value appears in the result (no truncation)
```

**Expected**: Full short key in repr; no IndexError

---

## US-068 — `utils/network.py` Coverage Uplift

### TC-092 — Duplicate IP addresses tried only once

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  socket.getaddrinfo returns two entries with the same IP address
When   probe_reachable_host(host, port, timeout) is called
Then   socket.create_connection is called exactly once
And    the function returns the host string
```

**Expected**: `create_connection.call_count == 1`; return value is the host

---

### TC-093 — Three getaddrinfo entries with two duplicates → two connection attempts

**Format**: BDD  
**Priority**: Low

```gherkin
Given  socket.getaddrinfo returns three entries: IP-A, IP-B, IP-A (duplicate)
When   probe_reachable_host is called
Then   socket.create_connection is called exactly twice (IP-A and IP-B only)
```

**Expected**: `create_connection.call_count == 2`

---

## US-069 — Sidebar Component Unit Tests

### TC-094 — _ca_bundle_available respects PGSSLROOTCERT env var

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  PGSSLROOTCERT env var is set to a path pointing to an existing file
When   _ca_bundle_available() is called
Then   the function returns True
```

**Expected**: `True`

---

### TC-095 — _clear_server_state removes all MySQL session keys

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  st.session_state contains all _MYSQL_KEYS with values
When   _clear_server_state() is called
Then   all _MYSQL_KEYS are removed from session_state
And    no KeyError is raised
And    calling it a second time also raises no error (idempotent)
```

**Expected**: All keys absent; no errors on first or second call

---

### TC-096 — _close_mongo_client swallows close() exceptions

**Format**: BDD  
**Priority**: Medium

```gherkin
Given  st.session_state["mongo_client"] holds a mock client
And    mock_client.close() raises RuntimeError
When   _close_mongo_client() is called
Then   no exception propagates
And    client.close() was called once
```

**Expected**: No exception; `close()` called once
