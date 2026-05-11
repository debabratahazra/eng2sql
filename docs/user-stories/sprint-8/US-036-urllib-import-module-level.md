# US-036: Move `urllib.parse` Import to Module Level in Sidebar

**Epic**: EPIC-008
**Sprint**: Sprint 8
**Points**: 1
**Priority**: Should Have
**Source**: Retro — SPRINT-7-retro.md

## User Story

> As a **developer**, I want the `urllib.parse` import in `sidebar.py` to be at module
> level, so that the codebase follows a consistent style and the import is not re-evaluated
> on every function call.

## Acceptance Criteria

```gherkin
Feature: Module-level import for urllib.parse

  Scenario: Import is at module level
    Given the file src/components/sidebar.py
    When I inspect all import statements
    Then `import urllib.parse` appears at the top of the file (not inside a function)
    And no local `import urllib.parse as _up` exists inside `_render_mongo_step1_uri_mode`

  Scenario: Sidebar behaviour is unchanged after refactor
    Given the sidebar is rendered with URI mode selected
    When a valid mongodb+srv:// URI is entered
    Then the URI is parsed correctly and credentials are injected as before
```

## Technical Notes
- Investigation (Sprint 8): `urllib.parse` is NOT present in `src/components/sidebar.py` at
  all — URI parsing was moved to `src/models/config.py` (`MongoConfig._connection_uri_from_raw`)
  and `src/services/mongo_connector.py`, both of which import `urllib.parse` at module level
  (line 4 and line 8 respectively).
- The local `import urllib.parse as _up` described in the retro does not exist in the current
  codebase; the implementation is already compliant with this story's acceptance criteria.
- No code change required — verified 2026-05-06.

## Definition of Done
- [x] Code implemented (already compliant — urllib.parse at module level in config.py & mongo_connector.py)
- [x] Unit tests passing (existing tests cover the relevant code paths)
- [x] Code review approved
- [x] Acceptance criteria verified (grep confirms no local urllib import in sidebar.py)
- [x] Docs updated

## Status
✅ Done
