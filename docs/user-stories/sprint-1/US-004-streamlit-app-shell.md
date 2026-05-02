# US-004: Streamlit App Shell

**Epic**: EPIC-002
**Sprint**: Sprint 1
**Points**: 2
**Priority**: Must Have

## User Story

> As a **user**, I want a Streamlit web page that loads cleanly and shows the app title
> and a brief description so that I know the tool is ready to use.

## Acceptance Criteria

```gherkin
Feature: Streamlit App Shell

  Scenario: App loads successfully
    Given the app is started with "streamlit run src/app.py"
    When I open http://localhost:8501 in a browser
    Then I see the title "Eng2SQL — English to SQL Generator"
    And I see a subtitle describing the tool's purpose
    And the sidebar shows mode selection options

  Scenario: Default mode is Static Schema
    When the app loads for the first time
    Then "Static Schema" is selected as the default mode in the sidebar
    And no database connection form is shown

  Scenario: Page is responsive
    When the app loads
    Then there are no Python exceptions in the terminal
    And the page renders in under 3 seconds
```

## Technical Notes
- `st.set_page_config(page_title="Eng2SQL", page_icon="🗄️", layout="wide")`
- Sidebar: radio buttons for "Static Schema" / "Live Database"
- Use `st.session_state` to persist mode selection across reruns

## Definition of Done
- [x] `src/app.py` created with working Streamlit shell
- [x] `src/components/sidebar.py` created
- [x] App loads without errors
- [x] Code review approved

## Status
✅ DONE
