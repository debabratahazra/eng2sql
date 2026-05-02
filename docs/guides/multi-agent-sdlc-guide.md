# Multi-Agent SDLC Guide — Eng2SQL

> How to drive the entire project lifecycle using GitHub Copilot agents,
> from first epic through to production deployment.

---

## Table of Contents

1. [How the System Works](#how-the-system-works)
2. [Prerequisites](#prerequisites)
3. [Phase Overview](#phase-overview)
4. [Step-by-Step Lifecycle](#step-by-step-lifecycle)
   - [Step 0 — Check Project State (Orchestrator)](#step-0--check-project-state-orchestrator)
   - [Step 1 — Define Epics (Epic Writer)](#step-1--define-epics-epic-writer)
   - [Step 2 — Write User Stories (User Story Writer)](#step-2--write-user-stories-user-story-writer)
   - [Step 3 — Design the System (Architect)](#step-3--design-the-system-architect)
   - [Step 4 — Plan the Sprint (Scrum Master)](#step-4--plan-the-sprint-scrum-master)
   - [Step 5 — Implement Stories (Developer)](#step-5--implement-stories-developer)
   - [Step 6 — Review Code (Code Reviewer)](#step-6--review-code-code-reviewer)
   - [Step 7 — Write Test Cases (Test Case Writer)](#step-7--write-test-cases-test-case-writer)
   - [Step 8 — Run Tests (Tester)](#step-8--run-tests-tester)
   - [Step 9 — Deploy (Deployment Agent)](#step-9--deploy-deployment-agent)
   - [Step 10 — Infrastructure & Monitoring (DevOps)](#step-10--infrastructure--monitoring-devops)
5. [Per-Story Verification Loop](#per-story-verification-loop)
6. [Adding New User Stories Mid-Sprint](#adding-new-user-stories-mid-sprint)
7. [Handling Bug Reports](#handling-bug-reports)
8. [Reading the Progress Dashboard](#reading-the-progress-dashboard)
9. [Quick-Reference Command Card](#quick-reference-command-card)
10. [Troubleshooting](#troubleshooting)

---

## How the System Works

Every agent is a **GitHub Copilot Chat session** driven by a prompt file under
`.github/prompts/`. Agents do not run automatically — **you invoke each one** by typing
a command in the Copilot Chat panel. Each agent:

1. Reads `PROJECT_PROGRESS.md` to understand current project state.
2. Reads the relevant `docs/` files for context.
3. Produces output (code, docs, test cases, or reports).
4. Updates `PROJECT_PROGRESS.md` with its results.
5. Issues an explicit **handoff message** naming the next agent.

You then copy that next-agent command and paste it into Copilot Chat to continue.

```
Your role: paste the correct agent command → read its output → act on any prompts → paste next agent command
Agent role: read context → produce work → update board → tell you what comes next
```

---

## Prerequisites

Before running any agent:

- [ ] VS Code installed with **GitHub Copilot** and **GitHub Copilot Chat** extensions
- [ ] Copilot Chat panel open (`Ctrl+Shift+I` on Windows, `Cmd+Shift+I` on Mac)
- [ ] Workspace opened at the `eng2sql/` project root
- [ ] `.env` file created from `.env.example` with your `OPENAI_API_KEY` filled in
- [ ] Python 3.11+ virtual environment activated and `pip install -r requirements.txt` run
- [ ] `PROJECT_PROGRESS.md` exists at project root (already scaffolded)

> **Tip**: Keep `PROJECT_PROGRESS.md` open in a VS Code tab alongside Copilot Chat.
> After each agent session, refresh it to see the updated board.

---

## Phase Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  PLANNING PHASE                                                 │
│  Step 0 → Orchestrator decides what's next                      │
│  Step 1 → Epic Writer creates EPIC-NNN files                    │
│  Step 2 → User Story Writer creates US-NNN files per epic       │
│  Step 3 → Architect creates system design + ADRs                │
│  Step 4 → Scrum Master plans sprint, assigns stories to sprints │
├─────────────────────────────────────────────────────────────────┤
│  EXECUTION PHASE  (repeats per story)                           │
│  Step 5 → Developer implements story + updates guides           │
│  Step 6 → Code Reviewer reviews for quality + security          │
│  Step 7 → Test Case Writer writes BDD scenarios                 │
│  Step 8 → Tester runs tests, files bugs if any                  │
│  Step 5 (again) → Developer fixes bugs                          │
│  Step 8 (again) → Tester re-verifies                            │
├─────────────────────────────────────────────────────────────────┤
│  DELIVERY PHASE                                                 │
│  Step 9 → Deployment Agent builds Docker image + CI/CD          │
│  Step 10 → DevOps sets up monitoring, secrets, hooks            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Lifecycle

---

### Step 0 — Check Project State (Orchestrator)

**When to run**: At the start of every session, or whenever you are unsure what to do next.

**Command to paste into Copilot Chat:**
```
@workspace #file:.github/prompts/00-orchestrator.prompt.md
```

**What the Orchestrator does:**
- Reads `PROJECT_PROGRESS.md` and `docs/roadmap.md`
- Checks which phases are complete and which are pending
- Tells you exactly which agent to invoke next and why

**What you will see:**
```
## 🤖 Orchestrator Handoff

Current Phase: Planning — Epics defined, no user stories yet
Next Agent: User Story Writer
Reason: 5 epics exist but no US-NNN files found in docs/user-stories/

To continue, run:
@workspace #file:.github/prompts/03-user-story-writer.prompt.md
```

**Your action**: Copy the `@workspace #file:...` command from the handoff and paste it into Chat.

---

### Step 1 — Define Epics (Epic Writer)

**Run this when**: No epics exist yet, or you want to add a new capability area.

**Command:**
```
@workspace #file:.github/prompts/02-epic-writer.prompt.md
```

**What the agent produces:**
- One file per epic under `docs/epics/EPIC-NNN-slug.md`
- Each epic has: Goal, Business Value, Scope, Acceptance Criteria, estimated size

**Epics already created for Eng2SQL:**

| Epic     | File                                         | Description              |
| -------- | -------------------------------------------- | ------------------------ |
| EPIC-001 | `docs/epics/EPIC-001-core-sql-generation.md` | OpenAI SQL generation    |
| EPIC-002 | `docs/epics/EPIC-002-streamlit-ui.md`        | Streamlit user interface |
| EPIC-003 | `docs/epics/EPIC-003-dynamic-schema.md`      | Live DB schema detection |
| EPIC-004 | `docs/epics/EPIC-004-quality-assurance.md`   | Testing and code quality |
| EPIC-005 | `docs/epics/EPIC-005-deployment-devops.md`   | CI/CD and Docker         |

**After this step**: Orchestrator will route to User Story Writer.

---

### Step 2 — Write User Stories (User Story Writer)

**Run this when**: Epics exist but user stories are missing or incomplete.

**Command:**
```
@workspace #file:.github/prompts/03-user-story-writer.prompt.md
```

**What the agent produces:**
- One file per story under `docs/user-stories/<sprint>/US-NNN-slug.md`
- Each story has: user story statement, Gherkin acceptance criteria, story points, priority

**To add additional user stories for a specific epic**, say in chat:

```
@workspace #file:.github/prompts/03-user-story-writer.prompt.md

Please create additional user stories for EPIC-003 (Dynamic Schema Detection).
Focus on: error handling when DB is unreachable, schema refresh UX, and column
type display in the schema viewer.
```

**After this step**: Orchestrator will route to Architect.

---

### Step 3 — Design the System (Architect)

**Run this when**: Stories exist but no architecture documentation.

**Command:**
```
@workspace #file:.github/prompts/04-architect.prompt.md
```

**What the agent produces:**
- `docs/architecture/system-design.md` — component diagram and data flows
- `docs/architecture/adr/ADR-NNN-*.md` — Architecture Decision Records
- `docs/architecture/api-contracts.md` — service method signatures

**After this step**: Orchestrator will route to Scrum Master.

---

### Step 4 — Plan the Sprint (Scrum Master)

**Run this when**: Architecture is done and you need to start or plan the next sprint.

**Command:**
```
@workspace #file:.github/prompts/01-scrum-master.prompt.md
```

**What the agent produces:**
- `docs/sprints/SPRINT-N.md` — sprint goal, committed stories, velocity target, DoD
- Updates `PROJECT_PROGRESS.md` sprint board

**To plan a specific sprint**, say:
```
@workspace #file:.github/prompts/01-scrum-master.prompt.md

Plan Sprint 2. Stories available: US-008, US-009, US-010, US-011, US-012.
Target velocity: 21 points. Sprint duration: 2026-05-15 to 2026-05-28.
```

**After this step**: Orchestrator will route to Developer.

---

### Step 5 — Implement Stories (Developer)

**Run this when**: Sprint is planned and stories are ready for implementation.

**Command:**
```
@workspace #file:.github/prompts/05-developer.prompt.md
```

**What the agent produces:**
- Source code in `src/` (services, components, models, utils)
- Unit tests in `tests/unit/`
- Updates `docs/guides/user-guide.md` (for user-facing changes)
- Updates `docs/guides/developer-guide.md` (for API/service changes)
- Updates `README.md` (if setup or env vars changed)
- Updates `PROJECT_PROGRESS.md` story statuses

**To implement a specific story**, say:
```
@workspace #file:.github/prompts/05-developer.prompt.md

Implement US-008: Database Connection Form.
Read: #file:docs/user-stories/sprint-2/US-008-db-connection-form.md
```

**To implement all stories in the current sprint**, say:
```
@workspace #file:.github/prompts/05-developer.prompt.md

Implement all NOT_STARTED stories in Sprint 1.
Work through them one at a time: US-001 → US-002 → US-003 → US-004 → US-005 → US-006 → US-007.
After each story, verify tests pass before moving to the next.
```

**After implementing each story**, the Developer agent will:
1. Run `pytest tests/unit/ -v` to confirm tests pass
2. Update the story file status to ✅ DONE
3. Update the sprint board in `PROJECT_PROGRESS.md`

**After this step**: Orchestrator will route to Code Reviewer.

---

### Step 6 — Review Code (Code Reviewer)

**Run this when**: Developer has implemented one or more stories.

**Command:**
```
@workspace #file:.github/prompts/06-code-reviewer.prompt.md
```

**What the agent produces:**
- Code review comments in `docs/code-reviews/CR-NNN.md`
- List of blocking issues (must fix) and suggestions (optional)
- Overall APPROVED / NEEDS CHANGES verdict

**To review a specific file or story**, say:
```
@workspace #file:.github/prompts/06-code-reviewer.prompt.md

Review the implementation of US-002 (SQL Generator service).
Files to review:
- #file:src/services/sql_generator.py
- #file:tests/unit/test_sql_generator.py
```

**After this step**:
- If **APPROVED** → Orchestrator routes to Test Case Writer
- If **NEEDS CHANGES** → Developer must fix issues, then re-review

---

### Step 7 — Write Test Cases (Test Case Writer)

**Run this when**: Code is reviewed and approved. Run once per sprint or per story batch.

**Command:**
```
@workspace #file:.github/prompts/07-test-case-writer.prompt.md
```

**What the agent produces:**
- BDD test scenario files in `docs/test-cases/TC-NNN-*.md`
- pytest stub files in `tests/` matching the scenarios

**To write test cases for a specific story**, say:
```
@workspace #file:.github/prompts/07-test-case-writer.prompt.md

Write BDD test cases for US-009 (Schema Auto-Detection).
Read: #file:docs/user-stories/sprint-2/US-009-schema-auto-detection.md
```

**After this step**: Orchestrator will route to Tester.

---

### Step 8 — Run Tests & Verify (Tester)

**Run this when**: Test cases are written and you want to verify the implementation.

**Command:**
```
@workspace #file:.github/prompts/08-tester.prompt.md
```

**What the agent produces:**
- Runs the full test suite: `pytest tests/ -v --cov=src`
- Test result file at `docs/test-results/TR-NNN.md`
- If tests fail: bug report at `docs/bug-reports/BUG-NNN.md`

**After this step**:
- All tests pass → Orchestrator routes to Deployment Agent
- Bugs found → Orchestrator routes back to Developer for fixes

**To verify a specific story**, say:
```
@workspace #file:.github/prompts/08-tester.prompt.md

Run tests for US-001 and US-002 implementations only.
Verify acceptance criteria from:
- #file:docs/user-stories/sprint-1/US-001-static-schema-config.md
- #file:docs/user-stories/sprint-1/US-002-openai-sql-generation.md
```

---

### Step 9 — Deploy (Deployment Agent)

**Run this when**: All sprint stories are tested and passing.

**Command:**
```
@workspace #file:.github/prompts/09-deployment-agent.prompt.md
```

**What the agent produces:**
- `Dockerfile` and `docker-compose.yml`
- `.github/workflows/ci-cd.yml` (GitHub Actions pipeline)
- `docs/deployment/RELEASE-<version>.md` — release notes
- `docs/deployment/runbook.md` — operational runbook
- Updates `docs/guides/user-guide.md` with latest deployment steps

**To create a specific release**, say:
```
@workspace #file:.github/prompts/09-deployment-agent.prompt.md

Create release v1.0.0 release notes. Stories completed: US-001 through US-007.
```

---

### Step 10 — Infrastructure & Monitoring (DevOps)

**Run this when**: Deployment config is done and you need production hardening.

**Command:**
```
@workspace #file:.github/prompts/10-devops.prompt.md
```

**What the agent produces:**
- `.env.example` with all required variables documented
- `.pre-commit-config.yaml` — git hooks for lint + type check
- `docs/deployment/monitoring.md` — alerting and observability setup
- Secrets management guidance

---

## Per-Story Verification Loop

For each user story, follow this exact loop. This ensures **every story is verified
end-to-end** before moving on.

```
┌──────────────────────────────────────────────────────────────┐
│  STORY LOOP (repeat for each US-NNN in the sprint)           │
│                                                              │
│  1. Developer implements the story                           │
│     Command: @workspace #file:.github/prompts/05-developer.prompt.md  │
│                                                              │
│  2. Run unit tests manually to spot-check                    │
│     Terminal: pytest tests/unit/ -v -k "test_<feature>"      │
│                                                              │
│  3. Code Reviewer reviews the specific story's code          │
│     Command: @workspace #file:.github/prompts/06-code-reviewer.prompt.md │
│                                                              │
│  4. Fix any blocking review issues (Developer)               │
│     Command: @workspace #file:.github/prompts/05-developer.prompt.md  │
│                                                              │
│  5. Test Case Writer writes BDD scenarios for the story      │
│     Command: @workspace #file:.github/prompts/07-test-case-writer.prompt.md │
│                                                              │
│  6. Tester runs full suite + verifies acceptance criteria    │
│     Command: @workspace #file:.github/prompts/08-tester.prompt.md     │
│                                                              │
│  7. If bugs → Developer fixes → Tester re-runs (back to 4)  │
│                                                              │
│  8. Mark story ✅ DONE, update PROJECT_PROGRESS.md           │
│     Then: start next story from step 1                       │
└──────────────────────────────────────────────────────────────┘
```

### Manually Verify the Running App After Each Story

After each story is implemented, run the app and manually confirm the behaviour:

```bash
# Activate venv, then:
streamlit run src/app.py
```

Open http://localhost:8501 and check:

| Story  | What to verify manually                            |
| ------ | -------------------------------------------------- |
| US-001 | Schema config loads; table list appears in sidebar |
| US-002 | Type a question → SQL is generated                 |
| US-003 | Schema is injected in the prompt (check logs)      |
| US-004 | Streamlit app loads with no errors                 |
| US-005 | Text input and Generate button work                |
| US-006 | Progress steps show during generation              |
| US-007 | SQL output panel shows syntax-highlighted result   |
| US-008 | DB connection form appears in Live mode            |
| US-009 | Schema is auto-detected after connecting           |

---

## Adding New User Stories Mid-Sprint

If you identify a gap during implementation, create additional user stories without
restarting the full lifecycle:

**Step 1 — Create the story file:**
```
@workspace #file:.github/prompts/03-user-story-writer.prompt.md

Create a new user story for the following gap identified during Sprint 1:

Gap: When the OpenAI API returns a timeout error, the app shows a raw Python
traceback instead of a user-friendly message.

Please write US-XXX with Gherkin acceptance criteria and assign it to the
current sprint.
```

**Step 2 — Update the sprint board:**
```
@workspace #file:.github/prompts/01-scrum-master.prompt.md

Add the new story US-XXX to Sprint 1. Update PROJECT_PROGRESS.md sprint board
and adjust velocity accordingly.
```

**Step 3 — Implement immediately:**
```
@workspace #file:.github/prompts/05-developer.prompt.md

Implement US-XXX (friendly error handling for OpenAI timeout).
Read: #file:docs/user-stories/sprint-1/US-XXX-openai-timeout-error.md
```

---

## Handling Bug Reports

When the Tester files a bug report, the flow is:

```
Bug filed at docs/bug-reports/BUG-NNN.md
        ↓
@workspace #file:.github/prompts/05-developer.prompt.md

Fix BUG-NNN:
Read: #file:docs/bug-reports/BUG-NNN-description.md
        ↓
Developer fixes the bug, writes regression test
        ↓
@workspace #file:.github/prompts/08-tester.prompt.md

Re-run tests to verify BUG-NNN is resolved.
Read: #file:docs/bug-reports/BUG-NNN-description.md
        ↓
Tester closes the bug → story resumes
```

---

## Reading the Progress Dashboard

Open `PROJECT_PROGRESS.md` at any time to see:

| Section                    | What it shows                               |
| -------------------------- | ------------------------------------------- |
| **Overall Project Status** | Phase-level progress bars                   |
| **Agent Activity Log**     | History of every agent action taken         |
| **Sprint N Board**         | Story-by-story status for the active sprint |
| **Test Coverage Table**    | Per-module coverage numbers                 |
| **Bug Tracker**            | Open / closed bugs                          |

**Status symbols used throughout:**

| Symbol | Meaning     |
| ------ | ----------- |
| 🔲      | NOT_STARTED |
| 🔄      | IN_PROGRESS |
| ✅      | DONE        |
| 🚫      | BLOCKED     |
| ❌      | FAILED      |

---

## Quick-Reference Command Card

Copy and paste these exact commands into Copilot Chat (`Ctrl+Shift+I`):

```
─────────────────────────────────────────────────────────────────
ALWAYS START HERE (check what's next):
@workspace #file:.github/prompts/00-orchestrator.prompt.md
─────────────────────────────────────────────────────────────────

PLANNING PHASE:
  Epics:        @workspace #file:.github/prompts/02-epic-writer.prompt.md
  User Stories: @workspace #file:.github/prompts/03-user-story-writer.prompt.md
  Architecture: @workspace #file:.github/prompts/04-architect.prompt.md
  Sprint Plan:  @workspace #file:.github/prompts/01-scrum-master.prompt.md

EXECUTION PHASE:
  Implement:    @workspace #file:.github/prompts/05-developer.prompt.md
  Review Code:  @workspace #file:.github/prompts/06-code-reviewer.prompt.md
  Test Cases:   @workspace #file:.github/prompts/07-test-case-writer.prompt.md
  Run Tests:    @workspace #file:.github/prompts/08-tester.prompt.md

DELIVERY PHASE:
  Deploy:       @workspace #file:.github/prompts/09-deployment-agent.prompt.md
  DevOps:       @workspace #file:.github/prompts/10-devops.prompt.md
─────────────────────────────────────────────────────────────────
```

### Adding Context to Any Command

You can append file references to any agent command to give it focused context:

```
@workspace #file:.github/prompts/05-developer.prompt.md

Only implement US-005 right now.
Context:
- #file:docs/user-stories/sprint-1/US-005-query-input-component.md
- #file:src/components/query_input.py
- #file:tests/unit/
```

---

## Troubleshooting

### Agent produces no output or stops mid-way

- Copilot Chat has a context window limit. If the response is cut off:
  1. Click **Continue** if the button appears
  2. Or type: `Please continue from where you left off`
- For very large sprints, implement one story at a time instead of all stories together

### Agent makes changes you didn't want

- Use `Ctrl+Z` in VS Code to undo file edits
- Or use **Source Control** (Ctrl+Shift+G) to discard specific file changes
- Then re-invoke the agent with more specific instructions

### Tests fail after agent implementation

```bash
# Run with verbose output to see what failed
pytest tests/ -v --tb=short

# Run only failing tests
pytest tests/ -v --lf

# Check coverage to find untested code
pytest tests/ --cov=src --cov-report=html
# then open htmlcov/index.html
```

Then invoke the Developer agent with the specific error:
```
@workspace #file:.github/prompts/05-developer.prompt.md

The following tests are failing. Please fix:

<paste the pytest failure output here>
```

### Agent edits the wrong file

Each agent has a defined "Writes To" scope in `.github/instructions/agent-protocol.instructions.md`.
If an agent edits outside its scope, discard those changes and re-invoke with more specific instructions.

### PROJECT_PROGRESS.md is out of date

Any agent can update it. If it's stale, invoke the Orchestrator:
```
@workspace #file:.github/prompts/00-orchestrator.prompt.md

PROJECT_PROGRESS.md may be out of date. Please read the actual files in
docs/user-stories/ and src/ to determine the real current state, then
update the board and tell me what to do next.
```

### Copilot Chat doesn't find a file reference

- Ensure the file path uses forward slashes: `#file:docs/guides/user-guide.md`
- Ensure the workspace root is `eng2sql/` (not a parent folder)
- Check the file actually exists: `Test-Path docs/user-stories/sprint-1/US-001-*.md`

---

## Next Steps After This Guide

Once you have read this guide, start with:

```
@workspace #file:.github/prompts/00-orchestrator.prompt.md
```

The Orchestrator will read `PROJECT_PROGRESS.md`, determine where the project currently
stands, and tell you the exact command to run next.

For additional reference:
- [User Guide](user-guide.md) — end-user documentation
- [Developer Guide](developer-guide.md) — technical setup and API reference
- [System Design](../architecture/system-design.md) — architecture diagrams
- [Roadmap](../roadmap.md) — sprint timeline and milestones
- [PROJECT_PROGRESS.md](../../PROJECT_PROGRESS.md) — live project dashboard
