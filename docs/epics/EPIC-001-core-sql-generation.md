# EPIC-001: Core SQL Generation Engine

## Goal
Build the Python service that accepts an English-language question and returns a valid
MySQL SELECT statement using OpenAI GPT-5.2, with full schema context injected into the
system prompt.

## Business Value
Users with no SQL knowledge can query their MySQL databases using plain English, reducing
reliance on database administrators and accelerating data access.

## Scope

### In Scope
- `SQLGenerator` service class with `generate_sql(question, schema, dialect)` method
- OpenAI GPT-5.2 integration via the official `openai` SDK with custom `httpx.Client` (corporate CA cert + Bearer auth header)
- Base URL: `https://gpt4ifx.icp.infineon.com` (configurable via `OPENAI_BASE_URL`)
- Schema-aware system prompt engineering
- Error handling: `SQLGenerationError`, `ValidationError`
- Support for MySQL dialect (primary), with SQLite for testing
- Response cleaning (strip markdown code fences if present)

### Out of Scope
- Multi-turn SQL refinement / conversation history (future epic)
- SQL execution (covered in EPIC-003)
- Non-SELECT statements (INSERT/UPDATE/DELETE) — read-only by design

## Acceptance Criteria
- [x] AC-1: `generate_sql("Show all customers", schema)` returns a string beginning with `SELECT`
- [x] AC-2: Generated SQL references only tables and columns present in the provided schema
- [x] AC-3: Empty or whitespace-only question raises `ValueError`
- [x] AC-4: OpenAI API failure raises `SQLGenerationError` with a user-friendly message
- [x] AC-5: Unit tests pass with mocked OpenAI client (no real API calls in tests)
- [x] AC-6: Service is stateless and thread-safe

## Dependencies
- Depends on: None (first epic)
- Blocks: EPIC-002, EPIC-003

## Estimated Size
**T-Shirt Size**: M
**Estimated Sprints**: 1

## Child User Stories
- [x] US-001: Static Schema Configuration
- [x] US-002: OpenAI SQL Generation Service
- [x] US-003: Prompt Engineering for Schema Context
- [x] US-012: Error Handling & User Feedback

## Status
- [x] Draft
- [x] Reviewed
- [x] Accepted
