# US-007: SQL Output Panel

**Epic**: EPIC-002
**Sprint**: Sprint 1
**Points**: 2
**Priority**: Must Have

## User Story

> As a **user**, I want to see the generated SQL in a syntax-highlighted code block
> so that I can read and copy it easily.

## Acceptance Criteria

```gherkin
Feature: SQL Output Panel

  Scenario: Generated SQL is displayed with syntax highlighting
    Given SQL generation has completed successfully
    When the output panel renders
    Then the SQL is displayed in a syntax-highlighted code block (language="sql")
    And a copy hint is shown below the code block

  Scenario: Clear button resets the output
    Given SQL is currently displayed
    When I click "🗑️ Clear"
    Then the SQL output is removed
    And the query result (if any) is also cleared
    And the panel shows the placeholder message

  Scenario: Placeholder shown before first generation
    Given no SQL has been generated yet
    When the output panel renders
    Then it shows "Generated SQL will appear here after you submit a question."

  Scenario: Markdown code fences are stripped before display
    Given OpenAI returns SQL wrapped in triple-backtick markdown fences
    When the SQL is passed to the output component
    Then no backticks or "sql" prefix are visible in the rendered code block
```

## Technical Notes
- Component class: `SQLOutputComponent` in `src/components/sql_output.py`
- `render(sql)` uses `st.code(sql, language="sql")` for syntax highlighting
- Empty `sql` argument renders `st.info(placeholder_message)` instead
- "🗑️ Clear" button sets `st.session_state["generated_sql"] = ""` and calls `st.rerun()`
- Markdown fence stripping (```` ```sql ``` ````) done in `SQLGenerator._clean_response()`

## Definition of Done
- [x] `SQLOutputComponent.render()` implemented in `src/components/sql_output.py`
- [x] Syntax-highlighted code block using `st.code(..., language="sql")`
- [x] "🗑️ Clear" button resets `generated_sql` and `query_result` session state
- [x] Placeholder info message shown when `sql` is empty
- [x] Code review approved (CR-001)

## Status
✅ DONE
