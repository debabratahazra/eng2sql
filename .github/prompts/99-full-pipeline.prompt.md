---
mode: agent
description: "Full E2E Pipeline — runs all 12 agents automatically without any manual steps, including retro-driven sprint seeding and automatic next-sprint launch"
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
7. **User story file hygiene** — after completing work for any user story, you MUST update
   its `docs/user-stories/**/*.md` file before moving to the next phase:
   - Tick every DoD checkbox (`- [ ]` → `- [x]`) whose criterion your work satisfies.
   - Set the `## Status` section or `**Status**:` frontmatter line to `✅ Done` once ALL
     DoD items are checked.
   - Never leave a completed sprint with unchecked DoD boxes or a stale status field.
   - Use `grep_search` on `docs/user-stories/**/*.md` for `- [ ]` after Phase 5, 6, and 8
     to catch any missed boxes before proceeding.
8. **Retro-driven seeding** — PHASE 0 MUST run first on every pipeline invocation.
   New epics, stories, and bugs created in Phase 0 are automatically consumed by
   Phases 1–10 in the same run.
9. **Automated sprint cadence** — After Phases 5–8b complete for a sprint, the pipeline
   MUST continue automatically:
   a. **Phase 8c** (Smoke Testing) runs the full Streamlit app smoke-test suite for the
      just-completed sprint WITHOUT any user prompt; failures are fixed inline or filed
      as bug reports. The retro must NOT be blocked by smoke failures.
   b. **Phase 8d** (Scrum Master retro) writes `docs/sprints/SPRINT-<N>-retro.md` —
      smoke test outcomes from Phase 8c MUST be referenced in the retro.
   c. **Phase 8e** (Re-entry loop) immediately re-runs Phase 0 to process the new retro.
      If Phase 0 creates any new user stories or epics, the pipeline MUST continue through
      Phases 1–8e again for the new sprint — no human interaction required.
   d. The sprint loop continues until Phase 0 finds nothing new to seed (no unprocessed
      retros, no new stories). Only then does the pipeline proceed to Phase 9.
10. **Unit test gate** — a user story, bug fix, or task MUST NOT be marked ✅ Done until
    the per-story unit test trigger (inline in Phase 5 / Phase 11) has run and produced
    a passing UTR document.  If the inline trigger creates a bug report instead of passing,
    the story is marked ⏸ Blocked until Phase 11 resolves it.

---

## Phase Readiness Check

Before starting Phase 1+, read these files to understand current project state:

- `PROJECT_PROGRESS.md`
- `docs/roadmap.md`
- All files matching `docs/epics/EPIC-*.md`
- All files matching `docs/user-stories/**/*.md`
- All files matching `docs/architecture/*.md`
- All files matching `docs/sprints/SPRINT-*.md`
- All files matching `docs/sprints/SPRINT-*-retro.md`

---

## PHASE 0 — Retro Analysis (Sprint Feedback Loop)

**Agent**: Retro Analyzer (`11-retro-analyzer.prompt.md`)

**Skip if**: Every `docs/sprints/SPRINT-*-retro.md` file has a corresponding
`Retro Analyzer | Processed SPRINT-<N>-retro.md` entry in `PROJECT_PROGRESS.md`.
(Search the Agent Activity Log for that exact string for each sprint N.)

**Execute if**: Any retro file has NOT been processed yet.

**Work to do**:
Read `.github/prompts/11-retro-analyzer.prompt.md` and
`.github/instructions/retro-analyzer.instructions.md` fully, then execute every step
in that prompt:
1. Identify all unprocessed `SPRINT-*-retro.md` files.
2. Parse "What Could Be Improved" and "Action Items" sections of each.
3. Classify each finding and create the required artifacts:
   - Bug Reports → `docs/bug-reports/BUG-<NNN>-*.md`
   - User Stories → `docs/user-stories/sprint-<N+1>/US-<NNN>-*.md`
   - Epics → `docs/epics/EPIC-<NNN>-*.md`
   - Future Backlog items → append to `docs/roadmap.md` only
