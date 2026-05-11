# SPRINT-15 Retrospective

**Sprint**: 15  
**Dates**: 2025-07-17  
**Velocity**: 11 / 11 story points (100%)  
**Facilitator**: Retro Analyzer Agent

---

## Sprint Goal

> Achieve 100% unit test coverage across all `src/services/`, `src/models/`, and `src/utils/`  
> modules, add sidebar component unit tests, and verify the CI coverage-docker job.

**Outcome**: ✅ Goal achieved — 100% coverage on 568 statements, 301 unit tests passing.

---

## Sprint Board Summary

| Story     | Title                                | Points | Status   |
| --------- | ------------------------------------ | ------ | -------- |
| US-066    | `mongo_connector.py` coverage uplift | 3      | ✅ Done   |
| US-067    | `models/config.py` coverage uplift   | 2      | ✅ Done   |
| US-068    | `utils/network.py` coverage uplift   | 1      | ✅ Done   |
| US-069    | Sidebar component unit tests         | 3      | ✅ Done   |
| US-070    | Verify CI coverage-docker job        | 2      | ✅ Done   |
| **Total** |                                      | **11** | **100%** |

---

## What Went Well

1. **100% coverage milestone reached** — For the first time in the project, all measured  
   source modules (`services/`, `models/`, `utils/`) hit exactly 100% statement coverage.

2. **sys.modules import-blocking technique** — The pattern of setting  
   `sys.modules["pymongo"] = None` and reloading the module enabled testing the  
   import-time fallback branch (lines 14–15) that is otherwise impossible to cover  
   when pymongo is installed in the test environment.

3. **Sidebar unit tests without Streamlit runtime** — By patching  
   `components.sidebar.st.session_state` with a dict subclass and importing functions  
   lazily inside test methods, 19 sidebar tests run in 3 s without AppTest overhead.

4. **CI job already correct** — US-070 required zero code changes; the `coverage-docker`  
   job was implemented correctly in Sprint 9 and just needed verification.

5. **Zero regressions** — All 264 pre-Sprint-15 tests continued to pass throughout.

---

## What Could Be Improved

1. **`src/components/*` still excluded from coverage gate** — The sidebar, main_content,  
   and other component files are omitted from `--cov=src` because they tightly couple  
   Streamlit widget calls to business logic. Refactoring components to separate pure  
   logic from widget calls would allow measuring their coverage.

2. **app.py untested at the function level** — `src/app.py` is also excluded from coverage.  
   The Streamlit `AppTest` regression tests exercise it end-to-end but don't give  
   line-level coverage.

3. **coverage-docker job not verifiable locally without Docker** — US-070 was verified  
   by reading the YAML config; actual end-to-end CI execution can only be confirmed  
   in a GitHub Actions run.

4. **Sprint 15 sprint board had no stretch goals** — All stories were "coverage uplift"  
   tasks. Future sprints should mix feature work with quality work to keep the product  
   moving forward.

---

## Action Items for Sprint 16

| #   | Action                                                                                             | Owner     | Priority |
| --- | -------------------------------------------------------------------------------------------------- | --------- | -------- |
| 1   | Refactor sidebar component to separate pure logic from `st.*` calls to enable line coverage        | Developer | High     |
| 2   | Add `src/app.py` function-level unit tests (not AppTest) for pure helper functions if any exist    | Developer | Medium   |
| 3   | Trigger actual GitHub Actions workflow on a test branch to verify `coverage-docker` job end-to-end | DevOps    | Medium   |
| 4   | Investigate `pytest-xdist` parallel execution to reduce 88 s unit suite runtime                    | DevOps    | Low      |

---

## Metrics

| Metric                 | Sprint 14 End | Sprint 15 End |
| ---------------------- | ------------- | ------------- |
| Total unit tests       | 264           | **301**       |
| Total coverage         | 98.06%        | **100%**      |
| Story points delivered | 7             | **11**        |
| Cumulative points      | 212           | **223**       |
| Open bugs              | 0             | 0             |
