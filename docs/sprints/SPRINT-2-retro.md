# Sprint 2 Retrospective

**Sprint**: Sprint 2 — Core UI + Dynamic Schema
**Date**: 2026-05-28
**Facilitator**: Scrum Master

---

## What Went Well

- Full 21-point velocity maintained — all 5 stories delivered
- `SchemaViewerComponent` cleanly renders any `TableSchema` — reusable for future dialects
- `execute_query()` SELECT-only guard prevents write operations — strong security boundary
- `DBConnector` integration tests run entirely on SQLite in-memory — zero CI infrastructure needed
- Error handling (`DatabaseConnectionError`, `QueryExecutionError`) surfaces cleanly in UI via `st.error()`
- Connection status indicator (✅ / ❌) provides immediate user feedback

## What Could Be Improved

- US-010 and US-011 story files were initially missing from `docs/user-stories/sprint-2/` —
  story file creation should be verified against epic child list before sprint start
- Schema caching invalidation is manual (Refresh button only) — automatic cache bust on
  reconnect would improve UX

## Action Items

| Action                                                                     | Owner            | Due                           |
| -------------------------------------------------------------------------- | ---------------- | ----------------------------- |
| Verify all epic child stories have corresponding files before sprint start | Scrum Master     | Sprint 3 planning             |
| Add automatic schema cache invalidation on new connection                  | Developer        | Sprint 3 (if capacity allows) |
| Write TC-011 to TC-013 test cases for Sprint 2 additions                   | Test Case Writer | Sprint 3                      |
