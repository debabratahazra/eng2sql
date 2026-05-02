# US-010: Schema Viewer Panel

**Epic**: EPIC-003
**Sprint**: Sprint 2
**Points**: 3
**Priority**: Must Have

## User Story

> As a **user**, I want to expand a collapsible "🗄️ Detected Schema" panel that lists
> all tables and columns so that I can verify my database connection is correct and
> understand which fields are available for querying.

## Acceptance Criteria

```gherkin
Feature: Schema Viewer Panel

  Scenario: Schema panel visible after successful connection
    Given I have connected to a live database in "Live Database" mode
    And schema has been detected
    When I look at the main page
    Then I see a collapsible "🗄️ Detected Schema (N tables)" expander
    And it is collapsed by default

  Scenario: Expanding the panel shows tables and columns
    Given the schema viewer panel is visible
    When I click to expand it
    Then each table is displayed with its column name, type, nullable, and PK flag
    And primary key columns show "🔑"
    And non-nullable columns show "❌" in the Nullable column

  Scenario: Refresh Schema button invalidates cache
    Given the schema panel is expanded
    When I click "🔄 Refresh Schema"
    Then st.session_state["detected_schema"] is cleared
    And the app reruns, triggering a fresh detect_live_schema() call

  Scenario: Empty database shows "No tables found"
    Given the connected database has no tables
    When the schema viewer renders
    Then it shows "No tables found." inside the expander

  Scenario: Panel not shown in Static Schema mode
    Given the mode is "Static Schema"
    When the app renders
    Then no schema viewer panel is shown
```

## Technical Notes
- Component class: `SchemaViewerComponent` in `src/components/schema_viewer.py`
- `render(schema)` uses `st.expander()` with `expanded=False`
- Columns displayed as `st.table(rows)` with keys: Column, Type, Nullable, PK
- "🔄 Refresh Schema" button resets `st.session_state["detected_schema"]` and calls `st.rerun()`
- Rendered in `src/app.py` only when `mode == "Live Database"` and `detected_schema` is set

## Definition of Done
- [x] `SchemaViewerComponent.render()` implemented in `src/components/schema_viewer.py`
- [x] Collapsible `st.expander` with table count in label
- [x] Per-table `st.table` with Column / Type / Nullable / PK columns
- [x] "🔄 Refresh Schema" button clears cache and reruns
- [x] "No tables found." shown for empty schema
- [x] Only rendered in Live Database mode in `src/app.py`
- [x] Code review approved (CR-001)

## Status
✅ DONE
