# US-041: Document AppTest Quirks and Known Limitations in Developer Guide

**Epic**: EPIC-004 — Quality Assurance
**Sprint**: Sprint 9
**Points**: 2
**Priority**: Should Have
**Source**: Retro — SPRINT-8-retro.md Action Item 2

## User Story

> As a **developer writing or maintaining Streamlit tests**, I want a dedicated section in
> the developer guide that documents Streamlit `AppTest` quirks and limitations, so that
> future contributors do not repeat the same debugging cycles discovered in Sprint 8.

## Acceptance Criteria

```gherkin
Feature: AppTest documentation in developer guide

  Scenario: Chaining restriction documented
    Given the developer guide has an AppTest section
    Then it contains a note that .set_value() and .run() MUST NOT be chained
    And it includes a correct code example and a broken example

  Scenario: session_state access documented
    Given the developer guide has an AppTest section
    Then it documents that at.session_state["key"] must be used (not .get())
    And explains that SafeSessionState raises AttributeError on .get()

  Scenario: Default timeout documented
    Given the developer guide has an AppTest section
    Then it documents that default_timeout=10 is required for the first run
    And explains that the default 3-second timeout causes sporadic failures

  Scenario: Widget tree instability documented
    Given the developer guide has an AppTest section
    Then it documents that widget indices change between different app states
    And recommends testing each state direction independently (no round-trips)
```

## Technical Notes

- Target file: `docs/guides/developer-guide.md`
- Add a new subsection under **Testing** → **Streamlit AppTest Known Quirks**.
- Include a quick-reference table with: quirk name, wrong pattern, correct pattern.
- Reference `tests/unit/test_sidebar_ui.py` as the canonical working example.
- No code changes required — documentation only.

## Definition of Done

- [x] Code implemented (N/A — doc only)
- [x] `docs/guides/developer-guide.md` updated with AppTest quirks section
- [x] Code review approved
- [x] Acceptance criteria verified
- [x] Docs updated

## Status

✅ Done
