# ADR-006 — pyproject.toml Optional-Dependency Groups

**Date**: 2026-05-07
**Status**: Accepted
**Deciders**: DevOps, Developer

---

## Context

`requirements.txt` is the canonical dependency source for this project. As new database
drivers (`psycopg`, `pymongo`) and test infrastructure (`testcontainers`) were added in
Sprints 9–11, they were appended directly to `requirements.txt` with inline comments.

This led to a single monolithic file that mixes runtime, optional-driver, and
dev/test concerns. New contributors must install everything (including
`testcontainers`, `ruff`, `mypy`) just to run the app.

`pyproject.toml` already governs tool configuration (ruff, mypy, pytest, coverage).
Adding `[project.optional-dependencies]` groups there makes the split explicit and
enables `pip install -e ".[dev]"` as a reproducible dev install command.

---

## Decision

Add a minimal `[project]` section to `pyproject.toml` declaring:

```toml
[project]
name = "eng2sql"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    # core runtime — always installed
    "streamlit>=1.35.0",
    "openai>=1.30.0",
    "httpx>=0.27.0",
    "sqlalchemy>=2.0.0",
    "pandas>=2.2.0",
    "pyyaml>=6.0.1",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
db = [
    "pymysql>=1.1.0",
    "psycopg[binary]>=3.2,<4",
    "pymongo>=4.7",
]
dev = [
    "pytest>=8.2.0",
    "pytest-cov>=5.0.0",
    "pytest-mock>=3.14.0",
    "testcontainers[mysql]>=4.7.0",
    "testcontainers[postgres]>=4.7.0",
    "ruff>=0.4.4",
    "mypy>=1.9.0",
    "types-PyYAML>=6.0.0",
    "types-requests>=2.32.0",
]
all = ["eng2sql[db,dev]"]
```

`requirements.txt` is kept as a flat pin file for Docker and CI compatibility.
It continues to list all deps (core + db + dev) so existing `pip install -r requirements.txt`
workflows are unaffected.

---

## Consequences

**Good**:
- `pip install -e ".[dev]"` installs all dev + db deps from a single command.
- `pip install -e "."` installs only core runtime — no test/DB-driver overhead.
- `pip install -e ".[db]"` installs only the database drivers — useful for minimal deploys.
- No breakage of `requirements.txt`-based CI or Docker workflows.
- The `[all]` extra simplifies full-stack local setups.

**Bad / Trade-offs**:
- There is now mild duplication between `pyproject.toml` optional-deps and `requirements.txt`.
  This is acceptable: `requirements.txt` remains the flat-pinned lock file; `pyproject.toml`
  declares version ranges. If a dep is added in future, both files must be updated.
- The `[project]` section introduces a `name` / `version` field that must be kept
  in sync with Docker/GitHub releases. Currently the project version is managed manually.
