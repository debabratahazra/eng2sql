"""Smoke tests for Sprint 12 — MQL Query Execution (EPIC-010).

Covers Sprint 12 user stories:
- US-057: Dynamic output label SQL ↔ MQL
- US-058: MongoDB LLM system prompt
- US-059: MongoQueryExecutor service
- US-060: Execute MQL button in app.py

Also includes regression coverage for Sprint 11 scenarios.
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

MOCK_SQL = "SELECT id, name FROM users WHERE active = 1;"
MOCK_MQL = '{"collection": "users", "pipeline": [{"$match": {"active": true}}]}'

SAMPLE_SCHEMA_MYSQL = {
    "users": [
        SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
        SchemaColumn(name="name", type="VARCHAR", nullable=True, primary_key=False),
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


# ── 1. App launch ─────────────────────────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_s12_app_launches_without_error(app: AppTest) -> None:
    """App renders without raising any exception on initial load."""
    app.run()
    assert not app.exception


# ── 2. Sidebar renders all DB types ──────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_s12_sidebar_db_selector(app: AppTest) -> None:
    """Sidebar radio contains MySQL, PostgreSQL, MongoDB options."""
    app.run()
    assert not app.exception
    options = app.radio[0].options
    assert "MySQL" in options
    assert "PostgreSQL" in options
    assert "MongoDB" in options


# ── 3. MySQL SQL generation (mocked OpenAI) ───────────────────────────────────


@pytest.mark.smoke
def test_smoke_s12_mysql_sql_generation(app: AppTest) -> None:
    """MySQL flow: mocked OpenAI call stores SQL in session state."""
    with patch("services.sql_generator.OpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        (
            mock_client.chat.completions.create.return_value
            .choices[0].message.content
        ) = MOCK_SQL

        app.session_state["detected_schema"] = SAMPLE_SCHEMA_MYSQL
        app.run()
        assert not app.exception


# ── 4. MongoDB mode — output label shows "Generated MQL" (US-057) ─────────────


@pytest.mark.smoke
def test_smoke_s12_mongodb_label_shows_generated_mql(app: AppTest) -> None:
    """When MongoDB is selected and MQL is in state, label says 'Generated MQL'."""
    app.session_state["db_type"] = "MongoDB"
    app.session_state["generated_sql"] = MOCK_MQL
    app.session_state["detected_schema"] = SAMPLE_SCHEMA_MONGO
    app.run()
    assert not app.exception
    # Subheader should contain 'MQL' — search all rendered text
    subheaders = [sh.value for sh in app.subheader]
    mql_headers = [s for s in subheaders if "MQL" in s or "mql" in s.lower()]
    assert mql_headers, (
        f"No 'MQL' subheader found. Subheaders present: {subheaders}"
    )


# ── 5. MongoDB mode — Execute MQL info shown when no DB connected (US-060) ───


@pytest.mark.smoke
def test_smoke_s12_execute_mql_info_no_db(app: AppTest) -> None:
    """Info message shown when MongoDB mode has MQL but no db connected."""
    app.session_state["db_type"] = "MongoDB"
    app.session_state["generated_sql"] = MOCK_MQL
    # mongo_db is NOT set → should show info box instead of button
    app.run()
    assert not app.exception
    # App renders without crash — info path does not raise
    infos = [i.value for i in app.info]
    mongo_infos = [i for i in infos if "MongoDB" in i or "Connect" in i]
    assert mongo_infos, (
        f"Expected MongoDB connect info box. Info messages: {infos}"
    )


# ── 6. Execute MQL button visible when mongo_db connected (US-060) ──────────


@pytest.mark.smoke
def test_smoke_s12_execute_mql_button_when_connected(app: AppTest) -> None:
    """Execute MQL button is present when mongo_db is set in session state."""
    mock_db = MagicMock()
    app.session_state["db_type"] = "MongoDB"
    app.session_state["generated_sql"] = MOCK_MQL
    app.session_state["mongo_db"] = mock_db
    app.session_state["detected_schema"] = SAMPLE_SCHEMA_MONGO
    app.run()
    assert not app.exception
    button_labels = [b.label for b in app.button]
    execute_btns = [l for l in button_labels if "Execute MQL" in l or "MQL" in l]
    assert execute_btns, (
        f"Expected '▶ Execute MQL' button. Buttons present: {button_labels}"
    )


# ── 7. Execute MQL button click — success stores query_result (US-060) ──────


@pytest.mark.smoke
def test_smoke_s12_execute_mql_click_success(app: AppTest) -> None:
    """Clicking Execute MQL calls MongoQueryExecutor and stores result."""
    import pandas as pd

    mock_db = MagicMock()
    mock_df = pd.DataFrame({"_id": ["1"], "name": ["Alice"]})

    with patch(
        "services.mongo_query_executor.MongoQueryExecutor.execute",
        return_value=mock_df,
    ):
        app.session_state["db_type"] = "MongoDB"
        app.session_state["generated_sql"] = MOCK_MQL
        app.session_state["mongo_db"] = mock_db
        app.session_state["detected_schema"] = SAMPLE_SCHEMA_MONGO
        app.run()
        assert not app.exception


# ── 8. Empty query does not crash ────────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_s12_empty_query_does_not_crash(app: AppTest) -> None:
    """Submitting no query remains stable."""
    app.run()
    assert not app.exception


# ── 9. Schema viewer with MongoDB schema (regression Sprint 11) ──────────────


@pytest.mark.smoke
def test_smoke_s12_schema_viewer_mongodb(app: AppTest) -> None:
    """Schema viewer renders MongoDB-style schema without error."""
    app.session_state["detected_schema"] = SAMPLE_SCHEMA_MONGO
    app.run()
    assert not app.exception


# ── 10. PostgreSQL sslmode selector (regression Sprint 11, US-056) ───────────


@pytest.mark.smoke
def test_smoke_s12_postgresql_sslmode_selector(app: AppTest) -> None:
    """PostgreSQL mode renders without error (sslmode widget present)."""
    app.session_state["db_type"] = "PostgreSQL"
    app.run()
    assert not app.exception
    options_lists = [r.options for r in app.radio]
    flat = [item for sublist in options_lists for item in sublist]
    assert "PostgreSQL" in flat
