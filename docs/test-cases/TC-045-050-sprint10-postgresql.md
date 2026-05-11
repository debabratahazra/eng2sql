# TC-045 to TC-050 — Sprint 10 Test Cases (PostgreSQL Live Connection Support)

**Sprint**: Sprint 10 (EPIC-009)
**Author**: Test Case Writer agent
**Date**: 2026-05-08

---

## TC-045 — `DBConfig` Dialect-Aware URL Building (US-044)

**File**: `tests/unit/test_config_postgresql.py`

| ID        | Scenario                                       | Given                                             | When                     | Then                                             |
| --------- | ---------------------------------------------- | ------------------------------------------------- | ------------------------ | ------------------------------------------------ |
| TC-045-01 | Default dialect is MySQL                       | A `DBConfig` constructed without `dialect=`       | the instance is created  | `dialect == "mysql"`                             |
| TC-045-02 | MySQL URL uses pymysql driver                  | A MySQL `DBConfig`                                | `connection_url` is read | URL is `mysql+pymysql://u:p@h:3306/d`            |
| TC-045-03 | Legacy long-form `mysql+pymysql` is normalised | A `DBConfig` with `dialect="mysql+pymysql"`       | constructor runs         | `dialect == "mysql"` and URL still works         |
| TC-045-04 | PostgreSQL URL uses psycopg driver             | A PostgreSQL `DBConfig`                           | `connection_url` is read | URL is `postgresql+psycopg://...?sslmode=prefer` |
| TC-045-05 | Default sslmode is `prefer`                    | A PostgreSQL `DBConfig` without `sslmode`         | URL is built             | `?sslmode=prefer` is appended                    |
| TC-045-06 | Explicit sslmode is honoured                   | A PostgreSQL `DBConfig` with `sslmode="require"`  | URL is built             | URL ends with `?sslmode=require`                 |
| TC-045-07 | Special password chars are URL-encoded         | A `DBConfig` with `password="p@ss/word"`          | URL is built             | URL contains `p%40ss%2Fword`                     |
| TC-045-08 | Invalid dialect raises ValueError              | `DBConfig(dialect="oracle")`                      | constructor runs         | `ValueError` mentioning "dialect"                |
| TC-045-09 | Invalid sslmode raises ValueError              | `DBConfig(dialect="postgresql", sslmode="bogus")` | constructor runs         | `ValueError` mentioning "sslmode"                |

---

## TC-046 — `DBConnector.list_databases` Dialect Dispatch (US-046)

**File**: `tests/unit/test_db_connector_postgresql.py`

| ID        | Scenario                                   | Given                                                                                                       | When                     | Then                                                               |
| --------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------------------------ |
| TC-046-01 | PostgreSQL system DBs filtered             | A mock engine `dialect.name = "postgresql"` returning `[postgres, template0, template1, app_db, analytics]` | `list_databases(engine)` | returns `["analytics", "app_db"]`                                  |
| TC-046-02 | PostgreSQL uses `pg_database` query        | A mock postgresql engine                                                                                    | `list_databases(engine)` | the executed text query contains `pg_database` and `datistemplate` |
| TC-046-03 | Unknown dialect raises NotImplementedError | A mock engine with `dialect.name = "oracle"`                                                                | `list_databases(engine)` | `NotImplementedError` mentioning `"oracle"`                        |

---

## TC-047 — `SQLGenerator` Dialect Tip Block (US-047)

**File**: `tests/unit/test_sql_generator_postgresql.py`

| ID        | Scenario                                | Given                                       | When                                                | Then                                                                |
| --------- | --------------------------------------- | ------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------- |
| TC-047-01 | PostgreSQL prompt contains dialect tips | A `SQLGenerator` with patched OpenAI client | `generate_sql(..., dialect="PostgreSQL")` is called | system-prompt content contains `"PostgreSQL"`, `"ILIKE"`, `"::"`    |
| TC-047-02 | MySQL prompt omits PostgreSQL tips      | Same generator                              | `generate_sql(..., dialect="MySQL")` is called      | system-prompt does NOT contain `"ILIKE"` or `"PostgreSQL-specific"` |

