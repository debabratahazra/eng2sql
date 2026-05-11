---
applyTo: "docs/bug-reports/**/*.md"
---

# Bug Fix Agent — Rules and Protocol

## Core Mandate

The Bug Fix Agent is a **self-healing loop**. It reads a BUG-xxx report, devises a fix
strategy, implements the fix, verifies it end-to-end, and — if the bug is still
reproducible after the fix — automatically files a new BUG-xxx and begins another fix
cycle. The loop continues until both the **UI** and **backend** sides are verified clean.

---

## Bug Report Schema

Every bug report MUST contain these sections (checked before work begins):

| Section | Required | Purpose |
|---------|----------|---------|
| `## Description` | ✅ | Plain-English description of the failure |
| `## Steps to Reproduce` | ✅ | Numbered steps; final two lines MUST be **Expected** and **Actual** |
| `## Root Cause Analysis` | ✅ | At least one confirmed or hypothesised cause |
| `## Proposed Fix` | ✅ | One or more numbered Fix Strategies |
| `## Fix Attempts` | auto-appended | Log of every attempt; never delete old entries |
| `## Verification Record` | auto-appended | Pass/Fail status + pytest output for each attempt |
| `## Status` | ✅ | One of: `🔲 Open`, `🔄 In Progress`, `✅ Fixed`, `❌ Cannot Reproduce`, `⏩ Superseded by BUG-NNN` |

---

## Fix Strategy Classification

Before touching any code, classify the available fix strategies:

| Strategy Type | Apply When |
|---------------|-----------|
| **A — Defensive Guard** | Add a pre-condition check that catches the bad state early and raises a clear error or applies a safe default |
| **B — Root-Cause Code Fix** | Change the logic that produces the wrong output (the canonical correct fix) |
| **C — Configuration Change** | The bug is caused by a wrong default, missing env var, or wrong driver flag |
| **D — Dependency / Driver Fix** | Upgrade a library, change a driver option, or switch to a compatible API |
| **E — Documentation / UX Fix** | The code is correct but the user has no actionable guidance; add a hint or warning in the UI |
| **F — Test-only Fix** | The code is correct but tests were wrong; fix the test, not the code |

Always attempt the **most impactful root-cause strategy first** (prefer B over A over E).
If a strategy is attempted and does not resolve the bug, move to the next strategy.

---

## The Fix Loop — Step by Step

### Step 1 — Read and Understand

1. Read the full bug report: `docs/bug-reports/BUG-NNN-*.md`
2. Read all `## Linked Source` files end-to-end (never assume you know the code).
3. Read the corresponding user story acceptance criteria (if `## Linked Story` is set).
4. Run the existing test suite to establish baseline: `pytest tests/ -v --tb=short`
5. Record baseline: number of tests, coverage %, and which tests are currently failing.

### Step 2 — Reproduce Locally

Reproduce the exact failure before writing any fix. This confirms the bug is real and
establishes the "before" state.

- For backend bugs: write a **minimal reproduction test** in `tests/unit/` that
  fails with the current code. Name it `test_BUG_NNN_<slug>_repro.py` (temporary).
- For UI bugs: describe the exact `AppTest` or manual Streamlit steps that trigger
  the error and record the exact error message.
- If the bug CANNOT be reproduced, set status to `❌ Cannot Reproduce`, update
  `PROJECT_PROGRESS.md`, and stop.

### Step 3 — Devise Fix Strategies

Write at least **two** independent fix strategies into the `## Proposed Fix` section if
the report only has one. Each strategy must specify:
- **What changes**: exact file(s) and function(s)
- **Why it should work**: the causal chain from root cause to fix
- **Risk**: side-effects or regressions to watch for

### Step 4 — Implement Fix (Strategy 1)

Apply the first fix strategy:

1. Edit only the files listed in the strategy — do not touch unrelated code.
2. Apply the fix conservatively (minimal diff, no refactoring).
3. Remove the temporary repro test `test_BUG_NNN_<slug>_repro.py`.
4. Write a permanent **regression test** that would have caught this bug:
   - File: `tests/unit/test_<module>.py` (add to existing test class)
   - Name: `test_bug_NNN_<descriptive_slug>`
   - Must FAIL before the fix and PASS after the fix.
5. Write a **BDD test case** in `docs/test-cases/TC-<NNN>-bug-NNN-fix.md`.