4. Create or update `docs/sprints/SPRINT-<N+1>.md` with the new stories and bugs.
5. Update `docs/roadmap.md` (new sprint section, epic progress, milestones, backlog).
6. Update `PROJECT_PROGRESS.md` (activity log, sprint board, overall status).

After this phase, proceed immediately to Phase 1. The new files created here will
cause Phases 1 and 2 to execute (since new epics/stories now exist without full coverage).

---

## PHASE 1 — Epic Writing

**Agent**: Epic Writer (`02-epic-writer.prompt.md`)

**Skip if**: Every epic referenced in `docs/roadmap.md`'s "Epic Progress" table exists
as a non-empty file in `docs/epics/`. (Phase 0 may have created new EPIC-NNN files that
require this phase to run even if EPIC-001 through EPIC-005 previously existed.)

**Execute if**: Any epic file referenced in the roadmap or created by Phase 0 is missing.

**Work to do**:
Read `.github/prompts/02-epic-writer.prompt.md` fully, then execute its complete
instructions: create all missing `docs/epics/EPIC-<NNN>-<slug>.md` files following
the exact format defined in that prompt. Update `PROJECT_PROGRESS.md`.

---

## PHASE 2 — User Story Writing

**Agent**: User Story Writer (`03-user-story-writer.prompt.md`)

**Skip if**: All user stories listed in ALL epics' "Child User Stories" sections exist
as files in `docs/user-stories/sprint-*/`. This includes any new epics created by Phase 0.

**Execute if**: Any user story file is missing (including stories seeded by Phase 0).

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

**Per-story unit test trigger (mandatory)**: After implementing each individual user
story (do NOT wait until all stories are done), immediately run the Unit Test Agent
for that story BEFORE moving to the integration test trigger:
1. Read `.github/prompts/14-unit-test-agent.prompt.md` and
   `.github/instructions/unit-test-agent.instructions.md`.
2. Check `tests/unit/test_<us-slug>.py` — create it if absent using the templates in
   the Unit Test Agent prompt.
3. Run unit tests for the new/modified modules:
   `python -m pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing`
4. **If unit tests fail**:
   a. Attempt an immediate fix (source code or test bug — diagnose first).
   b. Re-run — if still failing after one fix attempt, create a bug report at
      `docs/bug-reports/BUG-<NNN>-unit-<slug>.md` with status `🔲 Open` and mark the
      story ⏸ Blocked.  Phase 11 will handle it.
5. Verify overall coverage ≥ 80% (`--cov-fail-under=80`).
6. Create `docs/test-results/UTR-<NNN>-US-<NNN>.md` whether the tests passed or were
   deferred to a bug.
7. Tick the unit-test DoD checkboxes in the story file.
8. Update `PROJECT_PROGRESS.md` with the UTR outcome.

**Per-story integration test trigger (mandatory)**: After the unit test trigger passes
(or a bug is filed), immediately run integration tests for that story:
1. Check `tests/integration/test_<us-slug>.py` — create it if absent (follow the
   Integration Test Agent instructions in Phase 8b).
2. Run `pytest tests/integration/ -v --tb=short -m integration` restricted to the new
   test file.
3. **If the integration test fails**:
   a. Attempt an immediate fix in the same step (fix the source code or test fixture).
   b. Re-run the test — if it still fails after one fix attempt, create a bug report at
      `docs/bug-reports/BUG-<NNN>-<slug>.md` with status `🔄 In Progress`, record the
      failure details, and continue to the next user story.  The Bug Fix Loop (Phase 11)
      will handle it.
4. Create `docs/test-results/ITR-<NNN>-US-<NNN>.md` for the story whether the test
   passed or was deferred to a bug report.
5. Update `PROJECT_PROGRESS.md` with the ITR outcome before moving to the next story.

**US file update (mandatory)**: For every user story implemented in this phase:
1. Open its `docs/user-stories/**/*.md` file.
2. Tick all DoD checkboxes whose criteria are now met (implementation, unit tests written
   and passing, integration tests run, docs updated).
