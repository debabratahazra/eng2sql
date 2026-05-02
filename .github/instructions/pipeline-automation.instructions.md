---
applyTo: ".github/**"
---

# Pipeline Automation — Usage Guide

This project uses a three-tier automated SDLC pipeline. All 10 agent phases
(Epic Writing → User Stories → Architecture → Sprint Planning → Development →
Code Review → Test Cases → Testing → Deployment → DevOps) can be driven
automatically without any manual prompt-to-prompt handoffs.

---

## Tier 1 — VS Code Copilot Chat (Single Session)

Run the full pipeline in one Copilot session:

```
@workspace #file:.github/prompts/99-full-pipeline.prompt.md
```

What it does:
- Reads `PROJECT_PROGRESS.md` to determine state.
- Checks each phase's output directories; skips completed phases automatically.
- Executes every remaining phase in sequence without stopping.
- Commits no code — outputs are written by Copilot's file tools directly into
  your workspace.

When to use:
- New feature development from scratch.
- Resuming after a partial run (already-complete phases are skipped).

---

## Tier 2 — GitHub Actions (`agent-pipeline.yml`)

Trigger via the GitHub web UI or on every push to `docs/epics/EPIC-*.md`.

### Automatic trigger
Push or create any file matching `docs/epics/EPIC-*.md` on `main` or `develop`.

### Manual trigger (`workflow_dispatch`)
1. Go to **Actions → Multi-Agent SDLC Pipeline → Run workflow**.
2. Set `start_phase` (default `1`) to begin from a specific phase.
3. Set `dry_run: true` to print the plan without writing files.

Required GitHub Secrets:

| Secret | Description |
|--------|-------------|
| `OPENAI_API_KEY` | Bearer token for the LLM endpoint |
| `OPENAI_BASE_URL` | Endpoint URL (defaults to `https://gpt4ifx.icp.infineon.com`) |

Job dependency chain:
```
planning (phases 1–4)
    └─► development (phase 5)
            └─► code-review (phase 6)
                    └─► qa (phases 7–8)
                            └─► deployment (phases 9–10)
                                        └─► summary
```

Each job commits its outputs back to the branch with a `[skip ci]` tag to
prevent infinite loops.

---

## Tier 3 — Local Python Script

`scripts/run_pipeline.py` is the backend used by both Tier 2 (GitHub Actions)
and can also be run directly.

### Setup
```bash
pip install openai httpx pyyaml
export OPENAI_API_KEY="your-key"
export OPENAI_BASE_URL="https://gpt4ifx.icp.infineon.com"   # optional
```

### Commands

```bash
# Check which phases need running (read-only, no API calls)
python scripts/run_pipeline.py --check-only

# Run the full pipeline (skips completed phases automatically)
python scripts/run_pipeline.py

# Start from a specific phase
python scripts/run_pipeline.py --phase 6

# Dry-run: call the API and print what would be written, but write nothing
python scripts/run_pipeline.py --dry-run

# Start from phase 3, dry-run
python scripts/run_pipeline.py --phase 3 --dry-run
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — (required) | LLM bearer token |
| `OPENAI_BASE_URL` | `https://gpt4ifx.icp.infineon.com` | Endpoint URL |
| `OPENAI_MODEL` | `gpt-5.2` | Model name |
| `PIPELINE_MAX_TOKENS` | `8000` | Max tokens per LLM call |
| `PIPELINE_START_PHASE` | `1` | Start phase when called from CI |
| `DRY_RUN` | `false` | Set to `true` to skip file writes |
| `PYTHONPATH` | — | Set to `src` when running tests in Phase 8 |

---

## Phase Completion Detection

The script checks whether a phase's required output files already exist and are
non-empty (> 100 bytes). If they do, the phase is automatically skipped:

| Phase | Skip condition (outputs exist) |
|-------|-------------------------------|
| 1 — Epic Writing | `docs/epics/EPIC-001-*.md` … `EPIC-005-*.md` |
| 2 — User Stories | ≥1 `US-*.md` under `docs/user-stories/sprint-1/` and `sprint-2/` |
| 3 — Architecture | `system-design.md`, `ADR-001-*.md`, `api-contracts.md`, `security.md` |
| 4 — Sprint Planning | `SPRINT-1.md`, `SPRINT-2.md` under `docs/sprints/` |
| 5 — Development | Core service files + at least one test file |
| 6 — Code Review | At least one `CR-*.md` under `docs/code-reviews/` |
| 7 — Test Cases | At least one `TC-*.md` under `docs/test-cases/` |
| 8 — Testing | At least one `TR-*.md` under `docs/test-results/` |
| 9 — Deployment | `Dockerfile`, `docker-compose.yml`, `docs/deployment/runbook.md` |
| 10 — DevOps | `.pre-commit-config.yaml`, `docs/deployment/secrets-setup.md` |

---

## Output File Format

Every agent phase returns file content wrapped in XML blocks:

```
<FILE path="docs/epics/EPIC-001-core-sql-generation.md">
# EPIC-001 …
</FILE>
```

The script's `parse_file_blocks()` function extracts these and writes them to
`ROOT / path`. Outer markdown code fences are stripped automatically.

---

## CA Certificate (Corporate Proxy)

If `cert/ca-bundle.crt` exists in the repo root, the script passes it to
`ssl.create_default_context(cafile=...)` and uses the resulting `SSLContext`
object as `httpx.Client(verify=ssl_ctx)`. This satisfies the httpx ≥ 0.28
requirement (no string paths).

---

## Parallel vs Sequential Rationale

Phases 1–4 are documentation-only and could in principle run in parallel, but
the GitHub Actions workflow runs them sequentially within a single job because:
- Phase 2 depends on Phase 1 output (epic files).
- Phase 3 depends on Phase 2 output (user story files).
- Phase 4 depends on Phases 1–3.

Phases 5–10 are strictly sequential and each job uses `needs:` to enforce
ordering. Running development before architecture, or testing before code
review, would produce incorrect outputs.
