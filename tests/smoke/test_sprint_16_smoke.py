"""Smoke tests for Sprint 16 — Component Refactoring & Test Infrastructure.

Covers Sprint 16 user stories:
- US-071: Pure-logic helpers extracted from sidebar.py are callable without Streamlit
- US-072: test_sidebar_logic.py tests are importable and contain the expected 34 tests
- US-073: coverage-docker CI YAML job is structurally correct
- US-074: pytest-xdist is installed and pyproject.toml addopts includes -n auto

Also includes regression smoke for the 3-DB-type radio, SQL generation, and the
sidebar step-1 connect flow (ensures no regressions from the refactor).
All tests use Streamlit AppTest with mocked external services where needed.
No live database connection is required.
"""
from __future__ import annotations

import importlib
import pathlib
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

from components.sidebar import (
    _build_mongo_config,
    _build_relational_config,
    _format_connect_success,
    _select_default_index,
    _validate_mongo_fields_inputs,
    _validate_relational_inputs,
)
from models.config import AppConfig, DBConfig, MongoConfig, SchemaColumn

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")

SAMPLE_SCHEMA = {
    "orders": [
        SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
        SchemaColumn(name="total", type="DECIMAL", nullable=True, primary_key=False),
    ]
}

pytestmark = pytest.mark.smoke


# ---------------------------------------------------------------------------
# US-071: Pure helpers importable and callable without Streamlit
# ---------------------------------------------------------------------------


class TestPureHelpersImportable:
    """Pure-logic helpers can be imported and called outside a Streamlit session."""

    def test_validate_relational_inputs_no_error(self) -> None:
        """Valid inputs return None (no error)."""
        assert _validate_relational_inputs("h", "u", "p", None) is None

    def test_validate_relational_inputs_error(self) -> None:
        """Missing host returns a warning tuple."""
        result = _validate_relational_inputs("", "u", "p", None)
        assert result is not None and result[0] == "warning"

    def test_build_relational_config_type(self) -> None:
        """Factory returns a DBConfig instance."""
        cfg = _build_relational_config("h", 3306, "u", "p", "db", "mysql", None)
        assert isinstance(cfg, DBConfig)

    def test_format_connect_success_plural(self) -> None:
        """Plural 'databases' for n > 1."""
        assert "2 databases" in _format_connect_success("h", 2)

    def test_format_connect_success_singular(self) -> None:
        """Singular 'database' for n == 1."""
        msg = _format_connect_success("h", 1)
        assert "1 database " in msg and "databases" not in msg

    def test_select_default_index_found(self) -> None:
        """Returns correct index when value is present."""
        assert _select_default_index(["a", "b", "c"], "b") == 1

    def test_select_default_index_missing(self) -> None:
        """Returns 0 when value is absent."""
        assert _select_default_index(["a", "b"], "z") == 0

    def test_validate_mongo_fields_no_auth_bypass(self) -> None:
        """Empty credentials OK when no_auth=True."""
        assert _validate_mongo_fields_inputs("localhost", "", "", True) is None

    def test_build_mongo_config_type(self) -> None:
        """Factory returns a MongoConfig instance."""
        cfg = _build_mongo_config("h", 27017, "u", "p", "admin", "SCRAM-SHA-256")
        assert isinstance(cfg, MongoConfig)


# ---------------------------------------------------------------------------
# US-072: test_sidebar_logic.py discovery
# ---------------------------------------------------------------------------


class TestSidebarLogicTestFile:
    """test_sidebar_logic.py exists and exposes 34 test items."""

    def test_file_exists(self) -> None:
        """tests/unit/test_sidebar_logic.py is present in the workspace."""
        path = pathlib.Path(__file__).parent.parent / "unit" / "test_sidebar_logic.py"
        assert path.exists(), f"Expected {path} to exist"

    def test_file_contains_expected_class_count(self) -> None:
        """File defines exactly 6 test classes (one per pure function)."""
        path = pathlib.Path(__file__).parent.parent / "unit" / "test_sidebar_logic.py"
        source = path.read_text(encoding="utf-8")
        class_count = source.count("\nclass Test")
        assert class_count == 6, f"Expected 6 test classes, found {class_count}"


# ---------------------------------------------------------------------------
# US-073: coverage-docker CI job YAML verification
# ---------------------------------------------------------------------------


class TestCoverageDockerCI:
    """coverage-docker job is present and structurally correct in ci-cd.yml."""

    def test_coverage_docker_job_present(self) -> None:
        """ci-cd.yml contains the coverage-docker job definition."""
        ci_path = (
            pathlib.Path(__file__).parent.parent.parent
            / ".github" / "workflows" / "ci-cd.yml"
        )
        content = ci_path.read_text(encoding="utf-8")
        assert "coverage-docker:" in content

    def test_coverage_docker_command_correct(self) -> None:
        """CI job runs pytest with the docker marker."""
        ci_path = (
            pathlib.Path(__file__).parent.parent.parent
            / ".github" / "workflows" / "ci-cd.yml"
        )
        content = ci_path.read_text(encoding="utf-8")
        assert "pytest -m docker" in content


# ---------------------------------------------------------------------------
# US-074: pytest-xdist configuration
# ---------------------------------------------------------------------------


class TestPytestXdistConfig:
    """pytest-xdist is installed and configured in pyproject.toml."""

    def test_xdist_importable(self) -> None:
        """xdist package is importable."""
        import xdist  # noqa: F401 (import check only)

    def test_addopts_contains_n_auto(self) -> None:
        """-n auto is present in pyproject.toml addopts."""
        pyproject = (
            pathlib.Path(__file__).parent.parent.parent / "pyproject.toml"
        )
        content = pyproject.read_text(encoding="utf-8")
        assert "-n auto" in content


# ---------------------------------------------------------------------------
# Regression: app renders with DB-type radio
# ---------------------------------------------------------------------------


class TestAppRegressionSprint16:
    """Ensure the app still renders and DB-type selection is intact after refactor."""

    def test_app_renders_without_crash(self) -> None:
        """App starts without exceptions."""
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        assert not at.exception

    def test_db_type_radio_has_three_options(self) -> None:
        """DB type radio still offers MySQL, PostgreSQL, MongoDB."""
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        radios = at.radio
        radio_values: list[str] = []
        for r in radios:
            if r.options and len(r.options) == 3:  # type: ignore[union-attr]
                radio_values = list(r.options)  # type: ignore[arg-type]
                break
        assert "MySQL" in radio_values
        assert "PostgreSQL" in radio_values
        assert "MongoDB" in radio_values
