# BUG-002: ResourceWarning — Unclosed SQLite Connection in Test Fixture

**Severity**: Low
**Sprint**: Sprint 1
**Status**: ✅ Fixed
**Reported By**: Tester Agent
**Assigned To**: Developer Agent
**Linked Test Result**: TR-001

---

## Description

The session-scoped `sqlite_engine` fixture in `tests/conftest.py` creates an
in-memory SQLite engine but does not call `engine.dispose()` on teardown. Python 3.14
emits a `ResourceWarning` during garbage collection:

```
ResourceWarning: unclosed database in <sqlite3.Connection object at 0x...>
```

This warning appears twice per test run (once per SQLite connection object that the
engine holds open).

---

## Steps to Reproduce

```bash
pytest tests/ -q
```

Observe the `ResourceWarning` lines in the output.

---

## Expected Behaviour

No `ResourceWarning` emitted; all database connections closed cleanly after the
session-scoped fixture tears down.

## Actual Behaviour

```
ResourceWarning: unclosed database in <sqlite3.Connection object at 0x...>
Enable tracemalloc to get the object allocation traceback
```

---

## Root Cause

`tests/conftest.py` `sqlite_engine` fixture:

```python
@pytest.fixture(scope="session")
def sqlite_engine() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE customers ..."))
        ...
    return engine
    # ← engine.dispose() never called
```

`scope="session"` means pytest holds the engine for the entire test session. When the
session ends, Python 3.14's stricter GC detects the open connection before SQLAlchemy
finalises it.

---

## Proposed Fix

Convert the fixture to a generator and call `engine.dispose()` on teardown:

```python
@pytest.fixture(scope="session")
def sqlite_engine() -> Generator[Engine, None, None]:
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE customers ..."))
        conn.execute(text("CREATE TABLE orders ..."))
        conn.execute(text("INSERT INTO customers ..."))
        conn.execute(text("INSERT INTO orders ..."))
        conn.commit()
    yield engine
    engine.dispose()
```

---

## Priority Justification

Marked **Low** because:
- No test failures occur
- No production code is affected
- Warning is cosmetic in CI output (does not fail the pipeline)
- Fix is a one-line change to a test fixture
