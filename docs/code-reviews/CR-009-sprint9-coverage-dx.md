# CR-009 — Sprint 9 Code Review (Coverage Completeness & Developer Experience)

**Sprint**: Sprint 9
**Reviewer**: Pipeline (Code Reviewer agent)
**Date**: 2026-05-07
**Stories Reviewed**: US-040, US-041, US-042, US-043
**Bug Fixes Reviewed**: BUG-006 (fixed in same pipeline run)
**Verdict**: ✅ **Approved**

---

## 1. Files Changed in Sprint 9

### New files
- [tests/unit/test_sidebar_step2.py](../../tests/unit/test_sidebar_step2.py) — US-040
- [tests/integration/test_db_connector_live.py](../../tests/integration/test_db_connector_live.py) — US-042
- [docs/architecture/postgresql-epic-evaluation.md](../architecture/postgresql-epic-evaluation.md) — US-043
- [docs/test-cases/TC-040-bug-006-wsl2-localhost-fail-fast.md](../test-cases/TC-040-bug-006-wsl2-localhost-fail-fast.md) — BUG-006

### Modified files
- [src/services/mongo_connector.py](../../src/services/mongo_connector.py) — BUG-006 (Strategy E)
- [tests/unit/test_mongo_connector.py](../../tests/unit/test_mongo_connector.py) — BUG-006 regression tests
- [tests/conftest.py](../../tests/conftest.py) — `mysql_container` fixture (US-042)
- [pyproject.toml](../../pyproject.toml) — `docker` marker (US-042)
- [requirements.txt](../../requirements.txt) — `testcontainers[mysql]` (US-042)
- [docs/guides/developer-guide.md](../guides/developer-guide.md) — AppTest quirks section (US-041) + WSL2 networking note (BUG-006)
- [docs/roadmap.md](../roadmap.md) — EPIC-009 backlog entry (US-043)

---

## 2. Review Checklist

| Category        | Item                                                                  | Result |
| --------------- | --------------------------------------------------------------------- | :----: |
| **Correctness** | All AC scenarios covered by automated tests                           |   ✅    |
|                 | No mutations to existing public API signatures                        |   ✅    |
|                 | New code paths exercised by tests                                     |   ✅    |
| **Security**    | No hardcoded secrets                                                  |   ✅    |
|                 | No SQL/NoSQL injection vectors introduced                             |   ✅    |
|                 | testcontainers MySQL container uses non-default password (`testroot`) |   ✅    |
|                 | WSL2 fail-fast hint does not leak credentials                         |   ✅    |
| **Style**       | `from __future__ import annotations` on every new module              |   ✅    |
|                 | Type hints on every public function                                   |   ✅    |
|                 | Google-style docstrings on every public function                      |   ✅    |
|                 | PEP 8 compliance (manual review — `ruff` not installed in this env)   |   ✅    |
| **Tests**       | Each new code path has a unit test                                    |   ✅    |
|                 | Integration tests skip gracefully when Docker is unavailable          |   ✅    |
|                 | All tests pass: 144 passed / 4 skipped (Docker)                       |   ✅    |
| **Docs**        | Developer guide updated for every API/pattern change                  |   ✅    |
|                 | User-facing docs unchanged (no UX changes in Sprint 9)                |   ✅    |
|                 | README.md unchanged (no setup/env-var changes)                        |   ✅    |

---

## 3. Per-Story Review Notes

### US-040 — Mock-patched AppTest tests for `_render_step2`

- **Coverage**: 8 new tests cover success path (4), failure path (3), and edge case (1).
- **Patch targets**: `services.db_connector.DBConnector.create_engine` and
  `services.schema_detector.SchemaDetector.detect_live_schema` are patched at the
  class level — correctly avoids the import-source vs consumer-path trap documented in US-041.
- **Quirks handled**: `default_timeout=10`, `del at.session_state[...]` (not `.pop`),
  empty schema dict to bypass `SchemaViewerComponent.render` column iteration.
- **No source code changes needed** — the existing `_render_step2` was already correct;
  this story added the missing test coverage only.

### US-041 — AppTest quirks documentation

- New "Streamlit AppTest Known Quirks" subsection added under **Testing Guide**.
- Quick-reference table covers all 5 quirks discovered in Sprints 8–9.
- Each quirk has a wrong / correct code example.
- Cross-links to `tests/unit/test_sidebar_ui.py` and `tests/unit/test_sidebar_step2.py`
  as canonical examples.

### US-042 — Docker MySQL integration fixture

- Fixture is `scope="session"` to keep cold-start cost <30 s for the full integration suite.
- Two-level skip: missing `testcontainers` import → skip; Docker daemon unreachable → skip.
- `pytest.mark.docker` added to `pyproject.toml` markers; tests in
  `test_db_connector_live.py` carry `pytestmark = [integration, docker]` so both
  exclusion filters work.
- Coverage caveat: `db_connector.py` reaches ~90% only when Docker is available.
  In the default unit-only run it stays at 79% — this is documented in the US DoD checklist
  rather than artificially boosted by mocks.
- **One concern**: container teardown wraps `container.stop()` in a `try/except` that
  swallows all exceptions. This is intentional (avoid masking the real test failure) but
  worth flagging for the runbook.

### US-043 — PostgreSQL epic evaluation

- Evaluation document is structured (audit / driver choice / effort / risks / decision).
- Recommendation is ✅ GO with 13 pts effort estimate, fits sprint capacity.
- EPIC-009 file was intentionally deferred to Sprint 10 first phase (per evaluation §5)
  to avoid speculative epic files. This is a **deliberate** open DoD checkbox in US-043,
  documented inline.

### BUG-006 — WSL2 localhost MongoDB fail-fast

- Strategy E (UX fail-fast) was the correct choice; Strategy A (`directConnection=True`)
  was correctly rejected because the existing
  [test_connect_does_not_force_direct_connection](../../tests/unit/test_mongo_connector.py#L58-L72)
  forbids it (BUG-005 invariant).
- Fail-fast guard checks three conditions: probe failed, host in `_LOOPBACK_HOSTS`,
  `_is_wsl2()` true. All three needed → no false positives on Windows / macOS / native Linux.
- Error message includes actionable hint pointing at `/etc/resolv.conf` and
  `host.docker.internal`.

---

## 4. Issues Raised

None. All findings are addressed inline.

---

## 5. Approval

✅ **Approved for Sprint 9 close-out.**

All Sprint 9 user stories and BUG-006 are ready for the Tester / Integration Test Agent
phases.
