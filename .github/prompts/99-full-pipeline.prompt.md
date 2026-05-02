---
mode: agent
description: "Full E2E Pipeline — runs all 11 agents automatically without any manual steps"
---

# Full E2E Pipeline Orchestrator

You are running the **complete Eng2SQL SDLC pipeline** in a single automated session.
Your job is to work through every phase below IN ORDER, completing all incomplete work
without ever stopping to ask the user for input or prompting them to invoke another file.

Run : `@workspace #file:.github/prompts/99-full-pipeline.prompt.md`

---

## ⚠️ MANDATORY EXECUTION RULES

1. **Never stop between phases.** Complete every phase before finishing.
2. **Never ask the user to run another prompt.** You ARE the pipeline.
3. **Never issue a "handoff" asking the user to copy/paste a prompt.** Continue yourself.
4. **Check existing outputs first** — skip a phase only if ALL its output files exist and
   are complete (non-empty, have proper content, not just stubs).
5. **After every phase**, update `PROJECT_PROGRESS.md` (current agent, status, velocity).
6. **Follow all coding standards** from `.github/instructions/developer.instructions.md`
   for any code you write.

---

## Phase Readiness Check

Before starting Phase 2+, read these files to understand current project state:

- `PROJECT_PROGRESS.md`
- `docs/roadmap.md`
- All files matching `docs/epics/EPIC-*.md`
- All files matching `docs/user-stories/**/*.md`
- All files matching `docs/architecture/*.md`
- All files matching `docs/sprints/SPRINT-*.md`

---

## PHASE 1 — Epic Writing

**Agent**: Epic Writer (`02-epic-writer.prompt.md`)

**Skip if**: `docs/epics/` contains all of EPIC-001 through EPIC-005 with non-empty content.

**Execute if**: Any epic file is missing.

**Work to do**:
Read `.github/prompts/02-epic-writer.prompt.md` fully, then execute its complete
instructions: create all missing `docs/epics/EPIC-<NNN>-<slug>.md` files following
the exact format defined in that prompt. Update `PROJECT_PROGRESS.md`.

---

## PHASE 2 — User Story Writing

**Agent**: User Story Writer (`03-user-story-writer.prompt.md`)

**Skip if**: All user stories listed in the epics' "Child User Stories" sections exist
as files in `docs/user-stories/sprint-*/`.

**Execute if**: Any user story file is missing.

**Work to do**:
Read `.github/prompts/03-user-story-writer.prompt.md` fully, then execute its complete
instructions: create all missing `docs/user-stories/<sprint>/US-<NNN>-<slug>.md` files.
Update epic files to tick child story checkboxes. Update `PROJECT_PROGRESS.md`.

---

## PHASE 3 — Architecture

**Agent**: Architect (`04-architect.prompt.md`)

**Skip if**: All of these files exist and are non-empty:
- `docs/architecture/system-design.md`
- `docs/architecture/ADR-001-streamlit.md` through `ADR-005-yaml-schema.md`
- `docs/architecture/api-contracts.md`
- `docs/architecture/security.md`

**Execute if**: Any architecture file is missing.

**Work to do**:
Read `.github/prompts/04-architect.prompt.md` fully, then execute its complete
instructions: create all missing architecture documents. Update `PROJECT_PROGRESS.md`.

---

## PHASE 4 — Sprint Planning

**Agent**: Scrum Master (`01-scrum-master.prompt.md`)

**Skip if**: `docs/sprints/SPRINT-1.md` through `docs/sprints/SPRINT-4.md` all exist,
AND `docs/sprints/SPRINT-1-retro.md` through `docs/sprints/SPRINT-4-retro.md` all exist.

**Execute if**: Any sprint plan or retrospective file is missing.

**Work to do**:
Read `.github/prompts/01-scrum-master.prompt.md` fully, then execute its complete
instructions: create all missing sprint plan and retrospective files. Update
`docs/roadmap.md` story statuses. Update `PROJECT_PROGRESS.md`.

---

## PHASE 5 — Development

**Agent**: Developer (`05-developer.prompt.md`)

**Skip if**: All of the following are true:
- `src/services/sql_generator.py` exists and implements `SQLGenerator.generate_sql()`
- `src/services/schema_detector.py` exists and implements both `load_static_schema()` and `detect_live_schema()`
- `src/services/db_connector.py` exists and implements `create_engine()`, `test_connection()`, `execute_query()`
- `src/components/sidebar.py`, `query_input.py`, `sql_output.py`, `schema_viewer.py`, `progress_tracker.py` all exist
- `src/app.py` exists with the full 4-step Streamlit flow
- `src/utils/exceptions.py` and `src/utils/logger.py` exist
- `src/models/config.py` exists with all dataclasses
- `tests/unit/test_sql_generator.py`, `tests/unit/test_schema_detector.py`, `tests/integration/test_db_connector.py` all exist
- `tests/conftest.py` exists with `sqlite_engine` and `app_config` fixtures

