# US-033: URI Mode — directConnection Suppression for SRV URIs

**Epic**: EPIC-008 — MongoDB Flexible Connection Input
**Sprint**: Sprint 7
**Status**: ✅ Done
**Points**: 2
**Assignee**: Developer Agent

---

## User Story

> As a user connecting via a mongodb+srv:// URI,
> I want the app to automatically omit directConnection=True,
> so that the SRV-based topology lookup works correctly and my Atlas or replica-set connection succeeds.

---

## Acceptance Criteria

```gherkin
Scenario: Standard mongodb:// URI uses directConnection=True
  Given MongoConfig with raw_uri="mongodb://localhost:27017/"
  When MongoDBConnector.connect() is called
  Then MongoClient is constructed with directConnection=True

Scenario: SRV URI omits directConnection
  Given MongoConfig with raw_uri="mongodb+srv://cluster.mongodb.net/"
  When MongoDBConnector.connect() is called
  Then MongoClient is NOT constructed with directConnection=True

Scenario: Fields mode always uses directConnection=True
  Given MongoConfig with raw_uri="" (fields mode)
  When MongoDBConnector.connect() is called
  Then MongoClient is constructed with directConnection=True
```

---

## Definition of Done

- [x] `MongoDBConnector.connect()` inspects `config.connection_uri` for `mongodb+srv://` prefix
- [x] `directConnection=True` omitted for SRV URIs
- [x] Existing non-SRV behaviour unchanged
- [x] Unit tests cover both branches
