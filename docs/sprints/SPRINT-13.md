# Sprint 13 — Sidebar Refactor, Packaging & Test Hardening

**Sprint**: 13
**Goal**: Close the two longest-running carry-over items (US-051 sidebar mixin, US-054
pyproject optional deps) and harden the test suite with a live MongoDB Docker integration
test and `app.py` MQL unit tests.
**Epics**: EPIC-004 (quality), EPIC-010 (MQL hardening)
**Start**: TBD
**Points**: 9
**Status**: 🔲 Not Started

---

## Sprint Backlog

| Story  | Title                                                 | Points | Status        |
| ------ | ----------------------------------------------------- | ------ | ------------- |
| US-051 | Refactor sidebar — `RelationalConnectorSidebar` mixin | 3      | 🔲 Not Started |
| US-054 | `pyproject.toml` optional-dependency groups           | 1      | 🔲 Not Started |
| US-061 | `MongoQueryExecutor` live Docker integration test     | 3      | 🔲 Not Started |
| US-062 | `app.py` Execute MQL unit tests                       | 2      | 🔲 Not Started |

**Total**: 9 story points

---

## Sprint 13 Kick-off Action Items (Day 1)

From SPRINT-11-retro.md + SPRINT-12-retro.md action items:

- [ ] Update `docs/guides/developer-guide.md` — AppTest `SchemaColumn` injection pattern
- [ ] US-051 implementation begins
- [ ] US-054 ADR decision and implementation
- [ ] US-061 integration test file scaffolding

---

## Definition of Done Checklist

- [ ] US-051: sidebar.py LoC reduced ≥ 80 lines; all sidebar tests pass unchanged
- [ ] US-054: pyproject.toml optional groups added; README updated
- [ ] US-061: live Docker integration test created; skips cleanly without Docker
- [ ] US-062: test_app_mql_button.py created; ≥ 3 scenarios; all pass
- [ ] Developer guide AppTest SchemaColumn pattern section added
- [ ] Unit suite ≥ 234 tests passing
- [ ] Coverage gate ≥ 80 % (target: maintain ≥ 91 %)
- [ ] Smoke tests (Sprint 13) ≥ 10 scenarios passing
- [ ] Code review CR-013 approved
- [ ] `PROJECT_PROGRESS.md` updated

---

## Architecture Notes

- US-051: `RelationalConnectorSidebar` mixin stays internal to `components/sidebar.py` —
  no new public module created; existing test surface is preserved.
- US-054: ADR-006 to be created documenting optional-deps group decision.
- US-061: Use `testcontainers[mongo]` pattern matching the MySQL/PostgreSQL Docker tests.
- US-062: Direct `unittest.mock.patch("streamlit.*")` approach — no AppTest overhead.
