# US-060: Execute MQL Button + Results in UI

**Epic**: EPIC-009 — MQL Query Execution & Dynamic Output Label
**Sprint**: Sprint 12
**Points**: 5
**Status**: ✅ Done

---

## User Story

> As a user connected to MongoDB,
> I want a **"▶ Execute MQL"** button to appear after a query is generated,
> so that I can run the query and see the results immediately inside the app.

---

## Acceptance Criteria

- [ ] `app.py` removes the `st.info("MongoDB query execution is not yet supported …")` block.
- [ ] When `db_type == "MongoDB"`, `generated_sql` is non-empty, and `mongo_db` is in
  session state, a **"▶ Execute MQL"** button is rendered.
- [ ] Clicking the button calls `MongoQueryExecutor().execute(mongo_db, generated_sql)`.
- [ ] On success: `st.session_state["query_result"]` is set and `st.rerun()` is called.
- [ ] On `QueryExecutionError`: `st.error(f"MQL execution failed: {exc}")` is shown.
- [ ] The existing "Query Results" `st.dataframe` block renders MQL results the same
  way as SQL results.
- [ ] `SQLOutputComponent.render()` is called with the `db_type` argument so the label
  is correct.
- [ ] `app.py` imports `MongoQueryExecutor`.

---

## Definition of Done

- [x] `src/app.py` updated (import, button, error handling, `db_type` arg).
- [x] All pre-existing tests pass.
- [x] `docs/guides/user-guide.md` updated.
- [x] Code review approved (CR-012).
- [x] Smoke tests passing (STR-003 scenarios 5, 6, 7).
