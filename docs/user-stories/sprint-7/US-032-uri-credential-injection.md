# US-032: URI + Credentials Mode — URI Parsing & Credential Injection in MongoConfig

**Epic**: EPIC-008 — MongoDB Flexible Connection Input
**Sprint**: Sprint 7
**Status**: ✅ Done
**Points**: 5
**Assignee**: Developer Agent

---

## User Story

> As a user,
> I want to paste a MongoDB URI (without embedded credentials) and supply my username and password separately,
> so that I can connect using my existing connection string without exposing credentials in the URI field.

---

## Acceptance Criteria

```gherkin
Scenario: URI with credentials merges them correctly
  Given MongoConfig with raw_uri="mongodb://localhost:27017/?authSource=admin", username="root", password="root"
  When connection_uri is accessed
  Then the URI is "mongodb://root:root@localhost:27017/?authSource=admin"

Scenario: URI with no username returns URI as-is
  Given MongoConfig with raw_uri="mongodb://localhost:27017/", username=""
  When connection_uri is accessed
  Then the URI equals "mongodb://localhost:27017/"

Scenario: URI with embedded credentials raises ValueError
  Given MongoConfig with raw_uri="mongodb://root:root@localhost:27017/"
  When connection_uri is accessed
  Then ValueError is raised with message containing "Remove credentials from the URI"

Scenario: Special characters in password are percent-encoded in URI mode
  Given MongoConfig with raw_uri="mongodb://localhost:27017/", username="user", password="p@ss!"
  When connection_uri is accessed
  Then the URI contains percent-encoded password

Scenario: SRV URI preserves the mongodb+srv scheme
  Given MongoConfig with raw_uri="mongodb+srv://cluster.mongodb.net/?authSource=admin", username="u", password="p"
  When connection_uri is accessed
  Then the returned URI starts with "mongodb+srv://"
  And contains "u" and percent-encoded "p"

Scenario: raw_uri empty falls back to field-based logic
  Given MongoConfig with raw_uri="" and individual host/port/username fields set
  When connection_uri is accessed
  Then the existing field-based URI is returned (EPIC-007 behaviour unchanged)
```

---

## Definition of Done

- [x] `MongoConfig` gains `raw_uri: str = ""` field
- [x] `connection_uri` property branches on `raw_uri` being non-empty
- [x] Credential injection uses `urllib.parse.urlparse` + `urllib.parse.quote_plus`
- [x] Embedded-credentials guard raises `ValueError` with clear message
- [x] Field-based path (existing logic) unchanged when `raw_uri == ""`
- [x] `_render_mongo_step1()` URI-mode branch builds `MongoConfig(raw_uri=..., username=..., password=...)`
- [x] All unit tests pass
