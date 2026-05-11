# STR-003 — Sprint 12 Smoke Test Results: MQL Query Execution

**Sprint**: 12
**Agent**: Smoke Test Agent
**Date**: 2026-05-07
**Phase**: 8c
**Test file**: `tests/smoke/test_sprint_12_smoke.py`

---

## Summary

| Metric            | Value                 |
| ----------------- | --------------------- |
| Total smoke tests | 10                    |
| **Passed**        | **10 ✅**              |
| Failed            | 0                     |
| Duration          | 13.51 s               |
| Platform          | win32 / Python 3.14.3 |

**Overall result: ✅ ALL SMOKE TESTS PASSED**

---

## Scenarios Covered

| #   | Test                                                 | US / Bug   | Result |
| --- | ---------------------------------------------------- | ---------- | ------ |
| 1   | App launches without error                           | Core       | ✅ PASS |
| 2   | Sidebar DB selector (MySQL / PG / Mongo)             | Core       | ✅ PASS |
| 3   | MySQL SQL generation (mocked OpenAI)                 | US-058     | ✅ PASS |
| 4   | MongoDB mode — output label shows "Generated MQL"    | US-057     | ✅ PASS |
| 5   | Execute MQL info box when no DB connected            | US-060     | ✅ PASS |
| 6   | Execute MQL button visible when `mongo_db` connected | US-060     | ✅ PASS |
| 7   | Execute MQL button click — success stores result     | US-059/060 | ✅ PASS |
| 8   | Empty query does not crash                           | Core       | ✅ PASS |
| 9   | Schema viewer renders MongoDB-style schema           | US-059     | ✅ PASS |
| 10  | PostgreSQL sslmode selector regression (US-056)      | Regression | ✅ PASS |

---

## Notes for Retro

- **Critical pattern verified**: `detected_schema` must inject `SchemaColumn` dataclass objects (not plain strings). Tests 4, 6, 7, 9 all use `SchemaColumn`. This pattern is stable.
- **Execute MQL info-box path** (TC-064 scenario 5): confirmed `st.info` is shown with "Connect to a MongoDB database" when `mongo_db` is not in session state.
- **Execute MQL button** (TC-064 scenario 6): `▶ Execute MQL` button rendered correctly when `mongo_db` is set.
- **"Generated MQL" label** (TC-064 scenario 4): `🗒️ Generated MQL` subheader confirmed.
- **No integration execution in smoke**: `MongoQueryExecutor.execute` is patched — no live MongoDB required.

---

## DoD Checkboxes Triggered

- [x] US-057: smoke test confirms dynamic MQL label renders (test 4)
- [x] US-059: smoke test confirms MongoQueryExecutor is wired into app (test 7)
- [x] US-060: smoke test confirms Execute MQL button and info-box paths (tests 5, 6, 7)
