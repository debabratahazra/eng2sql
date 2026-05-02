# US-006: Step-by-Step Progress Display

**Epic**: EPIC-002
**Sprint**: Sprint 1
**Points**: 3
**Priority**: Must Have

## User Story

> As a **user**, I want to see step-by-step status messages (e.g. "Loading schema…",
> "Generating SQL…", "Done ✅") while SQL is being generated so that I know the system
> is working and can track progress.

## Acceptance Criteria

```gherkin
Feature: Step-by-Step Progress Display

  Scenario: Four steps shown during generation
    Given I have entered a valid question
    When I click "⚡ Generate SQL"
    Then I see "Step 1/4 — Loading schema…" appear
    And then "Step 2/4 — Building prompt…"
    And then "Step 3/4 — Generating SQL with OpenAI…"
    And then "Step 4/4 — Done ✅"

  Scenario: Progress collapses on completion
    Given SQL generation has completed
    When the final step "Done ✅" is added
    Then the st.status container collapses automatically
    And shows the label "Done ✅" in a completed state

  Scenario: Progress resets on new query
    Given previous steps are shown from a prior query
    When I submit a new question
    Then the progress tracker resets before showing new steps

  Scenario: No progress shown on empty input
    Given the text area is empty
    When I click "⚡ Generate SQL"
    Then no progress steps are displayed
```

## Technical Notes
- Component class: `ProgressTracker` in `src/components/progress_tracker.py`
- `reset()` clears `st.session_state["progress_steps"]`
- `update(message)` appends to the list and re-renders via `st.status()`
- Completion detected by checking `"Done ✅" in message`
- Session state key: `"progress_steps"`

## Definition of Done
- [x] `ProgressTracker.reset()` and `ProgressTracker.update()` implemented
- [x] Uses `st.status()` for expandable/collapsible display
- [x] Resets at start of each generation cycle in `src/app.py`
- [x] Code review approved (CR-001)

## Status
✅ DONE
