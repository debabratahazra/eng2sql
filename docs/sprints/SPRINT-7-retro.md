# Sprint 7 Retrospective

**Sprint**: Sprint 7 — MongoDB URI Connection Input
**Date**: 2026-05-02
**Facilitator**: Scrum Master

---

## What Went Well

- All 5 stories delivered at 15/15 points — velocity target met
- `MongoConfig.raw_uri` field + `_connection_uri_from_raw()` is a clean, backward-compatible extension; field-based path (Sprint 6) entirely unchanged
- Defence-in-depth on embedded credentials: `ValueError` at the model layer + `st.warning` at the UI layer — caught at both boundaries
- SRV URI detection (`uri.startswith("mongodb+srv://")`) is simple and correct; `directConnection` suppressed via conditional `**kwargs` spread — no flag proliferation
- Sidebar refactor into three focused methods (`_render_mongo_step1`, `_render_mongo_step1_fields_mode`, `_render_mongo_step1_uri_mode`) improves readability and testability
- Coverage held at 92.57% despite 8 new tests — no regressions
- `mongo_input_mode` and `mongo_raw_uri` added to `_MONGO_KEYS` — state clears cleanly on reconnect or engine-switch
- `urllib.parse.urlparse` + `urlunparse` handles both `mongodb://` and `mongodb+srv://` correctly without custom parsing

## What Could Be Improved

- Sprint 7 was shorter (15 pts) than Sprint 6 (28 pts) — appropriate given the focused scope, but the two-week cadence means some capacity was underutilised; could have pulled in a roadmap backlog item
- `_render_mongo_step1_uri_mode` contains a local `import urllib.parse as _up` — minor style inconsistency; should be at module level; low priority
- `MongoConfig.__repr__` and the `else` branch in `_connection_uri_from_raw` remain uncovered (lines 104/108/126-127 in config.py) — cosmetic, coverage gate well above 80%
- No UI test for the mode toggle radio widget — `AppTest`-based sidebar tests remain a backlog item from Sprint 4 retro

## Action Items

| Action                                                                                       | Owner                  | Due                    |
| -------------------------------------------------------------------------------------------- | ---------------------- | ---------------------- |
| Move `import urllib.parse` in `_render_mongo_step1_uri_mode` to module level                 | Developer              | Next PR / housekeeping |
| Schedule `AppTest`-based sidebar UI tests (carried from Sprint 4 retro)                      | Scrum Master           | Sprint 8 planning      |
| Review roadmap backlog for next sprint candidate (PostgreSQL? Query history? MQL execution?) | Product / Scrum Master | Sprint 8 planning      |

---

## Cumulative Velocity

| Sprint   | Committed | Delivered | Cumulative |
| -------- | --------- | --------- | ---------- |
| Sprint 1 | 21        | 21        | 21         |
| Sprint 2 | 21        | 21        | 42         |
| Sprint 3 | 13        | 13        | 55         |
| Sprint 4 | 16        | 16        | 71         |
| Sprint 5 | 16        | 16        | 87         |
| Sprint 6 | 28        | 28        | 115        |
| Sprint 7 | 15        | 15        | 130        |

**Total delivered**: 130 story points across 35 stories in 7 sprints
