# Multi-Agent Development System — Eng2SQL

## Project Overview

**Eng2SQL** is an English-to-SQL code generation system that uses OpenAI LLM models to
translate plain-English queries into valid SQL. A Streamlit UI drives the experience with
step-by-step progress feedback, static MySQL schema support, and advanced auto-detection
of database structure from user-supplied configuration.

---

## Multi-Agent Architecture

This workspace runs a structured **multi-agent SDLC system**. Every agent has a dedicated
prompt file under `.github/prompts/`. Agents communicate by reading and writing structured
Markdown files under `docs/` and by updating the central `PROJECT_PROGRESS.md` board.

### Agent Registry

| # | Agent | Prompt File | Responsibility |
|---|-------|-------------|----------------|
| 0 | **Orchestrator** | `.github/prompts/00-orchestrator.prompt.md` | Reads progress, picks next agent, issues handoff |
| 1 | **Scrum Master** | `.github/prompts/01-scrum-master.prompt.md` | Sprint planning, velocity, blocker removal |
| 2 | **Epic Writer** | `.github/prompts/02-epic-writer.prompt.md` | Defines epics, goals, and acceptance outcomes |
| 3 | **User Story Writer** | `.github/prompts/03-user-story-writer.prompt.md` | Writes INVEST-compliant user stories |
| 4 | **Architect** | `.github/prompts/04-architect.prompt.md` | System design, ADRs, component diagrams |
| 5 | **Developer** | `.github/prompts/05-developer.prompt.md` | Implements features from user stories |
| 6 | **Code Reviewer** | `.github/prompts/06-code-reviewer.prompt.md` | Reviews PRs for quality, security, style |
| 7 | **Test Case Writer** | `.github/prompts/07-test-case-writer.prompt.md` | Writes BDD test scenarios |
| 8 | **Tester** | `.github/prompts/08-tester.prompt.md` | Executes tests, files bug reports |
| 9 | **Deployment Agent** | `.github/prompts/09-deployment-agent.prompt.md` | CI/CD, Docker, release notes |
| 10 | **DevOps** | `.github/prompts/10-devops.prompt.md` | Infra-as-code, monitoring, secrets |

### Agent Communication Protocol

```
PROJECT_PROGRESS.md      ←→  All agents (read/write)
docs/epics/              ←   Epic Writer output
docs/user-stories/       ←   User Story Writer output   →  Developer input
docs/architecture/       ←   Architect output            →  Developer input
docs/test-cases/         ←   Test Case Writer output     →  Tester input
docs/bug-reports/        ←   Tester output               →  Developer input
docs/deployment/         ←   Deployment Agent output
docs/guides/user-guide.md     ←→  Developer (updated every story completion)
docs/guides/developer-guide.md ←→  Developer (updated every story completion)
README.md                ←→  Developer / Deployment Agent (updated on feature completion)
```

**Rules every agent MUST follow:**
1. Read `PROJECT_PROGRESS.md` at the start of every session.
2. Write outputs to the correct `docs/` subdirectory.
3. Update `PROJECT_PROGRESS.md` (status + next-agent field) before finishing.
4. Never skip the handoff — always name the next agent explicitly.
5. **Documentation rule** — on every user story completion the Developer agent MUST:
   - Update `docs/guides/user-guide.md` for any user-facing change
   - Update `docs/guides/developer-guide.md` for any API / service / pattern change
   - Update `README.md` if setup steps, env vars, or usage instructions change

### How to Start / Continue Work

Open GitHub Copilot Chat (`Ctrl+Shift+I`) and type:

```
@workspace #file:.github/prompts/00-orchestrator.prompt.md
```

The Orchestrator will read `PROJECT_PROGRESS.md`, determine the current state, and tell
you which agent prompt to invoke next.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit 1.35+ |
| Language | Python 3.11+ |
| LLM | OpenAI GPT-4o (via `openai` SDK) |
| Database | MySQL 8.0 (via SQLAlchemy + PyMySQL) |
| Schema detection | SQLAlchemy `inspect()` |
| Config | YAML (`config/database_config.yaml`) |
| Testing | pytest + pytest-cov |
| Linting | ruff + mypy |
| CI/CD | GitHub Actions |
| Containers | Docker + Docker Compose |

---

## Code Standards

- **Python 3.11+** with full type hints (`from __future__ import annotations`)
- **PEP 8** enforced by `ruff`
- **Docstrings** on every public function, class, and module
- **Minimum 80 % test coverage** (`pytest --cov`)
- **No secrets in code** — use `.env` / environment variables only
- **SQL injection prevention** — always use parameterised queries
- **Error handling** at service boundaries; never swallow exceptions silently

---

## Project Directory Layout

```
eng2sql/
├── .github/
│   ├── copilot-instructions.md       ← YOU ARE HERE
│   ├── prompts/                      ← Agent prompt files
│   ├── instructions/                 ← Role-scoped instruction files
│   └── workflows/
│       └── ci-cd.yml
├── src/
│   ├── app.py                        ← Streamlit entry point
│   ├── components/                   ← UI components
│   ├── services/                     ← Business logic
│   ├── models/                       ← Data models / config
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
│   ├── roadmap.md
│   ├── guides/
│   │   ├── user-guide.md         ← End-user documentation (updated per story)
│   │   └── developer-guide.md    ← Developer documentation (updated per story)
│   ├── architecture/
│   ├── epics/
│   ├── user-stories/
│   ├── test-cases/
│   ├── bug-reports/
│   └── deployment/
├── config/
│   └── database_config.yaml
├── PROJECT_PROGRESS.md               ← Central progress board
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```
