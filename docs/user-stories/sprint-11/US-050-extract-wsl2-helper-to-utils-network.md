# US-050 — Extract WSL2 fail-fast helper to `src/utils/network.py`

**Sprint**: Sprint 11
**Epic**: Tech Debt (Sprint 10 retro action item #1)
**Source**: SPRINT-10-retro.md "What Could Be Improved" §1
**Points**: 2
**Owner**: Developer

## User Story

As a **maintainer of Eng2SQL**, I want the WSL2 fail-fast helper extracted into a shared
`src/utils/network.py` module so that both `MongoDBConnector` and `DBConnector` can apply
the same protection without code duplication, preventing BUG-006-style timeouts from
silently regressing for PostgreSQL.

## Acceptance Criteria

1. New module `src/utils/network.py` exposes:
   - `LOOPBACK_HOSTS: frozenset[str]` (constant)
   - `is_wsl2() -> bool` (cached, mirrors current `_is_wsl2`)
   - `probe_reachable_host(host: str, port: int, timeout_s: float = 1.0) -> str` (mirrors current `_probe_reachable_host` semantics)
2. `src/services/mongo_connector.py` imports from `utils.network`; the existing inline
   class-private versions (`_LOOPBACK_HOSTS`, `_is_wsl2`, `_probe_reachable_host`) are
   removed.
3. Existing BUG-005 / BUG-006 invariant tests in `tests/unit/test_mongo_connector.py`
   still pass unchanged.
4. `src/services/db_connector.py` imports `is_wsl2` and `probe_reachable_host` and adds a
   guard in `create_engine()` that, when `host` is a loopback name and `is_wsl2()` is
   true and the port is not reachable in 1 s, raises `DatabaseConnectionError` with the
   same WSL2 hint message used by MongoDB.
5. New `tests/unit/test_network.py` with at least 3 tests covering: loopback host set,
   `is_wsl2` cached behaviour, `probe_reachable_host` returns input host on success.

## Definition of Done

- [x] `src/utils/network.py` created with the three exports
- [x] `mongo_connector.py` uses the shared helper; old inline copies removed
- [x] `db_connector.create_engine` invokes the WSL2 guard before SQLAlchemy
- [x] All existing tests pass (165 baseline)
- [x] At least 3 new unit tests for the helper module
- [x] Coverage on `src/utils/network.py` ≥ 90 %
- [x] CR-011 approved
- [x] Developer guide updated with the new module location

## Status

✅ Done
