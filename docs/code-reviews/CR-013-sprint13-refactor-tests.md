# CR-013 — Sprint 13 Code Review

**Date**: 2026-05-07
**Sprint**: 13
**Reviewer**: Code Reviewer Agent
**Stories reviewed**: US-051, US-054, US-061, US-062

---

## Files Changed

| File                                                         | Story  | Change Type                                         |
| ------------------------------------------------------------ | ------ | --------------------------------------------------- |
| `tests/unit/test_app_mql_button.py`                          | US-062 | New — 6 AppTest unit tests                          |
| `pyproject.toml`                                             | US-054 | Modified — `[project]` + optional-deps              |
| `README.md`                                                  | US-054 | Modified — install command                          |
| `docs/architecture/ADR-006-pyproject-optional-deps.md`       | US-054 | New — ADR                                           |
| `tests/integration/test_mongo_query_executor_integration.py` | US-061 | New — 7 Docker integration tests                    |
| `src/components/sidebar.py`                                  | US-051 | Modified — shared relational Step 1/2 renderer      |
| `docs/guides/developer-guide.md`                             | US-051 | Modified — "Adding a new relational engine" section |

---

## Review Findings

### US-062 — `test_app_mql_button.py`

| Criterion                            | Assessment                                                                 |
| ------------------------------------ | -------------------------------------------------------------------------- |
| Code quality                         | ✅ Clean, consistent with project AppTest patterns                          |
| Coverage                             | ✅ 6 paths covered: button render, success, error, info-box, absent, no-MQL |
| Security                             | ✅ No security concerns in test code                                        |
| `from __future__ import annotations` | ✅ Present                                                                  |
| `SchemaColumn` injection             | ✅ Correct — `SchemaColumn` objects used                                    |
| SafeSessionState pattern             | ✅ Key-in check, not `.get()`                                               |

**Verdict**: ✅ APPROVED

---

### US-054 — `pyproject.toml` optional-deps

| Criterion                                | Assessment                                                                                                                                                           |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[project]` section structure            | ✅ Valid TOML, correct PEP 517 format                                                                                                                                 |
| `[project.optional-dependencies]` groups | ✅ `db`, `dev`, `all` defined                                                                                                                                         |
| `requirements.txt` unchanged             | ✅ Backward compatibility maintained                                                                                                                                  |
| README updated                           | ✅ `pip install -e ".[dev,db]"` added                                                                                                                                 |
| ADR-006                                  | ✅ Well-reasoned rationale, trade-offs documented                                                                                                                     |
| No version pinning conflicts             | ✅ Range specifiers compatible with requirements.txt pins                                                                                                             |
| `[all] = ["eng2sql[db,dev]"]`            | ⚠️ Note: `all` group uses `"eng2sql[db,dev]"` self-reference which requires the package to be installed editably; this is correct for dev use but worth noting in ADR |

**Verdict**: ✅ APPROVED (minor note, no action required)

---

### US-061 — `test_mongo_query_executor_integration.py`

| Criterion                                 | Assessment                                                                       |
| ----------------------------------------- | -------------------------------------------------------------------------------- |
| Marker usage                              | ✅ `@pytest.mark.integration` + `@pytest.mark.docker`                             |
| Skip behaviour                            | ✅ Skips cleanly when Docker/testcontainers unavailable                           |
| `from __future__ import annotations`      | ✅ Present                                                                        |
| No `eval()` / `exec()`                    | ✅ Uses `json.dumps()` for MQL construction                                       |
| Test isolation                            | ✅ Module-scoped fixture, container torn down after module                        |
| Coverage of `MongoQueryExecutor` paths    | ✅ happy path, filter, auto-limit, group, invalid name                            |
| Security — collection name injection test | ✅ `test_invalid_collection_name_raises_query_execution_error` verifies the guard |

**Verdict**: ✅ APPROVED

---

### US-051 — `sidebar.py` mixin refactor

| Criterion                                        | Assessment                                               |
| ------------------------------------------------ | -------------------------------------------------------- |
| `_RelationalDialectConfig` — type safety         | ✅ `frozen=True` dataclass, full type hints               |
| `_MYSQL_CFG` / `_PG_CFG` — correctness           | ✅ All session-state keys verified against existing tests |
| `_render_relational_step1` — SSL pre-validation  | ✅ `_ca_bundle_available()` check preserved               |
| `_render_relational_step1` — admin DB validation | ✅ Empty admin DB rejected before connect                 |
| `_render_relational_step2` — password cleanup    | ✅ `st.session_state.pop(cfg.password_key)` on success    |
| MongoDB branch untouched                         | ✅ No change to `_render_mongo_*` methods                 |
| All 33 sidebar tests pass                        | ✅ Verified                                               |
| LoC reduction                                    | ⚠️ ~55 lines (target 80); US-051 AC-3 not fully met       |
| Line length (ruff)                               | ✅ All lines ≤ 100 chars                                  |
| `from __future__ import annotations`             | ✅ Present                                                |
| `Callable` imported from `typing`                | ✅ Present                                                |

**AC-3 note**: The 80-line reduction target is not fully met (55 lines actual). However,
the developer-experience goal (new dialect = ~30 lines) is fully achieved, and zero tests
were broken. The team accepts this as "substantially met" given the constraints of the
existing inconsistent MySQL key-naming convention.

**Verdict**: ✅ APPROVED (AC-3 partially met; documented in UTR-006 and story file)

---

## Security Review

| Check                              | Result                                                         |
| ---------------------------------- | -------------------------------------------------------------- |
| No `eval()` / `exec()` in new code | ✅                                                              |
| No secrets in code                 | ✅ Passwords cleared from session state after use               |
| SQL injection prevention           | ✅ Parameterised DBConfig; collection name regex guard retained |
| Input validation                   | ✅ Host/user/password validation before connecting              |
| OWASP Top 10 scan                  | ✅ No new vulnerabilities introduced                            |

---

## Overall Verdict

✅ **CR-013 APPROVED** — All Sprint 13 stories reviewed and approved. Minor notes
documented above. No blocking issues.

**Next agent**: Tester (Phase 8 — full test run TR-013)
