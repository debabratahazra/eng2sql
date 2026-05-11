# US-058: MongoDB System Prompt — Structured JSON MQL Output

**Epic**: EPIC-009 — MQL Query Execution & Dynamic Output Label
**Sprint**: Sprint 12
**Points**: 3
**Status**: ✅ Done

---

## User Story

> As a developer,
> I want the LLM to output a structured JSON object `{"collection": "…", "pipeline": […]}`
> when the dialect is MongoDB,
> so that the MQL executor can safely parse and run the query without `eval()`.

---

## Acceptance Criteria

- [ ] `sql_generator.py` contains a `"MongoDB"` entry in `_DIALECT_TIPS`.
- [ ] The MongoDB tips instruct the model to output **only** a JSON object with keys
  `collection` (string) and `pipeline` (array of aggregation stages).
- [ ] The tips include a concrete example of the expected output format.
- [ ] The tips instruct the model to add `{"$limit": 100}` as the last stage unless
  the user explicitly requests more rows.
- [ ] The tips instruct the model to use `$match`, `$sort`, `$project`, `$group` stages.
- [ ] No other text, markdown, or code fences are produced for MongoDB queries.

---

## Definition of Done

- [x] `src/services/sql_generator.py` updated (`_DIALECT_TIPS["MongoDB"]` added).
- [x] Unit test added covering `generate_sql()` with `dialect="MongoDB"` verifying the
  system prompt contains the JSON format instruction.
- [x] All pre-existing tests pass.
- [x] Code review approved (CR-012).