**Execute if**: Any source file listed above is missing or is an empty stub.

**Work to do**:
Read `.github/prompts/05-developer.prompt.md` and `.github/instructions/developer.instructions.md`
fully. Implement all missing source files following the exact coding standards:
- `from __future__ import annotations`
- Full type hints, Google-style docstrings, parameterised queries only
- No hardcoded secrets; use `os.getenv()`
- Raise specific exceptions from `utils/exceptions.py`

After implementing, also update:
- `docs/guides/user-guide.md` for any user-facing changes
- `docs/guides/developer-guide.md` for any API/service changes
- `README.md` if env vars or setup steps changed

Update `PROJECT_PROGRESS.md`.

---

## PHASE 6 — Code Review

**Agent**: Code Reviewer (`06-code-reviewer.prompt.md`)

**Skip if**: A review file exists in `docs/code-reviews/` that covers the current sprint's
implemented stories (i.e. `CR-002` exists if Sprint 2 code has never been reviewed).

**Execute if**: Any implemented sprint is missing a code review document.

**Work to do**:
Read `.github/prompts/06-code-reviewer.prompt.md` fully. Review all source files in `src/`
against the review checklist (correctness, security, style, tests, docs). Create
`docs/code-reviews/CR-<NNN>-<slug>.md` for each un-reviewed sprint. If issues are found,
fix them directly in the source files (do not leave issues open for a manual developer
pass). Update `PROJECT_PROGRESS.md`.

---

## PHASE 7 — Test Case Writing

**Agent**: Test Case Writer (`07-test-case-writer.prompt.md`)

**Skip if**: Test case files in `docs/test-cases/` cover ALL implemented user stories.

**Execute if**: Any user story lacks a corresponding test case document.

**Work to do**:
Read `.github/prompts/07-test-case-writer.prompt.md` fully. Write BDD-style test case
documents for all uncovered stories. Create the corresponding `pytest` test functions in
`tests/unit/` or `tests/integration/` as appropriate. Update `PROJECT_PROGRESS.md`.

---

## PHASE 8 — Testing

**Agent**: Tester (`08-tester.prompt.md`)

**Skip if**: `docs/test-results/` contains a test result file for every implemented sprint
AND the most recent run shows all tests passing.

**Execute if**: Any sprint is missing a test results document.

**Work to do**:
Read `.github/prompts/08-tester.prompt.md` fully.
Run the test suite: execute `python -m pytest tests/ -q --cov=src --cov-report=term-missing`
in the terminal. Capture the output. Create `docs/test-results/TR-<NNN>-sprint-<N>.md`
with the full results. If tests fail, file bug reports in `docs/bug-reports/` and fix the
underlying code. Re-run until all tests pass. Update `PROJECT_PROGRESS.md`.

---

## PHASE 9 — Deployment

**Agent**: Deployment Agent (`09-deployment-agent.prompt.md`)

**Skip if**: All of the following exist:
- `Dockerfile` (non-empty)
- `docker-compose.yml` (non-empty)
- `.env.example`
- `docs/deployment/RELEASE-1.0.0.md`
- `docs/deployment/runbook.md`

**Execute if**: Any deployment artefact is missing.

**Work to do**:
Read `.github/prompts/09-deployment-agent.prompt.md` fully. Create all missing deployment
artefacts. Ensure the GitHub Actions workflow in `.github/workflows/ci-cd.yml` is
complete and correct. Update `PROJECT_PROGRESS.md`.

---

## PHASE 10 — DevOps

**Agent**: DevOps (`10-devops.prompt.md`)

**Skip if**: All of the following exist:
- `.pre-commit-config.yaml`
- `docs/deployment/secrets-setup.md`
- `docs/deployment/monitoring.md`
- `.gitignore` contains `*.pem` and `*.key` entries

**Execute if**: Any DevOps artefact is missing.

**Work to do**:
Read `.github/prompts/10-devops.prompt.md` fully. Create all missing DevOps files.
Harden `.gitignore` with private key patterns. Update `PROJECT_PROGRESS.md`.

---

## PHASE 11 — Final Verification

After completing all phases:

1. Run `python -m pytest tests/ -q --cov=src --cov-report=term-missing` in the terminal
   and confirm all tests pass with ≥ 80% coverage.
2. Verify all epic ACs are ticked in `docs/epics/*.md`.
3. Update `PROJECT_PROGRESS.md`:
   - Set all sprint velocities to actual values
   - Set all phase rows to ✅ DONE / 100%
   - Set `Current Agent` to `Pipeline Complete`
   - Set `Next Action` to `🎉 All phases complete — project ready`
4. Print a final summary table of all phases executed and their outcomes.

---

## Parallel Execution Note

Phases 1–4 (planning/docs) can run in any order since they do not depend on code.
Phases 5–10 (implementation/QA/deploy) must run sequentially since each depends on the
previous. The pipeline enforces sequential execution by default.
