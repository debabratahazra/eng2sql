---
applyTo: "docs/**/*.md"
---

# Agent Communication Protocol

## Core Rules (All Agents Must Follow)

1. **Read before writing** — always read `PROJECT_PROGRESS.md` before doing any work
2. **Produce output files** — write results to the correct `docs/` subdirectory
3. **Update the board** — update `PROJECT_PROGRESS.md` before ending your session
4. **Name the next agent** — every session ends with an explicit handoff
5. **Documentation rule** — on every user story completion the Developer agent MUST:
   - Update `docs/guides/user-guide.md` for any user-facing change
   - Update `docs/guides/developer-guide.md` for any API / service / pattern change
   - Update `README.md` if setup steps, env vars, or usage instructions change

## File Ownership

| Agent | Reads From | Writes To |
|-------|-----------|-----------|
| Orchestrator | `PROJECT_PROGRESS.md` | `PROJECT_PROGRESS.md` |
| Scrum Master | `docs/epics/`, `docs/user-stories/` | `docs/sprints/` |
| Epic Writer | `docs/roadmap.md` | `docs/epics/` |
| User Story Writer | `docs/epics/` | `docs/user-stories/` |
| Architect | `docs/user-stories/` | `docs/architecture/` |
| Developer | `docs/user-stories/`, `docs/architecture/`, `docs/bug-reports/` | `src/`, `tests/`, **`docs/guides/`** |
| Code Reviewer | `src/` | `docs/code-reviews/` |
| Test Case Writer | `docs/user-stories/` | `docs/test-cases/`, `tests/` |
| Tester | `docs/test-cases/`, `tests/` | `docs/test-results/`, `docs/bug-reports/` |
| Deployment Agent | `src/`, `requirements.txt` | `Dockerfile`, `docker-compose.yml`, `docs/deployment/`, **`docs/guides/`** |
| DevOps | `Dockerfile`, `docker-compose.yml` | `.env.example`, `.pre-commit-config.yaml`, `docs/deployment/` |

## Status Values for PROJECT_PROGRESS.md

Use exactly these strings:
- `NOT_STARTED` — work not yet begun
- `IN_PROGRESS` — currently being worked on
- `DONE` — complete and verified
- `BLOCKED` — waiting on a dependency

## Handoff Message Format

Every agent session MUST end with:

```markdown
## 🤖 <Agent Name> Handoff
**Completed**: <what was done>
**Next Agent**: <agent name>
**To continue**: @workspace #file:.github/prompts/<NN-agent>.prompt.md
```

## Story Status Symbols

Use these in `PROJECT_PROGRESS.md` and story files:
- 🔲 `NOT_STARTED`
- 🔄 `IN_PROGRESS`
- ✅ `DONE`
- 🚫 `BLOCKED`
- ❌ `FAILED`
