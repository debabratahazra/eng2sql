---
applyTo: "src/**/*.py"
---

# Developer Instructions — Eng2SQL

## Language & Typing
- Python 3.11+ only. First line of every module: `from __future__ import annotations`
- Full type hints on every function, method, and class variable
- Use `typing.TYPE_CHECKING` guard for import-only-for-type-hints

## Style
- PEP 8 enforced by `ruff`. Max line length: 100 characters
- Google-style docstrings on every public function, class, and module
- Single quotes for strings; double quotes allowed only for f-strings with inner quotes
- Imports ordered: stdlib → third-party → local (ruff handles this)

## Error Handling
- Raise specific custom exceptions (defined in `src/utils/exceptions.py`)
- Never swallow exceptions with bare `except:` — always `except SpecificError as e`
- Log the error with context before re-raising at service boundaries
- Use `finally` blocks to close DB connections and file handles

## Security
- NEVER hardcode secrets, API keys, or passwords
- Always use `os.getenv("VAR_NAME")` or load from `.env` via `python-dotenv`
- SQL execution: always use SQLAlchemy `text()` with bound parameters
- Log sanitisation: never log request bodies, passwords, or API keys

## Testing
- Every new function must have at least one unit test
- Tests live in `tests/unit/` (unit) or `tests/integration/` (integration)
- Use `pytest.mark.parametrize` for data-driven tests
- Mock OpenAI and DB calls in unit tests — never call real APIs in unit tests

## Patterns
- Services are stateless classes with dependency injection
- Configuration passed as dataclass instances, not dict literals
- Return `None` only when a value is genuinely optional; use `Optional[T]` type hint
