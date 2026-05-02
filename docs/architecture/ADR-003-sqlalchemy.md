# ADR-003: SQLAlchemy for Schema Inspection

**Status**: Accepted
**Date**: 2026-05-01
**Deciders**: Architect

---

## Context

EPIC-003 requires auto-detection of a live database's tables and columns so that the SQL
generator always has an accurate schema context. The detection mechanism must:

1. Work with MySQL 8.0 (primary target) and SQLite (CI/testing — no server required)
2. Return structured data: table names, column names, types, nullable flags, primary keys
3. Be testable in CI without a running MySQL instance
4. Remain database-agnostic to simplify future PostgreSQL/MSSQL support

Options considered:

| Option                           | Pros                                                                                  | Cons                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **SQLAlchemy `inspect()`**       | DB-agnostic; returns structured metadata; works with any SQLAlchemy-supported dialect | Requires SQLAlchemy already in the dependency tree             |
| Raw `INFORMATION_SCHEMA` queries | No ORM dependency                                                                     | MySQL-only; must write dialect-specific SQL                    |
| PyMySQL cursor introspection     | Lightweight                                                                           | MySQL-only; low-level; complex parsing                         |
| DB-API `cursor.description`      | Universal DB-API 2                                                                    | Only returns column info after a query; cannot list all tables |

## Decision

Use **SQLAlchemy `sqlalchemy.inspect(engine)`** for all schema introspection, with
**PyMySQL** as the MySQL dialect driver (see ADR-004). The `SchemaDetector` service
wraps `inspector.get_table_names()` and `inspector.get_columns(table_name)` to produce
a `TableSchema` dict. This is called once per session and cached in
`st.session_state["detected_schema"]`.

SQLite is used in all automated tests via an in-memory engine (`sqlite:///:memory:`),
eliminating the need for a running database server in CI.

## Consequences

### Positive
- Works identically with MySQL, PostgreSQL, SQLite, MSSQL — no dialect-specific code
- `inspector.get_pk_constraint()` gives primary key info with a single call
- In-memory SQLite allows full integration tests in CI (no Docker-in-Docker required)
- Schema cached in session state — only one network round-trip per connection

### Negative
- Adds `sqlalchemy` and `pymysql` to `requirements.txt` (both small, well-maintained)
- `inspect()` may be slow on databases with thousands of tables (not a concern for v1)
- Schema cache invalidated only on "Refresh Schema" click or new connection

### Neutral
- `SchemaDetectionError` wraps all `sqlalchemy.exc.*` exceptions for clean error handling
  at the UI layer

## References
- `src/services/schema_detector.py`
- `src/services/db_connector.py`
- EPIC-003: Dynamic Schema Detection
- ADR-004: PyMySQL as MySQL driver
