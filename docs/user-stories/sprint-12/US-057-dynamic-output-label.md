# US-057: Dynamic Output Label — "Generated SQL" vs "Generated MQL"

**Epic**: EPIC-009 — MQL Query Execution & Dynamic Output Label
**Sprint**: Sprint 12
**Points**: 3
**Status**: ✅ Done

---

## User Story

> As a user selecting MongoDB as my database type,
> I want the output panel to say **"Generated MQL"** instead of "Generated SQL",
> so that the label reflects what the query actually is.

---

## Acceptance Criteria

- [ ] When `db_type == "MongoDB"` the output panel subheader shows "🗒️ Generated MQL".
- [ ] When `db_type == "MySQL"` or `"PostgreSQL"` the subheader shows "🗒️ Generated SQL".
- [ ] The copy hint text updates accordingly:
  - MongoDB: "Copy the MQL above to use in your MongoDB client."
  - Others: "Copy the SQL above to use in your database client."
- [ ] The placeholder text (empty state) updates:
  - MongoDB: "Generated MQL will appear here after you submit a question."
  - Others: "Generated SQL will appear here after you submit a question."
- [ ] `SQLOutputComponent.render()` accepts an optional `db_type: str = "MySQL"` parameter.
- [ ] Existing callers that omit `db_type` continue to work (backward-compatible default).

---

## Definition of Done

- [x] `src/components/sql_output.py` updated.
- [x] `tests/unit/test_sql_output_label.py` added (≥ 4 tests).
- [x] All pre-existing tests pass.
- [x] `docs/guides/user-guide.md` updated.
- [x] Code review approved (CR-012).
- [x] Smoke tests passing (STR-003 scenario 4).
