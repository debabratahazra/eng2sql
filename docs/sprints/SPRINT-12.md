# Sprint 12 — MQL Query Execution & Dynamic Label

**Sprint**: 12
**Goal**: Deliver end-to-end MQL query execution from the Streamlit UI, eliminating the
"not yet supported" placeholder and giving MongoDB the same execute→results experience
as MySQL and PostgreSQL.
**Epic**: EPIC-009
**Start**: 2026-05-07
**Points**: 16
**Status**: ✅ Done

---

## Sprint Backlog

| Story  | Title                                              | Points | Status |
| ------ | -------------------------------------------------- | ------ | ------ |
| US-057 | Dynamic output label (SQL → MQL)                   | 3      | ✅ Done |
| US-058 | MongoDB system prompt — structured JSON MQL output | 3      | ✅ Done |
| US-059 | `MongoQueryExecutor` service                       | 5      | ✅ Done |
| US-060 | Execute MQL button + results in UI                 | 5      | ✅ Done |

**Total**: 16 story points

---

## Definition of Done Checklist

- [x] All 4 user stories implemented.
- [x] Unit tests pass (≥ 90% coverage on new modules).
- [x] All 199 pre-existing unit tests pass.
- [x] `ruff` lint clean.
- [x] `docs/guides/user-guide.md` updated.
- [x] `docs/guides/developer-guide.md` updated.
- [x] `PROJECT_PROGRESS.md` updated.

---

## Architecture Decisions

No new ADRs required — the new `MongoQueryExecutor` follows the existing service-layer
pattern (stateless class, `QueryExecutionError` for failures, `pd.DataFrame` return type,
no `eval()`). The LLM output contract (structured JSON) is documented in EPIC-009.

---

## Notes

- Security: `json.loads()` only — no `eval()` or shell calls anywhere in the executor.
- Auto-limit: `$limit: 1000` is appended when no terminal grouping/limit stage exists.
- `_id` ObjectId values are `str()`-converted so that `st.dataframe` can render them.
- Backward compatibility: `SQLOutputComponent.render()` keeps `db_type="MySQL"` default.