### Step 5 — Verify Fix

Run the full verification suite in this order:

```bash
# 1. Unit tests
pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing

# 2. Integration tests
pytest tests/integration/ -v --tb=short

# 3. Linting
ruff check src/ tests/

# 4. Type checking
mypy src/

# 5. AppTest UI smoke test (if bug was UI-visible)
pytest tests/unit/test_sidebar_ui.py -v --tb=short
```

Record all output verbatim in the `## Verification Record` section of the bug report.

**Pass criteria** (ALL must be true):

| Check | Criterion |
|-------|-----------|
| Regression test | PASS |
| Full test suite | No new failures |
| Coverage | ≥ current baseline (never regress coverage) |
| ruff | 0 errors |
| mypy | 0 new errors |
| UI reproduction steps | No longer reproduce the error |

### Step 6 — If PASS → Mark Fixed

1. Update `docs/bug-reports/BUG-NNN-*.md`:
   - Append to `## Fix Attempts`: attempt number, strategy used, commit of fix
   - Append to `## Verification Record`: full pytest summary, coverage %, PASS
   - Set `**Status**` to `✅ Fixed`
2. Update `docs/test-cases/TC-<NNN>-bug-NNN-fix.md` — tick all DoD boxes.
3. Update `PROJECT_PROGRESS.md`:
   - Change bug status from `🔲 Open` / `🔄 In Progress` to `✅ Fixed`
   - Add activity log entry
4. Update `docs/roadmap.md` if the bug was blocking a sprint or epic.
5. Update `docs/guides/developer-guide.md` if the fix introduces a new pattern.
6. Update `docs/guides/user-guide.md` if the fix changes user-visible error messages.

### Step 7 — If FAIL → Create New Bug and Loop

If the verification fails (bug still reproducible or new failures introduced):

1. **Revert** the failed fix (restore the files to pre-fix state).
2. Append a FAIL entry to `## Fix Attempts` and `## Verification Record` in the
   current bug report. Include: strategy tried, why it failed, error output.
3. If the original bug is still open, try the **next fix strategy** (return to Step 4).
4. If ALL proposed strategies have been tried and failed, create a new bug report:

```markdown
# BUG-<NNN+1>: <Same title> — Strategy Exhausted, Root Cause Unresolved

**Severity**: <same as or higher than parent>
**Status**: 🔲 Open
**Parent Bug**: BUG-<NNN>
**Sprint**: Backlog

## Description
All fix strategies defined in BUG-<NNN> were attempted and failed.
This report starts a new investigation cycle with the following evidence gathered:
...
```

5. Update the parent bug `**Status**` to `⏩ Superseded by BUG-<NNN+1>`.
6. Begin the loop again from Step 1 with the new bug report as the active target.

---

## Documentation Obligations

After any successful fix:

| File | What to update |
|------|---------------|
| `docs/bug-reports/BUG-NNN-*.md` | Fix Attempts + Verification Record + Status ✅ |
| `docs/test-cases/TC-NNN-bug-NNN-fix.md` | Created or updated — all DoD boxes ticked |
| `docs/guides/developer-guide.md` | New pattern / root cause note if non-obvious |
| `docs/guides/user-guide.md` | Updated error message guidance if UI-visible |
| `PROJECT_PROGRESS.md` | Bug status, activity log entry |
| `docs/roadmap.md` | Remove from Backlog if carried there |

---

## Security Rules (MUST NOT Violate)

- Never log plaintext passwords, tokens, or connection strings in regression tests.
- Never hardcode test credentials — use `pytest` fixtures or `os.getenv()`.
- All new test assertions that check error messages must verify credentials are masked.
- SQL assertions must use parameterised queries — never f-string injection.

---

## File Naming

| Artifact | Path template |
|----------|--------------|
| Regression test (in existing file) | `tests/unit/test_<module>.py::test_bug_NNN_<slug>` |
| BDD test case | `docs/test-cases/TC-NNN-bug-NNN-<slug>.md` |
| New child bug (if loop continues) | `docs/bug-reports/BUG-NNN-<slug>-attempt-N.md` |

---

## Activity Log Entry Format

Add one row to `PROJECT_PROGRESS.md` Agent Activity Log per fix attempt:

```
| <#> | Bug Fix Agent | <PASS/FAIL> fix attempt <N> for BUG-<NNN> using strategy <X> | `<files changed>` | <date> |
```
