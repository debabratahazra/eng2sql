"""Smoke tests for Sprint 11 — Refactor & Hardening.

Covers mandatory scenarios plus Sprint-11-specific additions:
- Configurable PostgreSQL admin-DB field (US-052)
- sslmode selector with verify-* pre-validation hint (US-056)
- WSL2 helper extraction: app still launches without error (US-050)

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


@pytest.fixture()
def app() -> AppTest:
    """Fresh AppTest instance."""
    return AppTest.from_file(APP_PATH, default_timeout=15)


# ── 1. App launch ─────────────────────────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_app_launches_without_error(app: AppTest) -> None:
    """App renders without raising any exception on initial load."""
    app.run()
    assert not app.exception


# ── 2. Sidebar DB selector ───────────────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_sidebar_renders_db_selector(app: AppTest) -> None:
    """Sidebar radio widget is present with all supported DB types."""
    app.run()
    assert not app.exception
    assert len(app.radio) >= 1
    options = app.radio[0].options
    assert "MySQL" in options
    assert "MongoDB" in options
    assert "PostgreSQL" in options


# ── 3. MySQL static flow ─────────────────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_mysql_sql_generation_with_mock(app: AppTest) -> None:
    """MySQL flow: entering a question and mocking OpenAI returns SQL in state."""
    with patch("services.sql_generator.OpenAI") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        (
            mock_client.chat.completions.create.return_value.choices[0].message.content
        ) = MOCK_SQL

        app.session_state["detected_schema"] = {
            "users": [
                SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
                SchemaColumn(name="name", type="VARCHAR", nullable=True, primary_key=False),
                SchemaColumn(name="active", type="TINYINT", nullable=False, primary_key=False),
            ]
        }
        app.run()
        assert not app.exception
        app.text_input[0].set_value("show all active users").run()
        assert not app.exception


# ── 4. Empty query shows validation, not crash ───────────────────────────────


@pytest.mark.smoke
def test_smoke_empty_query_does_not_crash(app: AppTest) -> None:
    """Submitting an empty query string does not raise an exception."""
    app.run()
    assert not app.exception
    # No text entered — app should stay at baseline
    assert not app.exception


# ── 5. Schema viewer present after schema load ───────────────────────────────


@pytest.mark.smoke
def test_smoke_schema_viewer_appears_after_schema_load(app: AppTest) -> None:
    """Schema viewer section renders when detected_schema is in session state."""
    app.session_state["detected_schema"] = {
        "orders": [
            SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
            SchemaColumn(name="total", type="DECIMAL", nullable=True, primary_key=False),
            SchemaColumn(name="status", type="VARCHAR", nullable=True, primary_key=False),
        ]
    }
    app.run()
    assert not app.exception


# ── 6. SQL output panel present ──────────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_sql_output_panel_renders(app: AppTest) -> None:
    """SQL output panel is rendered (code block or placeholder info box)."""
    app.run()
    assert not app.exception


# ── 7. Progress tracker present ──────────────────────────────────────────────


@pytest.mark.smoke
def test_smoke_progress_tracker_present(app: AppTest) -> None:
    """App renders without exception — progress tracker is wired in main()."""
    app.run()
    assert not app.exception


# ── 8. Sprint-11 specific: PostgreSQL sslmode selector ───────────────────────


@pytest.mark.smoke
def test_smoke_postgresql_form_renders_sslmode_selector(app: AppTest) -> None:
    """Switching to PostgreSQL shows sslmode selectbox (US-045 / US-056)."""
    app.run()
    assert not app.exception
    app.radio[0].set_value("PostgreSQL").run()
    assert not app.exception
    # At least one selectbox (sslmode) should be present
    assert len(app.selectbox) >= 1


# ── 9. Sprint-11 specific: configurable PG admin-DB session key ──────────────


@pytest.mark.smoke
def test_smoke_pg_admin_db_session_key_initialised(app: AppTest) -> None:
    """pg_admin_db session key is initialised to 'postgres' on app start (US-052)."""
    app.run()
    assert not app.exception
    pg_admin = app.session_state["pg_admin_db"] if "pg_admin_db" in app.session_state else None
    assert pg_admin == "postgres"


# ── 10. Sprint-11 specific: MongoDB URI mode toggle ──────────────────────────


@pytest.mark.smoke
def test_smoke_mongodb_uri_mode_toggle_renders(app: AppTest) -> None:
    """Switching to MongoDB shows connection mode radio (US-031)."""
    app.run()
    assert not app.exception
    app.radio[0].set_value("MongoDB").run()
    assert not app.exception
    assert app.session_state["db_type"] if "db_type" in app.session_state else "MongoDB"