3. Set `**Status**:` or `## Status` to `✅ Done` when ALL boxes are checked (including
   the unit test gate from Rule 10).

Update `PROJECT_PROGRESS.md`.

---

## PHASE 5b — Unit Testing (Sprint-level sweep)

**Agent**: Unit Test Agent (`14-unit-test-agent.prompt.md`)

> **Note**: Per-story unit tests are triggered inline during Phase 5 (Development) and
> Phase 11 (Bug Fix Loop). Phase 5b is a **sprint-level sweep** that catches any story
> or fix that was missed or had a deferred failure.

**Skip if**: `docs/test-results/` contains a non-failing UTR document for every User
Story and Bug Fix completed in the current sprint.

**Execute if**: Any completed User Story or Bug Fix is missing a UTR document, OR any
existing UTR for this sprint records a failing test or unmet coverage.

**Work to do**:
Read `.github/prompts/14-unit-test-agent.prompt.md` and
`.github/instructions/unit-test-agent.instructions.md` fully, then for each story/fix
that still needs a UTR or has a failing UTR:

1. Check `tests/unit/test_<slug>.py` — create or extend it as needed.
2. Run the full unit suite:
   `python -m pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing --cov-fail-under=80`
3. **On failure**:
   a. **Attempt an immediate fix** — diagnose (wrong mock, missing branch, logic bug).
   b. Re-run once. If all tests pass → record ✅ in the UTR.
   c. If still failing → create (or update) a bug report at
      `docs/bug-reports/BUG-<NNN>-unit-<slug>.md` with status `🔲 Open`, full
      traceback, and the attempted fix. Record ❌ in the UTR and reference the BUG
      number. Phase 11 will handle it.
4. Create or update `docs/test-results/UTR-<NNN>-<trigger>.md` for each story/fix.
5. Tick unit-test DoD checkboxes in all affected story / bug-report files.
6. Run `ruff check tests/unit/` — fix any linting errors before proceeding.

Update `PROJECT_PROGRESS.md` after the sweep.

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
pass).

**US file update (mandatory)**: For every user story covered by the review, open its
`docs/user-stories/**/*.md` file and tick the `Code review approved` DoD checkbox.

Update `PROJECT_PROGRESS.md`.

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
underlying code. Re-run until all tests pass.

**US file update (mandatory)**: Once the test run is green, open each user story file for
the current sprint and tick all test-related DoD checkboxes (e.g. `Unit tests passing`,
`pytest --cov-fail-under=80 exits 0`, `No existing tests broken`, `Branch coverage ≥ N%`).

Update `PROJECT_PROGRESS.md`.

---

## PHASE 8b — Integration Testing (Sprint-level sweep)

**Agent**: Integration Test Agent (`13-integration-test-agent.prompt.md`)

> **Note**: Individual per-story and per-fix integration tests are triggered inline
> during Phase 5 (Development) and Phase 11 (Bug Fix Loop).  Phase 8b is a **sprint-level
> sweep** that catches any story or fix that was missed or had a deferred failure.

**Skip if**: `docs/test-results/` contains a non-failing ITR file for every User Story
and Bug Fix completed in the current sprint.

**Execute if**: Any completed User Story or Bug Fix is missing an ITR document, OR any
existing ITR for this sprint records a failing or Docker-deferred test.

**Work to do**:
Read `.github/prompts/13-integration-test-agent.prompt.md` and
`.github/instructions/integration-test-agent.instructions.md` fully, then for each
story/fix that still needs an ITR or has a failing ITR:

1. Check if `tests/integration/test_<slug>.py` exists — create it if absent, following
   the templates in the instructions file.
2. Check if `tests/conftest.py` has the required DB fixtures (MySQL / MongoDB / PostgreSQL)
   — add missing fixtures.
