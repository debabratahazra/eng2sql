# US-035: Documentation Updates for URI Connection Mode

**Epic**: EPIC-008 — MongoDB Flexible Connection Input
**Sprint**: Sprint 7
**Status**: ✅ Done
**Points**: 2
**Assignee**: Developer Agent

---

## User Story

> As a user or developer,
> I want the user guide and developer guide updated to document the URI input mode,
> so that I can understand how to use and extend this feature.

---

## Acceptance Criteria

```gherkin
Scenario: User guide documents URI mode
  Given docs/guides/user-guide.md
  Then a section describes "URI + credentials" mode with an example URI
  And notes that credentials must not be embedded in the URI

Scenario: Developer guide documents raw_uri field and session-state key
  Given docs/guides/developer-guide.md
  Then MongoConfig.raw_uri field is documented
  And mongo_input_mode session-state key is listed
  And the connection_uri branching logic is explained

Scenario: README feature table updated
  Given README.md capability table
  Then URI input mode is listed alongside the existing two-step connect description
```

---

## Definition of Done

- [x] `docs/guides/user-guide.md` updated with URI mode walkthrough
- [x] `docs/guides/developer-guide.md` updated with `raw_uri`, `mongo_input_mode`, SRV note
- [x] `README.md` capability table updated
