# US-005: Query Input Component

**Epic**: EPIC-002
**Sprint**: Sprint 1
**Points**: 3
**Priority**: Must Have

## User Story

> As a **user**, I want a text area labelled "Ask in English" and a "⚡ Generate SQL"
> button so that I can trigger SQL generation from the UI.

## Acceptance Criteria

```gherkin
Feature: Query Input Component

  Scenario: User enters a question and clicks Generate SQL
    Given the app is loaded in Static Schema mode
    When I type "Show all customers" in the text area
    And I click "⚡ Generate SQL"
    Then the question is passed to the SQL generation service
    And a step-by-step progress indicator appears

  Scenario: Empty question shows warning
    Given the text area is empty
    When I click "⚡ Generate SQL"
    Then a warning "⚠️ Please enter a question before generating SQL." is displayed
    And no SQL generation is attempted

  Scenario: Whitespace-only question is rejected
    Given the text area contains only spaces
    When I click "⚡ Generate SQL"
    Then the same warning is displayed

  Scenario: Button label is correct
    When the app loads
    Then a button labelled "⚡ Generate SQL" is visible
    And a text area with placeholder text is visible
```

## Technical Notes
- Component class: `QueryInputComponent` in `src/components/query_input.py`
- `render()` returns the stripped question string if button clicked with valid input, else `None`
- Uses `st.text_area` (height=120) and `st.button` (type="primary")
- Hint caption shown beside the button using `st.columns([1, 3])`

## Definition of Done
- [x] `QueryInputComponent.render()` implemented in `src/components/query_input.py`
- [x] Empty / whitespace input shows `st.warning` and returns `None`
- [x] Wired into `src/app.py` main loop
- [x] Code review approved (CR-001)

## Status
✅ DONE
