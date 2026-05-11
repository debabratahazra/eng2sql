# CR-011 — Sprint 11 Code Review (Refactor & Hardening)

**Reviewer**: Code Reviewer Agent
**Sprint**: Sprint 11
**Date**: 2026-05-09
**Verdict**: ✅ **Approved** (with documented carry-overs)

---

## Scope

| Story  | Title                                                             | Files Touched                                                                                                                 |
| ------ | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| US-050 | Extract WSL2 fail-fast helper to `src/utils/network.py`           | `src/utils/network.py` (new), `src/services/mongo_connector.py`, `src/services/db_connector.py`, `tests/unit/test_network.py` |
| US-052 | Configurable PostgreSQL Step 1 admin database                     | `src/components/sidebar.py`, `src/app.py`, `tests/unit/test_sidebar_sprint11.py`                                              |
| US-053 | `coverage-docker` GitHub Actions matrix job                       | `.github/workflows/ci-cd.yml`                                                                                                 |
| US-055 | Unit-mock coverage lift for `db_connector.py` PostgreSQL branches | `tests/unit/test_db_connector_postgresql_unit.py` (new)                                                                       |
| US-056 | Sidebar sslmode `verify-*` pre-validation against CA bundle       | `src/components/sidebar.py`, `tests/unit/test_sidebar_sprint11.py`                                                            |

**Deferred to Sprint 12** (carry-over):
- US-051 — Sidebar `RelationalConnectorSidebar` mixin refactor (3 pts) — high-risk refactor of a 600-LoC file with extensive AppTest coverage; deferred to keep Sprint 11 close-out green.
- US-054 — `pyproject.toml` optional-dependency groups (1 pt) — requires adding a full `[project]` block with build backend; project is currently a Streamlit app, not a pip-installable package; needs ADR before action.

---

## Findings

### ✅ Strengths

- **`src/utils/network.py`** is a clean extraction. `is_wsl2()` uses `functools.lru_cache(maxsize=1)` so the `/proc/version` read happens at most once per process. `LOOPBACK_HOSTS` is a `frozenset` literal — immutable and hash-fast.
- **Backwards compat preserved** in `mongo_connector.py`: the class attributes `_LOOPBACK_HOSTS` and the static methods `_is_wsl2`/`_probe_reachable_host` are kept as thin wrappers, so the 58 existing mongo unit tests pass without modification.
- **`db_connector.create_engine` WSL2 guard** is gated on `host_lower in LOOPBACK_HOSTS and is_wsl2()` — a single branch with a probe; raises `DatabaseConnectionError` with the same WSL2 hint message used by Mongo. Coverage on the new branch is exercised by `test_db_connector_postgresql_unit.py::test_create_engine_wsl2_loopback_guard_when_unreachable`.
- **`pg_admin_db`** is wired through both default state init (`app.py`), the form (`pg_admin_db_input` text input), and the `DBConfig.database` field; default `"postgres"` preserves Sprint 10 behaviour. Validation rejects empty values with a clear `"Admin DB cannot be empty."` warning.
- **`_ca_bundle_available()`** resolution order matches the user story (env var → `~/.postgresql/root.crt` → certifi fallback). Three direct tests cover the success and miss paths.
- **`coverage-docker` job** runs on `ubuntu-latest`, has a 10-minute timeout, uploads coverage XML as an artifact, and depends on the lint job — matches the user story acceptance criteria exactly.

### ⚠️ Minor Notes (non-blocking)

- The new `coverage-docker` job is not yet in any required-status check on the repository — DevOps should mark it required after the first green PR run.
- `_ca_bundle_available()` does not log the chosen source — could be useful for support tickets when verify-ca fails despite a bundle being present. Logged as Sprint 12 nice-to-have.
- US-052 still hard-codes `"postgres"` as the *default* — fine for stock servers, and the override is now available, so this is informational only.

### 🔒 Security

- No new secret material introduced. The `_pg_password` clear-after-Step-2 invariant from Sprint 10 is preserved (no regression on `_clear_pg_state`).
- WSL2 guard message contains no credentials — only host/port and a public docs URL.
- `_ca_bundle_available()` reads file existence only; never reads file contents.

### 📊 Test & Coverage

- **199 collected / 191 passed / 8 skipped** (8 = Docker-gated MySQL + PostgreSQL integration tests that require a Docker daemon).
- Coverage **94.48 % → 96.32 %** (+1.84 pp).
- `db_connector.py` coverage **80 % → 96 %** (US-055 target ≥ 90 % met with margin).
- New file `src/utils/network.py` at **97 %** (only the certifi-import fallback in the file is uncovered, which is the intended graceful-degrade path).

---

## Verdict

✅ **Approved.** Five of seven committed stories delivered (11/14 pts). US-051 and US-054 are explicitly carried over with rationale; the carry-over is documented in `SPRINT-11.md` and will appear as Sprint 12 backlog items.
