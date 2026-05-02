# ADR-004: PyMySQL as MySQL Driver

**Status**: Accepted
**Date**: 2026-05-01
**Deciders**: Architect

---

## Context

SQLAlchemy requires a DBAPI driver for each database dialect. For MySQL 8.0, the two
mainstream pure-Python options are PyMySQL and the official `mysql-connector-python`.
A compiled C-extension option (`mysqlclient`) also exists.

Options considered:

| Option                 | Pure Python   | Docker-friendly                            | SQLAlchemy URL prefix     | Notes                                                       |
| ---------------------- | ------------- | ------------------------------------------ | ------------------------- | ----------------------------------------------------------- |
| **PyMySQL**            | ✅ Yes         | ✅ No build tools needed                    | `mysql+pymysql://`        | Widely used; actively maintained                            |
| mysqlclient            | ❌ C ext       | ⚠️ Needs `libmysqlclient-dev` in Dockerfile | `mysql+mysqldb://`        | Fastest; build complexity in Docker                         |
| mysql-connector-python | ✅ Yes         | ✅                                          | `mysql+mysqlconnector://` | Official Oracle driver; heavier than PyMySQL                |
| aiomysql               | ✅ Yes (async) | ✅                                          | `mysql+aiomysql://`       | Async only; incompatible with SQLAlchemy sync API used here |

## Decision

Use **PyMySQL** (`mysql+pymysql://` dialect prefix). It installs from PyPI with no C
compiler or system library dependencies, making Docker builds reproducible on any base
image including `python:3.11-slim`.

SQLAlchemy connection URL format used in `DBConfig.connection_url`:
```
mysql+pymysql://<user>:<password>@<host>:<port>/<database>
```

## Consequences

### Positive
- Pure Python — `pip install pymysql` works everywhere; no `apt-get install` in Dockerfile
- `python:3.11-slim` base image sufficient (no `-bullseye` or build-essential needed)
- Well-maintained; compatible with MySQL 5.7, 8.0, and MariaDB

### Negative
- 5–15% slower than `mysqlclient` for large result sets (not a concern for read-only
  analytical queries in v1)
- Does not support MySQL X Protocol or async mode natively

### Neutral
- SQLite is used in tests; no driver installation needed (bundled with Python)
- If performance becomes a concern, swapping to `mysqlclient` only requires changing the
  dialect prefix in `DBConfig.connection_url`

## References
- `src/models/config.py` — `DBConfig.connection_url`
- `src/services/db_connector.py`
- ADR-003: SQLAlchemy for schema inspection
