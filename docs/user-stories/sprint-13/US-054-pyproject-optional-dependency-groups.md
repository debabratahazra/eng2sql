# US-054 — `pyproject.toml` optional-dependency groups

**Sprint**: Sprint 13 (carried from Sprint 11 + Sprint 12)
**Source**: SPRINT-10-retro.md "What Could Be Improved" §5 → SPRINT-11-retro.md Action Item → SPRINT-12-retro.md Action Item
**Points**: 1
**Owner**: DevOps

## User Story

As a **developer running `pip install -e .[dev]`**, I want all dev/test/db-engine
dependencies declared in `pyproject.toml` `[project.optional-dependencies]` so that the
canonical installation path produces the same dependency tree as `requirements.txt`,
removing the current drift where new deps land in `requirements.txt` only.

## Acceptance Criteria

1. `pyproject.toml` gains:
   ```toml
   [project.optional-dependencies]
   db = ["psycopg[binary]>=3.2,<4", "pymysql>=1.1,<2", "pymongo>=4.6,<5"]
   dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.5", "mypy>=1.10",
          "testcontainers[mysql,postgres]>=4.7"]
   ```
2. Core deps stay in `[project.dependencies]`; nothing duplicated across groups.
3. `requirements.txt` regenerated from `pip-compile` (or manually verified) and
   committed; line-by-line diff documented.
4. README "Setup" section updated with `pip install -e ".[dev]"` as the recommended
   install command.

## Definition of Done

- [x] `pyproject.toml` optional groups added
- [x] `requirements.txt` updated and verified
- [x] README install command updated
- [x] Code review approved (CR-013)

## Status

✅ Done
