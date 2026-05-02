# EPIC-002: Streamlit UI — Basic Query Interface

## Goal
Create the Streamlit web application providing a clean, step-by-step interface for users
to type an English question, watch SQL being generated in real time, and view the result.

## Business Value
A zero-setup, browser-accessible UI makes the tool accessible to non-technical users and
eliminates the need for a separate frontend team.

## Scope

### In Scope
- Streamlit app entry point (`src/app.py`)
- Query input component (text area + "Generate SQL" button)
- Step-by-step progress spinner/status messages (Parsing → Generating → Done)
- SQL output panel with syntax highlighting (`st.code`)
- Sidebar for mode selection (Static Schema / Live Database)
- Session state management for query history

### Out of Scope
- User authentication / login (future)
- Saving / exporting queries (future)
- Multi-database support beyond MySQL/SQLite

## Acceptance Criteria
- [x] AC-1: App loads at `http://localhost:8501` with title "Eng2SQL — English to SQL Generator"
- [x] AC-2: User types a question, clicks "Generate SQL", and sees step indicators updating
- [x] AC-3: Generated SQL is displayed in a syntax-highlighted code block
- [x] AC-4: Sidebar shows "Static Schema" mode selected by default
- [x] AC-5: Empty query submission shows a `st.warning` message, not an error
- [x] AC-6: App remains responsive during OpenAI API call (spinner shown)

## Dependencies
- Depends on: EPIC-001 (SQL Generator service must exist)
- Blocks: EPIC-003 (Dynamic Schema mode extends this UI)

## Estimated Size
**T-Shirt Size**: M
**Estimated Sprints**: 1

## Child User Stories
- [x] US-004: Streamlit App Shell
- [x] US-005: Query Input Component
- [x] US-006: Step-by-Step Progress Display
- [x] US-007: SQL Output Panel

## Status
- [x] Draft
- [x] Reviewed
- [x] Accepted