3. Run integration tests: `pytest tests/integration/ -v --tb=short -m integration`
4. **On failure**:
   a. **Attempt an immediate fix** — diagnose the failure (wrong fixture, missing env var,
      logic bug in the new code) and apply the fix directly.
   b. Re-run the failing test(s) once.  If they pass → record ✅ in the ITR.
   c. If they still fail after the fix attempt → create (or update) a bug report at
      `docs/bug-reports/BUG-<NNN>-<slug>.md` with full reproduction steps, the
      traceback, the attempted fix, and status `🔲 Open`.  Record ❌ in the ITR and
      reference the BUG number.  The Bug Fix Loop (Phase 11) will handle it.
5. Create or update `docs/test-results/ITR-<NNN>-<trigger>.md` for each story/fix with
   the final pass/fail/deferred outcome.
6. If integration tests require Docker and Docker is unavailable, register the tests with
   `@pytest.mark.docker` and document "Docker not available — test registered for CI"
   in the ITR file.  This is NOT treated as a failure.
7. Update `docs/guides/developer-guide.md` if new fixtures or markers were added.

Update `PROJECT_PROGRESS.md` after the sweep.

---

## PHASE 8c — Smoke Testing (Sprint-end gate)

**Agent**: Smoke Test Agent (`15-smoke-test-agent.prompt.md`)

**Skip if**: `docs/test-results/STR-<NNN>-sprint-<N>.md` exists and shows all smoke
tests passing for the sprint just completed in Phases 5–8b.

**Execute if**: No STR document exists for the current sprint, OR the existing STR shows
a failed smoke test that has not yet been resolved.

**Work to do**:
Read `.github/prompts/15-smoke-test-agent.prompt.md` and
`.github/instructions/smoke-test-agent.instructions.md` fully, then:

1. Locate or create `tests/smoke/test_sprint_<N>_smoke.py`. The file MUST cover all
   mandatory smoke scenarios:
   - App launch without error (`at.run()` completes, `at.exception` is falsy)
   - Sidebar DB selector renders with all supported DB type options
   - MySQL static schema → SQL generation flow (OpenAI mocked to return fixed SQL)
   - Empty query input shows a validation warning, not a crash
   - Schema viewer panel is present and populated after schema load
   - Progress tracker advances through all 4 steps
   - SQL output panel displays the generated SQL string
   - One additional scenario per new DB type or UI feature added in this sprint
2. Decorate all test functions with `@pytest.mark.smoke`.
3. Ensure `pyproject.toml` has `smoke` in `markers` and `addopts` excludes smoke tests
   by default (`-m 'not integration and not smoke'`).
4. Run: `python -m pytest tests/smoke/ -v --tb=short -m smoke`
5. **On failure**:
   a. **Attempt an immediate fix** — diagnose (wrong mock, stale session state, import
      error, missing fixture) and apply the fix to the source or test file directly.
   b. Re-run once. If all tests pass → record ✅ in the STR.
   c. If still failing → create `docs/bug-reports/BUG-<NNN>-smoke-<slug>.md` with full
      traceback, the attempted fix, and status `🔲 Open`. Record ❌ in the STR and
      reference the BUG number. Phase 11 handles it in the next sprint cycle.
      **Do NOT block the retro — proceed to Phase 8d regardless.**
6. Create `docs/test-results/STR-<NNN>-sprint-<N>.md` with the full results table and a
   "Notes for Retro" section that Phase 8d MUST reference when writing the retro.
7. Update `docs/guides/developer-guide.md` if new smoke test patterns were introduced.

> **No stopping here.** After writing the STR, the pipeline MUST immediately proceed
> to Phase 8d — do NOT wait for user input.

Update `PROJECT_PROGRESS.md` with the STR outcome.

---

## PHASE 8d — Sprint Retrospective (Scrum Master)

**Agent**: Scrum Master (`01-scrum-master.prompt.md`)

**Skip if**: `docs/sprints/SPRINT-<N>-retro.md` already exists and is non-empty for the
sprint whose Phases 5–8c were just completed (where N = the sprint number whose stories
were just implemented and tested).

**Execute if**: The just-completed sprint does NOT yet have a retrospective file.

