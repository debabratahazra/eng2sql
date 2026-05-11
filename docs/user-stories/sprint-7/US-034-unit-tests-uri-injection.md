# US-034: Unit Tests for URI Injection and Validation

**Epic**: EPIC-008 — MongoDB Flexible Connection Input
**Sprint**: Sprint 7
**Status**: ✅ Done
**Points**: 3
**Assignee**: Developer Agent

---

## User Story

> As a developer,
> I want comprehensive unit tests for all URI-mode code paths,
> so that regressions in credential injection and SRV detection are caught automatically.

---

## Acceptance Criteria

```gherkin
Scenario: All URI injection scenarios are tested
  Given tests/unit/test_mongo_connector.py
  Then TestMongoConfig covers:
    - raw_uri + username → credentials injected
    - raw_uri + empty username → URI unchanged
    - raw_uri with embedded creds → ValueError raised
    - raw_uri with special-char password → percent-encoded
    - raw_uri with SRV scheme → scheme preserved
    - raw_uri empty → field-based URI (regression guard)

Scenario: directConnection suppression is tested
  Given tests/unit/test_mongo_connector.py::TestMongoDBConnector
  Then there is a test asserting directConnection=True for standard URI
  And a test asserting directConnection absent for SRV URI

Scenario: Coverage gate maintained
  When pytest --cov=src --cov-fail-under=80 runs
  Then total coverage is ≥ 80%
```

---

## Definition of Done

- [x] All scenarios above have passing tests in `tests/unit/test_mongo_connector.py`
- [x] `pytest --cov=src --cov-fail-under=80` exits 0
- [x] No existing tests broken
