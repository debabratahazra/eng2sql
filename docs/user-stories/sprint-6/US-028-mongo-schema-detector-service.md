# US-028: MongoSchemaDetector Service

**Epic**: EPIC-007
**Sprint**: Sprint 6
**Points**: 5
**Priority**: Must Have

## User Story

> As a **system**, I want a `MongoSchemaDetector` service that samples documents from
> every collection in a MongoDB database and infers a schema (collection names +
> top-level field names + best-effort types) so that the SQL/MQL generator can
> produce accurate queries against a live MongoDB instance.

## Acceptance Criteria

```gherkin
Feature: MongoSchemaDetector Service

  Scenario: detect_schema() returns TableSchema from populated collections
    Given a MongoDB database with collection "users" containing documents
      with fields _id, name, email
    When MongoSchemaDetector.detect_schema(db) is called
    Then the returned TableSchema contains key "users"
    And the column list includes SchemaColumn entries for "_id", "name", "email"

  Scenario: detect_schema() handles empty collections
    Given a MongoDB database with an empty collection "logs"
    When MongoSchemaDetector.detect_schema(db) is called
    Then "logs" is present in the result with an empty column list

  Scenario: detect_schema() unions fields across sampled documents
    Given collection "products" has some documents with field "price"
      and other documents with field "discount"
    When MongoSchemaDetector.detect_schema(db) is called
    Then the column list for "products" contains both "price" and "discount"

  Scenario: detect_schema() respects sample_size limit
    Given collection "events" has 500 documents
    When MongoSchemaDetector.detect_schema(db, sample_size=50) is called
    Then at most 50 documents are sampled per collection

  Scenario: detect_schema() raises SchemaDetectionError on driver failure
    Given a database object that raises an exception on list_collection_names()
    When MongoSchemaDetector.detect_schema(db) is called
    Then a SchemaDetectionError is raised
```

## Technical Notes
- New file: `src/services/mongo_schema_detector.py`
- Use `db.list_collection_names()` to enumerate collections
- For each collection: `db[name].find({}, limit=sample_size)` — sample documents
- Union top-level keys across all sampled documents per collection
- Map BSON Python types to type strings:
  - `int` / `float` → `"Number"`; `str` → `"String"`; `bool` → `"Boolean"`;
  - `dict` → `"Object"`; `list` → `"Array"`; `ObjectId` → `"ObjectId"`;
  - anything else → `"Mixed"`
- `SchemaColumn.nullable` = `True` for all MongoDB fields (document schema is flexible)
- `SchemaColumn.primary_key` = `True` only for `_id` field
- Wrap driver errors in `SchemaDetectionError`

## Definition of Done
- [x] Code implemented
- [x] Unit tests passing
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated (if needed)

## Status
✅ Done
