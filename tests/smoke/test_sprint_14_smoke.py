"""Smoke tests for Sprint 14 — Dependency Hygiene & Coverage Uplift.

Covers Sprint 14 user stories:
- US-063: testcontainers[mongo] declared in dev dependencies
- US-064: schema_detector.py mock-based unit tests (regression: app still works)
- US-065: db_connector.py mock-based unit tests (regression: connect/execute paths)

Also includes regression coverage for Sprint 12 / 13 key paths.
All tests use Streamlit AppTest with mocked external services.
No live database connection is required.
"""
from __future__ import annotations

import importlib.metadata
import importlib.util
import pathlib
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

from models.config import SchemaColumn

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")

MOCK_SQL = "SELECT id, name FROM users WHERE active = 1;"
MOCK_MQL = '{"collection": "users", "pipeline": [{"$match": {"active": true}}]}'

SAMPLE_SCHEMA_MYSQL = {
    "users": [
        SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
        SchemaColumn(name="name", type="VARCHAR(100)", nullable=False, primary_key=False),
        SchemaColumn(name="active", type="TINYINT", nullable=False, primary_key=False),
    ]
}

SAMPLE_SCHEMA_MONGO = {
    "users": [
        SchemaColumn(name="_id", type="ObjectId", nullable=False, primary_key=True),
        SchemaColumn(name="name", type="str", nullable=True, primary_key=False),
        SchemaColumn(name="active", type="bool", nullable=True, primary_key=False),
    ]
}


@pytest.fixture()
def app() -> AppTest:
    """Fresh AppTest instance for each test."""
    return AppTest.from_file(APP_PATH, default_timeout=15)


# ---------------------------------------------------------------------------
# US-063 — testcontainers[mongo] dependency hygiene
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s14_testcontainers_importable() -> None:
    """US-063: testcontainers package can be imported (installed correctly)."""
    spec = importlib.util.find_spec("testcontainers")
    assert spec is not None, "testcontainers must be installed (pip install testcontainers[mongo])"


@pytest.mark.smoke
def test_smoke_s14_pyproject_declares_testcontainers_mongo() -> None:
    """US-063: pyproject.toml declares testcontainers[mongo] in dev deps."""
    pyproject_path = pathlib.Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    assert "testcontainers[mongo]" in content, (
        "testcontainers[mongo] must be declared in pyproject.toml [project.optional-dependencies].dev"
    )


@pytest.mark.smoke
def test_smoke_s14_requirements_declares_testcontainers_mongo() -> None:
    """US-063: requirements.txt declares testcontainers[mongo]."""
    req_path = pathlib.Path(__file__).parent.parent.parent / "requirements.txt"
    content = req_path.read_text(encoding="utf-8")
    assert "testcontainers[mongo]" in content, (
        "testcontainers[mongo] must be declared in requirements.txt"
    )


# ---------------------------------------------------------------------------
# US-064 — schema_detector.py coverage uplift (regression: app unaffected)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s14_app_renders_after_schema_detector_uplift(app: AppTest) -> None:
    """US-064: App still launches without exception after schema_detector test changes."""
    app.run()
    assert not app.exception


@pytest.mark.smoke
def test_smoke_s14_mysql_schema_detected_in_session_state(app: AppTest) -> None:
    """US-064: detected_schema (SchemaColumn objects) still drives MySQL UI correctly."""
    app.run()
    app.session_state["db_type"] = "MySQL"
    app.session_state["db_engine"] = MagicMock(name="db_engine")
    app.session_state["detected_schema"] = SAMPLE_SCHEMA_MYSQL
    app.run()
    assert not app.exception


@pytest.mark.smoke
def test_smoke_s14_schema_detector_module_importable() -> None:
    """US-064: schema_detector module still importable after test file changes."""
    from services.schema_detector import SchemaDetector  # noqa: F401
    assert SchemaDetector is not None


# ---------------------------------------------------------------------------
# US-065 — db_connector.py coverage uplift (regression: connect/execute paths)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s14_db_connector_module_importable() -> None:
    """US-065: db_connector module still importable after test file changes."""
    from services.db_connector import DBConnector  # noqa: F401
    assert DBConnector is not None


@pytest.mark.smoke
def test_smoke_s14_mysql_connect_button_present(app: AppTest) -> None:
    """US-065: MySQL connect button (Step 1) still renders (create_engine path regression)."""
    app.run()
    assert not app.exception
    assert any(b.key == "mysql_connect" for b in app.button)


@pytest.mark.smoke
def test_smoke_s14_postgresql_connect_button_present(app: AppTest) -> None:
    """US-065: PostgreSQL connect button still renders (db_connector regression)."""
    app.run()
    app.session_state["db_type"] = "PostgreSQL"
    app.run()
    assert not app.exception
    assert any(b.key == "pg_connect" for b in app.button)


# ---------------------------------------------------------------------------
# General regression checks
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s14_all_three_db_types_in_radio(app: AppTest) -> None:
    """Regression: Radio widget exposes MySQL, PostgreSQL, MongoDB options."""
    app.run()
    assert not app.exception
    options = list(app.radio[0].options)
    assert "MySQL" in options
    assert "PostgreSQL" in options
    assert "MongoDB" in options


@pytest.mark.smoke
def test_smoke_s14_execute_mql_button_present_when_mongo_connected(app: AppTest) -> None:
    """Regression: Execute MQL button (key=mongo_execute) still renders for MongoDB."""
    app.run()
    app.session_state["db_type"] = "MongoDB"
    app.session_state["mongo_db"] = MagicMock(name="mongo_db")
    app.session_state["generated_sql"] = MOCK_MQL
    app.run()
    assert not app.exception
    assert any(b.key == "mongo_execute" for b in app.button)


@pytest.mark.smoke
def test_smoke_s14_sql_generation_pipeline_mysql(app: AppTest) -> None:
    """Regression: MySQL SQL generation pipeline still works end-to-end (mocked LLM)."""
    import pandas as pd

    fake_df = pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
    app.run()
    app.session_state["db_type"] = "MySQL"
    app.session_state["db_engine"] = MagicMock(name="db_engine")
    app.session_state["detected_schema"] = SAMPLE_SCHEMA_MYSQL
    app.session_state["generated_sql"] = MOCK_SQL

    with patch(
        "services.db_connector.DBConnector.execute_query",
        return_value=fake_df,
    ):
        app.run()

    assert not app.exception
