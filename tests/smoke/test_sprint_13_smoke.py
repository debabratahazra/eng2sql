"""Smoke tests for Sprint 13 — Refactor + Optional-Deps + MQL Tests (Sprint 13).

Covers Sprint 13 user stories:
- US-051: RelationalConnectorSidebar mixin refactor (sidebar.py)
- US-054: pyproject.toml optional-dependency groups
- US-061: MongoQueryExecutor Docker integration test (skipped if no Docker)
- US-062: Execute MQL button unit tests

Also includes regression coverage for Sprint 11 and Sprint 12 scenarios.
All tests use Streamlit AppTest with mocked external services.
No live database connection is required.
"""
from __future__ import annotations

import pathlib
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

from models.config import SchemaColumn

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")

MOCK_SQL = "SELECT id, customer, total FROM orders WHERE status = 'delivered';"
MOCK_MQL = '{"collection": "orders", "pipeline": [{"$match": {"status": "delivered"}}]}'

SAMPLE_SCHEMA_MYSQL = {
    "orders": [
        SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
        SchemaColumn(name="customer", type="VARCHAR(100)", nullable=False, primary_key=False),
        SchemaColumn(name="total", type="DECIMAL(10,2)", nullable=False, primary_key=False),
        SchemaColumn(name="status", type="VARCHAR(20)", nullable=False, primary_key=False),
    ]
}

SAMPLE_SCHEMA_MONGO = {
    "orders": [
        SchemaColumn(name="_id", type="ObjectId", nullable=False, primary_key=True),
        SchemaColumn(name="customer", type="str", nullable=True, primary_key=False),
        SchemaColumn(name="total", type="float", nullable=True, primary_key=False),
        SchemaColumn(name="status", type="str", nullable=True, primary_key=False),
    ]
}


@pytest.fixture()
def app() -> AppTest:
    """Fresh AppTest instance for each test."""
    return AppTest.from_file(APP_PATH, default_timeout=15)


# ---------------------------------------------------------------------------
# US-051 — Sidebar mixin regression checks
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s13_mysql_step1_renders_after_refactor(app: AppTest) -> None:
    """MySQL Step 1 form still renders correctly after US-051 sidebar refactor."""
    app.run()
    assert not app.exception
    assert any(b.key == "mysql_connect" for b in app.button)


@pytest.mark.smoke
def test_smoke_s13_postgresql_step1_renders_after_refactor(app: AppTest) -> None:
    """PostgreSQL Step 1 form still renders correctly after US-051 sidebar refactor."""
    app.run()
    app.session_state["db_type"] = "PostgreSQL"
    app.run()
    assert not app.exception
    assert any(b.key == "pg_connect" for b in app.button)
    assert any(s.key == "pg_sslmode_input" for s in app.selectbox)


@pytest.mark.smoke
def test_smoke_s13_mysql_step2_renders_with_seeded_state(app: AppTest) -> None:
    """MySQL Step 2 selectbox appears when Step 1 state is pre-seeded (regression)."""
    app.run()
    app.session_state["db_type"] = "MySQL"
    app.session_state["db_server_engine"] = MagicMock(name="server_engine")
    app.session_state["available_databases"] = ["shop_db", "analytics"]
    app.run()
    assert not app.exception
    assert any(s.key == "mysql_db_select" for s in app.selectbox)


@pytest.mark.smoke
def test_smoke_s13_postgresql_step2_renders_with_seeded_state(app: AppTest) -> None:
    """PostgreSQL Step 2 selectbox appears when Step 1 state is pre-seeded (regression)."""
    app.run()
    app.session_state["db_type"] = "PostgreSQL"
    app.session_state["pg_server_engine"] = MagicMock(name="pg_server_engine")
    app.session_state["pg_available_databases"] = ["main_db", "dw"]
    app.run()
    assert not app.exception
    assert any(s.key == "pg_db_select" for s in app.selectbox)


@pytest.mark.smoke
def test_smoke_s13_admin_db_field_renders_for_postgresql(app: AppTest) -> None:
    """Admin DB text field still present after US-051 refactor (US-052 regression)."""
    app.run()
    app.session_state["db_type"] = "PostgreSQL"
    app.run()
    assert not app.exception
    assert any(ti.key == "pg_admin_db_input" for ti in app.text_input)


# ---------------------------------------------------------------------------
# US-062 — Execute MQL button regression checks
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s13_execute_mql_button_present_when_mongo_connected(app: AppTest) -> None:
    """Execute MQL button renders when mongo_db is set and MQL is generated."""
    app.run()
    app.session_state["db_type"] = "MongoDB"
    app.session_state["mongo_db"] = MagicMock(name="mongo_db")
    app.session_state["generated_sql"] = MOCK_MQL
    app.run()
    assert not app.exception
    assert any(b.key == "mongo_execute" for b in app.button)


@pytest.mark.smoke
def test_smoke_s13_execute_mql_info_when_no_db_connected(app: AppTest) -> None:
    """Info message shown when MongoDB type selected but no mongo_db in state."""
    app.run()
    app.session_state["db_type"] = "MongoDB"
    app.session_state["generated_sql"] = MOCK_MQL
    # mongo_db not set → info path
    app.run()
    assert not app.exception
    info_texts = [i.value for i in app.info]
    assert any("Connect" in t or "connect" in t for t in info_texts)


@pytest.mark.smoke
def test_smoke_s13_execute_mql_success_click(app: AppTest) -> None:
    """Clicking Execute MQL with a valid mock executor stores query_result."""
    import pandas as pd

    fake_df = pd.DataFrame({"customer": ["Alice"], "total": [99.99]})
    app.run()
    app.session_state["db_type"] = "MongoDB"
    app.session_state["mongo_db"] = MagicMock(name="mongo_db")
    app.session_state["generated_sql"] = MOCK_MQL

    with patch(
        "services.mongo_query_executor.MongoQueryExecutor.execute",
        return_value=fake_df,
    ):
        app.run()
        app.button(key="mongo_execute").click()
        app.run()

    assert not app.exception
    result = app.session_state["query_result"] if "query_result" in app.session_state else None
    assert result is not None


# ---------------------------------------------------------------------------
# General regression (Sprint 11 / 12 core paths)
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s13_app_launches_without_error(app: AppTest) -> None:
    """App renders without exception after Sprint 13 changes."""
    app.run()
    assert not app.exception


@pytest.mark.smoke
def test_smoke_s13_db_type_radio_has_all_three_options(app: AppTest) -> None:
    """Radio widget exposes MySQL, PostgreSQL, MongoDB options (regression)."""
    app.run()
    assert not app.exception
    options = list(app.radio[0].options)
    assert "MySQL" in options
    assert "PostgreSQL" in options
    assert "MongoDB" in options