**Work to do**:
Read `.github/prompts/01-scrum-master.prompt.md` fully.  Write the retrospective for the
sprint that was just closed.  The retro MUST follow the standard format (see the Scrum
Master prompt) and MUST include ALL of the following sections:

- **Sprint Snapshot** — goal, dates, velocity (committed vs delivered pts)
- **What Went Well** — at least 3 concrete observations drawn from Phase 5–8c outcomes
  (patterns that worked, tests that passed cleanly, smoke tests green, refactors that
  went smoothly, etc.)
- **What Could Be Improved** — at least 3 honest observations (deferred stories,
  coverage gaps, smoke test failures or flakiness, technical debt, process friction)
- **Action Items** table — one row per "What Could Be Improved" item, with Owner and Due
  columns set to the NEXT sprint
- **Cumulative Velocity** table — updated with the row for the sprint just closed

**Reference the STR** — read `docs/test-results/STR-<NNN>-sprint-<N>.md` and incorporate
its "Notes for Retro" section into "What Went Well" or "What Could Be Improved" as
appropriate.

Save the file at `docs/sprints/SPRINT-<N>-retro.md`.

Update `PROJECT_PROGRESS.md`: add an activity-log entry for the Scrum Master and note
the retro file in the `Next Action` field so Phase 8e knows to process it.

> **No stopping here.** After writing the retro, the pipeline MUST immediately proceed
> to Phase 8e — do NOT wait for user input.

---

## PHASE 8e — Retro Re-entry Loop (Auto next-sprint trigger)

**Agent**: Retro Analyzer (`11-retro-analyzer.prompt.md`) → then re-runs Phases 1–8e

**Skip if**: The retro file produced by Phase 8d was already processed by Phase 0 earlier
in this same pipeline invocation, AND no new user stories or epics were created by that
processing.  (This prevents an infinite loop when Phase 0 finds nothing new.)

**Execute if**: Phase 8d just wrote a new `SPRINT-<N>-retro.md` that has NOT yet been
processed by Phase 0 in this invocation.

**Work to do**:

1. **Run Phase 0** on the new retro (same logic as the top-level Phase 0 — parse "What
   Could Be Improved" and "Action Items", create bug reports, user stories, epics, update
   the sprint plan, roadmap, and `PROJECT_PROGRESS.md`).

2. **Check what was seeded**:
   - If Phase 0 created one or more new committed user stories (i.e. a `SPRINT-<N+1>.md`
     was created or updated with new stories), the pipeline MUST re-run Phases 1–8e for
     the new sprint immediately.  The new sprint is treated exactly like the first
     sprint — run Epic Writing, User Story Writing, Architecture (if needed), Sprint
     Planning, Development, Code Review, Testing, Integration Testing, Smoke Testing
     (Phase 8c), then write the next retro in Phase 8d, and loop again.
   - If Phase 0 produced only Future Backlog items (no committed stories for the next
     sprint), record the items in `docs/roadmap.md` as normal and proceed to Phase 9.
     Do NOT loop.

