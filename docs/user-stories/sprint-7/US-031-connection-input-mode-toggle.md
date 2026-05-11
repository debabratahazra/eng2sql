# US-031: Connection Input Mode Toggle in MongoDB Sidebar

**Epic**: EPIC-008 — MongoDB Flexible Connection Input
**Sprint**: Sprint 7
**Status**: ✅ Done
**Points**: 3
**Assignee**: Developer Agent

---

## User Story

> As a user connecting to MongoDB,
> I want a toggle in the MongoDB connection form to switch between "Fields" and "URI + credentials" input modes,
> so that I can choose whichever connection style matches how I have my credentials.

---

## Acceptance Criteria

```gherkin
Scenario: Default mode is "Fields"
  Given I open the Streamlit app and select MongoDB
  When the MongoDB Step 1 form renders
  Then a "Connection input mode" radio is visible with options "Fields" and "URI + credentials"
  And "Fields" is selected by default

Scenario: Switching to URI mode hides individual fields
  Given the "Connection input mode" radio is showing
  When I select "URI + credentials"
  Then the Host, Port, Auth Source, and Auth Mechanism fields are hidden
  And a "MongoDB URI" text input and Username/Password fields are shown

Scenario: Switching back to Fields mode restores individual fields
  When I select "Fields"
  Then Host, Port, Auth Source, and Auth Mechanism fields reappear
  And the URI text box is hidden

Scenario: Selected mode persists across rerenders
  Given I select "URI + credentials"
  When Streamlit rerenders due to a widget interaction
  Then "URI + credentials" remains selected
  And st.session_state["mongo_input_mode"] equals "URI + credentials"
```

---

## Definition of Done

- [x] `st.radio("Connection input mode", ["Fields", "URI + credentials"])` added to `_render_mongo_step1()`
- [x] `st.session_state["mongo_input_mode"]` written on every render
- [x] Fields branch renders existing Host/Port/Username/Password/Auth Source/Auth Mechanism
- [x] URI branch renders only MongoDB URI + Username + Password
- [x] Mode survives Streamlit rerenders (key-based persistence)
- [x] Unit test for session-state key written
