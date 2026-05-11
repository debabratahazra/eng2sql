# Sprint 6 Retrospective

**Sprint**: Sprint 6 — MongoDB Database Support
**Date**: 2026-07-28
**Facilitator**: Scrum Master

---

## What Went Well

- All 6 stories delivered at 28/28 points — largest sprint yet, velocity target hit
- `MongoDBConnector` and `MongoSchemaDetector` services are stateless, fully tested, and follow exactly the same patterns as MySQL services — easy for developers to pick up
- BSON type inference (`_BSON_TYPE_MAP`) handles the full range of MongoDB native types cleanly; "Mixed" fallback prevents schema-detection crashes on heterogeneous documents
- 83 tests, 92.41% coverage — significant improvement over Sprint 5 baseline
- MongoDB dialect in `SQLGenerator` required only a two-word change to the system prompt — demonstrates good abstraction in the LLM layer
- Hiding "Execute SQL" for MongoDB mode was a clean UI decision — no half-working functionality exposed to users
- `directConnection=True` fix (topology timeout BUG-005) found and resolved within the sprint — good regression test added
- BUG-004 (`None / No Auth` credential drop) filed and fixed before sprint close

## What Could Be Improved

- Sprint 6 was 28 points — the highest-velocity sprint so far; consider splitting large epics into smaller sprints to reduce WIP risk
- `MongoConfig.connection_uri` grew complex handling all auth edge cases — the URI-mode refactor (EPIC-008) was anticipated but deferred; should have been scoped-in to Sprint 6 to avoid the field-form workaround
- `directConnection=True` hardcoded in `mongo_connector.py` at sprint end — known to be incompatible with SRV URIs; left as a known limitation until Sprint 7
- MongoDB schema sampling uses a fixed `sample_size=100` with no UI control — user cannot adjust for large collections; a future enhancement
- No integration test for `MongoDBConnector` against a real MongoDB server — mocking is comprehensive but a Docker-based integration fixture would add confidence

## Action Items

| Action                                                 | Owner       | Due               |
| ------------------------------------------------------ | ----------- | ----------------- |
| Create EPIC-008 — MongoDB URI + credentials input mode | Epic Writer | Sprint 7 planning |
| Address `directConnection` SRV incompatibility         | Developer   | Sprint 7 (US-033) |
| Add `sample_size` UI control to roadmap backlog        | Product     | Future backlog    |
| Consider Docker-based MongoDB integration fixture      | Developer   | Future sprint     |

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

**Total delivered**: 115 story points across 30 stories in 6 sprints