---

## TC-048 — Sidebar PostgreSQL Branch (US-045)

**File**: `tests/unit/test_sidebar_postgresql.py`

| ID        | Scenario                              | Given                                                    | When                     | Then                                                                     |
| --------- | ------------------------------------- | -------------------------------------------------------- | ------------------------ | ------------------------------------------------------------------------ |
| TC-048-01 | PostgreSQL appears in db-type radio   | The app is loaded                                        | radio options enumerated | `"PostgreSQL"` is one of the options; default still `"MySQL"`            |
| TC-048-02 | PG Step 1 form renders when selected  | `db_type == "PostgreSQL"`                                | sidebar re-renders       | `pg_sslmode_input` selectbox + `pg_connect` button exist                 |
| TC-048-03 | PG Step 1 success populates databases | Patched `create_engine` + `list_databases`               | `pg_connect` clicked     | `pg_server_engine`, `pg_available_databases` populated; status `success` |
| TC-048-04 | PG Step 1 connection failure          | `create_engine` raises `DatabaseConnectionError("boom")` | `pg_connect` clicked     | `pg_step1_status == ("error", "...boom...")`                             |
| TC-048-05 | PG Step 2 success populates schema    | Step 1 state seeded; patched engine + detector           | `pg_db_confirm` clicked  | `detected_schema`, `pg_engine`, `pg_selected_database` populated         |
| TC-048-06 | PG Step 2 clears `_pg_password`       | Step 1 state seeded with password                        | `pg_db_confirm` clicked  | `_pg_password` removed from session state                                |
| TC-048-07 | Expired credentials warn at Step 2    | Step 1 state seeded but `_pg_password` deleted           | `pg_db_confirm` clicked  | `pg_step2_status == ("warning", "...reconnect...")`                      |

---

## TC-049 — PostgreSQL Live Container Integration (US-048)

**File**: `tests/integration/test_db_connector_postgres_live.py`
**Markers**: `[integration, docker]` — auto-skip without Docker.

| ID        | Scenario                                        | Given                            | When                                                | Then                                                             |
| --------- | ----------------------------------------------- | -------------------------------- | --------------------------------------------------- | ---------------------------------------------------------------- |
| TC-049-01 | Engine creation against real Postgres 16        | `postgres_container` fixture     | `create_engine(config)` + `test_connection(engine)` | engine created; `dialect.name == "postgresql"`; ping succeeds    |
| TC-049-02 | `list_databases` filters template DBs           | `postgres_container` fixture     | `list_databases(engine)`                            | `template0`, `template1`, `postgres` excluded; `testdb` included |
| TC-049-03 | `execute_query` returns DataFrame               | Real engine                      | `execute_query("SELECT 1 AS one, 2 AS two")`        | returns 1×2 DataFrame with values 1, 2                           |
| TC-049-04 | Bad credentials raise `DatabaseConnectionError` | Container host/port + bogus user | `create_engine` + `test_connection`                 | `DatabaseConnectionError` raised                                 |

---

## TC-050 — Documentation Verifications (US-049)

| ID        | Scenario                                   | Verification                                                                                                                          |
| --------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| TC-050-01 | User-guide has PostgreSQL section          | `docs/guides/user-guide.md` contains a "PostgreSQL Live Connection" section with sslmode instructions                                 |
| TC-050-02 | Developer-guide documents dialect dispatch | `docs/guides/developer-guide.md` describes `_DRIVER_SCHEMES`, `_LIST_DB_QUERIES`, sslmode whitelist, and `postgres_container` fixture |
| TC-050-03 | README mentions PostgreSQL                 | `README.md` features list includes PostgreSQL; setup mentions `psycopg[binary]`                                                       |
| TC-050-04 | Roadmap reflects EPIC-009                  | `docs/roadmap.md` lists EPIC-009 under delivered when sprint closes                                                                   |