3. **Loop termination condition** (safety guard): If the pipeline has already completed
   three or more successive sprint loops in this single invocation (i.e. Sprint N,
   Sprint N+1, Sprint N+2 all completed and retro'd), stop looping regardless and proceed
   to Phase 9 with a note in `PROJECT_PROGRESS.md`: "Auto-loop limit reached; remaining
   backlog items deferred to next pipeline invocation."

Update `PROJECT_PROGRESS.md` after every iteration.

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

## PHASE 11 — Bug Fix Loop

**Agent**: Bug Fix Agent (`12-bug-fix-agent.prompt.md`)

**Skip if**: The `## 🐛 Open Bug Reports` table in `PROJECT_PROGRESS.md` contains NO rows
with status `🔲 Backlog`, `🔄 In Progress`, or the sprint column matches the current sprint.

**Execute if**: Any bug in `docs/bug-reports/` has status `🔲 Open` or `🔄 In Progress`
AND is not marked `⏩ Superseded`.

**Work to do**:
Read `.github/prompts/12-bug-fix-agent.prompt.md` and
`.github/instructions/bug-fix-agent.instructions.md` fully, then for each open bug
(lowest BUG-NNN first):

1. Establish baseline test run.
2. Write a minimal reproduction test.
3. Apply fix strategies in order (root-cause B → guard A → config C → driver D → UX E).
4. Verify: regression test PASS, full suite PASS, coverage ≥ baseline, ruff 0, mypy 0,
   UI steps no longer reproduce the error.
5. If PASS: mark bug ✅ Fixed, update all docs (bug report, test case, PROJECT_PROGRESS.md,
   roadmap, guides).
6. If ALL strategies FAIL: create child bug BUG-NNN+1, update parent to ⏩ Superseded,
   restart the loop with the child bug.
7. The loop MUST continue until the bug is ✅ Fixed or explicitly escalated by the user.

**Per-fix unit test trigger (mandatory)**: After EACH bug is marked ✅ Fixed,
immediately run the Unit Test Agent for that fix BEFORE the integration test trigger:
1. Read `.github/prompts/14-unit-test-agent.prompt.md`.
2. Locate or create `tests/unit/test_<bug-slug>.py` with a regression test class
   `TestBugNNN<Description>` that must FAIL on the unfixed code and PASS after the fix.
3. Run `python -m pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing`.
4. **If unit tests fail**:
   a. Attempt an immediate fix (implementation or test).
   b. Re-run once. If still failing → create child bug `BUG-<NNN+1>-unit-regression.md`
      with status `🔲 Open` and continue. Phase 8b sweep will catch it.
5. Create `docs/test-results/UTR-<NNN>-BUG-<NNN>.md` with the outcome.
6. Update `PROJECT_PROGRESS.md`.

**Per-fix integration test trigger (mandatory)**: After the unit test trigger passes
(or a child bug is filed), immediately run integration tests for that fix:
1. Locate or create `tests/integration/test_<bug-slug>.py`.
2. Run `pytest tests/integration/ -v --tb=short -m integration` for that test file.
3. **If the integration test fails**:
   a. Attempt an immediate inline fix (fixture issue, env var, logic regression).
   b. Re-run once.  If it passes → record ✅ in the ITR and continue.
   c. If it still fails → create a NEW child bug report `BUG-<NNN+1>-integration-<slug>.md`
      with status `🔲 Open`, reference the parent fix, and continue the outer loop.
      Phase 8b will catch it in the sprint-level sweep.
4. Create `docs/test-results/ITR-<NNN>-BUG-<NNN>.md` with the outcome.
5. Update `PROJECT_PROGRESS.md` with the ITR result.

Update `PROJECT_PROGRESS.md` after every fix attempt (pass or fail).

---

## PHASE 12 — Final Verification

After completing all phases:

1. Run `python -m pytest tests/ -q --cov=src --cov-report=term-missing` in the terminal
   and confirm all tests pass with ≥ 80% coverage.
2. Confirm `docs/test-results/` contains ALL of the following for every completed sprint
   and trigger:
   - `TR-*` — sprint test results (from Phase 8) for every sprint
   - `UTR-*` — unit test results (from Phase 5b) for every User Story and Bug Fix
   - `ITR-*` — integration test results (from Phase 8b) for every User Story and Bug Fix
   - `STR-*` — smoke test results (from Phase 8c) for every sprint
   If any are missing, run the appropriate agent phase now before proceeding.
3. Verify all epic ACs are ticked in `docs/epics/*.md`.
4. **US file audit** — run `grep_search` on `docs/user-stories/**/*.md` for the pattern
   `- [ ]`. If any unchecked DoD boxes remain:
   a. Tick every box whose criterion is satisfied by the current codebase.
   b. Set the `## Status` / `**Status**:` field of every fully-checked story to `✅ Done`.
   c. If a box cannot honestly be ticked (criterion genuinely not met), file a bug report
      in `docs/bug-reports/` and note it in the summary.
5. **Bug audit** — confirm NO bug in `docs/bug-reports/` has status `🔲 Open` or
   `🔄 In Progress`. Any remaining open bugs must have either been deferred to Backlog
   (by explicit user decision) or escalated as `⏩ Superseded`.
6. **Retro audit** — for every `docs/sprints/SPRINT-*-retro.md` file that exists:
   a. Confirm a matching `Retro Analyzer | Processed SPRINT-<N>-retro.md` entry appears
      in the `PROJECT_PROGRESS.md` Agent Activity Log.
   b. If any retro is missing its processed entry, re-run Phase 0 for that retro, then
      check whether Phase 0 seeded a new sprint; if it did, re-run Phases 1–8e before
      returning to Phase 12.
   c. If the pipeline hit the auto-loop limit in Phase 8e, note the remaining unprocessed
      retros as "deferred to next invocation" — do NOT re-run them here.
7. **Sprint retro completeness** — confirm that every sprint which has a `SPRINT-<N>.md`
   plan file also has a corresponding `SPRINT-<N>-retro.md`. If a retro is missing for a
   completed sprint, write it now (same rules as Phase 8d) and re-run Phase 0 on it.
   Also confirm each sprint has an `STR-*` smoke test result — if missing, run Phase 8c.
8. Update `PROJECT_PROGRESS.md`:
   - Set all sprint velocities to actual values
   - Set all phase rows to ✅ DONE / 100%
   - Set `Current Agent` to `Pipeline Complete`
   - Set `Next Action` to `🎉 All phases complete — project ready`
9. Print a final summary table of all phases executed and their outcomes, including:
   - Which sprints were completed in this invocation
   - Which sprints had retros and smoke tests written automatically
   - How many auto-loop iterations ran (Phase 8e)
   - Total tests passed / skipped / coverage %

---

## Parallel Execution Note

Phase 0 (Retro Analysis) MUST run before all other phases. It seeds new work items that
Phases 1–12 will then process. Running Phases 1–12 before Phase 0 means retro-driven
items would be missed in the current run.

Phases 1–4 (planning/docs) can run in any order since they do not depend on code.
Phases 5–12 (implementation/QA/bugs/deploy) must run sequentially since each depends on
the previous. Phase 5b (Unit Test sweep) runs after Phase 5 and after Phase 11 (Bug Fix
Loop). Phase 8b (Integration Test sweep) runs after Phase 8 and after Phase 11. Phase 8c
(Smoke Tests) runs once per sprint after Phase 8b completes, before Phase 8d (Sprint
Retro). The pipeline enforces sequential execution by default.

## Automated Sprint Loop (Phases 8c → 8e)

```
Phase 5 ──► [per-story: unit tests + integration tests]
  │
  ▼
Phase 5b ──► Phase 6 → Phase 7 → Phase 8 → Phase 8b
                                              │
                                              ▼
                                        Phase 8c
                                   (Smoke Test Agent
                                    STR-NNN-sprint-N.md)
                                              │
                                              ▼
                                        Phase 8d  ←─────────────────────────────┐
                                   (Scrum Master writes                          │
                                    SPRINT-N-retro.md)                          │
                                              │                                  │
                                              ▼                                  │
                                        Phase 8e                                 │
                                   (Phase 0 on new retro)                        │
                                              │                                  │
                             ┌────────────────┴──────────────────┐               │
                             │ New committed                      │ Nothing new   │
                             │ stories seeded                     │ / loop limit  │
                             ▼                                    ▼               │
                   Phases 1-8e for                         Phase 9 →             │
                   Sprint N+1  ────────────────────────────────────────►         │
                             │                                                    │
                             └────────── Phase 8c + Phase 8d for Sprint N+1 ─────┘
```

The loop runs up to **3 successive sprint iterations** per invocation. If the limit is
reached, remaining backlog items are recorded in `docs/roadmap.md` and the next
`@workspace #file:.github/prompts/99-full-pipeline.prompt.md` invocation picks them up.
