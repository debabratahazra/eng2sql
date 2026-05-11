# US-086 — CSV Export of Most Recent Result Set

**ID**: US-086  
**Epic**: EPIC-017  
**Sprint**: 20  
**Points**: 3  
**Status**: ✅ Done  
**Priority**: Medium

---

## User Story

As a **data analyst**, I want to download the most recent SQL/MQL query result as a
CSV file so that I can use the data in downstream tools (Excel, pandas, BI dashboards).

---

## Acceptance Criteria

- [ ] When a SQL/MQL result set is displayed in the app, a "⬇ Download CSV" button
  appears below the result table.
- [ ] Clicking the button triggers a `st.download_button` file download with the
  result as UTF-8 CSV.
- [ ] The downloaded file is named `eng2sql_results_<YYYYMMDD>.csv`.
- [ ] If the result set is empty (0 rows), the download button shows "No results to
  export" and is disabled.

---

## Technical Notes

- Extract `_result_to_csv(df) -> bytes` and `_export_filename(date_str) -> str` as
  pure helpers per ADR-007.
- `st.download_button` rendering stays under `# pragma: no cover`.
- The pure helpers are fully unit-testable with a pandas DataFrame fixture.

---

## Definition of Done

- [x] Code implemented
- [x] Pure helper(s) extracted and unit-tested
- [x] Code review approved
- [x] User story status set to ✅ Done
