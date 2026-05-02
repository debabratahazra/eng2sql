---
applyTo: "tests/**/*.py"
---

# Tester Instructions — Eng2SQL

## Test Structure
- Unit tests: `tests/unit/test_<module>.py`
- Integration tests: `tests/integration/test_<feature>.py`
- Shared fixtures: `tests/conftest.py`

## Naming Conventions
- Test functions: `test_<action>_<condition>_<expected>` e.g. `test_generate_sql_empty_input_raises_value_error`
- Test classes: `Test<ClassName>` e.g. `TestSQLGenerator`
- Fixtures: snake_case noun e.g. `sample_schema`, `mock_openai_client`

## Fixtures
- Define all shared fixtures in `tests/conftest.py`
- Use `pytest.fixture(scope="session")` for expensive setup (DB engine)
- Always yield (not return) fixtures that need teardown

## Mocking
- Mock `openai.OpenAI` client in all unit tests — never hit the real API
- Mock SQLAlchemy engine with `unittest.mock.MagicMock` or `pytest-mock`
- Use `respx` for mocking HTTP calls if needed

## Assertions
- One logical assertion per test (multiple `assert` statements are fine if they test one behaviour)
- Use `pytest.raises(ExceptionType, match="message fragment")` for error tests
- Prefer `assert result == expected` over `assert result` for clarity

## Coverage
- Run: `pytest --cov=src --cov-report=term-missing --cov-fail-under=80`
- Coverage must be ≥ 80% for CI to pass
- Exclusions allowed only for `if TYPE_CHECKING:` blocks and abstract methods

## Integration Tests
- Require `pytest.mark.integration` marker
- Use an in-memory SQLite engine for DB integration tests (avoids real MySQL dependency)
- Skip if environment variable `SKIP_INTEGRATION=true`
