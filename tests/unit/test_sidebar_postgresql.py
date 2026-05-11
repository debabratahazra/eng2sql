"""US-045 — AppTest tests for `SidebarComponent._render_pg_step1` / `_render_pg_step2`.

Mirror of test_sidebar_step2.py for the PostgreSQL branch (EPIC-009).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from utils.exceptions import DatabaseConnectionError

APP_PATH = "src/app.py"


def _select_postgres(at: object) -> None:
    """Switch the db_type radio to PostgreSQL."""
    at.session_state["db_type"] = "PostgreSQL"  # type: ignore[attr-defined]


def _seed_pg_step1_state(at: object, *, password: str = "secret") -> None:
    at.session_state["db_type"] = "PostgreSQL"  # type: ignore[attr-defined]
    at.session_state["pg_host"] = "localhost"  # type: ignore[attr-defined]
    at.session_state["pg_port"] = 5432  # type: ignore[attr-defined]
    at.session_state["pg_user"] = "test_user"  # type: ignore[attr-defined]
    at.session_state["pg_sslmode"] = "prefer"  # type: ignore[attr-defined]
    at.session_state["_pg_password"] = password  # type: ignore[attr-defined]
    at.session_state["pg_server_engine"] = MagicMock(name="server_engine")  # type: ignore[attr-defined]
    at.session_state["pg_available_databases"] = ["app_db", "analytics"]  # type: ignore[attr-defined]


class TestPostgresRadioOption:
    def test_postgresql_appears_in_db_type_radio(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        assert not at.exception
        # The first radio is the db-type selector
        radio_options = list(at.radio[0].options)
        assert "PostgreSQL" in radio_options
        # MySQL must remain the default
        assert at.session_state["db_type"] == "MySQL"


class TestPgStep1:
    def test_pg_step1_form_renders_when_postgres_selected(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _select_postgres(at)
        at.run()
        assert not at.exception
        assert any(s.key == "pg_sslmode_input" for s in at.selectbox)
        assert any(b.key == "pg_connect" for b in at.button)

    def test_pg_step1_success_populates_databases(self) -> None:
        from streamlit.testing.v1 import AppTest

        fake_engine = MagicMock(name="server_engine")
        with patch(
            "services.db_connector.DBConnector.create_engine", return_value=fake_engine
        ), patch(
            "services.db_connector.DBConnector.list_databases",
            return_value=["app_db", "analytics"],
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=10)
            at.run()
            _select_postgres(at)
            at.run()

            # Fill required fields and click Connect
            at.text_input(key="pg_host_input").set_value("localhost")
            at.text_input(key="pg_user_input").set_value("test_user")
            at.text_input(key="pg_password_input").set_value("secret")
            at.button(key="pg_connect").click()
            at.run()

            assert not at.exception
            assert at.session_state["pg_server_engine"] is fake_engine
            assert at.session_state["pg_available_databases"] == ["app_db", "analytics"]
            level, _msg = at.session_state["pg_step1_status"]
            assert level == "success"

    def test_pg_step1_connection_failure_sets_error_status(self) -> None:
        from streamlit.testing.v1 import AppTest

        with patch(
            "services.db_connector.DBConnector.create_engine",
            side_effect=DatabaseConnectionError("boom"),
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=10)
            at.run()
            _select_postgres(at)
            at.run()

            at.text_input(key="pg_host_input").set_value("localhost")
            at.text_input(key="pg_user_input").set_value("test_user")
            at.text_input(key="pg_password_input").set_value("secret")
            at.button(key="pg_connect").click()
            at.run()

            assert not at.exception
            level, msg = at.session_state["pg_step1_status"]
            assert level == "error"
            assert "boom" in msg


class TestPgStep2:
    def test_pg_step2_success_populates_detected_schema(self) -> None:
        from streamlit.testing.v1 import AppTest

        fake_engine = MagicMock(name="db_engine")
        with patch(
            "services.db_connector.DBConnector.create_engine", return_value=fake_engine
        ), patch(
            "services.schema_detector.SchemaDetector.detect_live_schema",
            return_value={},
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=10)
            at.run()
            _seed_pg_step1_state(at)
            at.run()

            at.button(key="pg_db_confirm").click()
            at.run()

            assert not at.exception
            assert at.session_state["detected_schema"] == {}
            assert at.session_state["pg_selected_database"] == "app_db"
            assert at.session_state["pg_engine"] is fake_engine

    def test_pg_step2_success_clears_pg_password(self) -> None:
        from streamlit.testing.v1 import AppTest

        with patch(
            "services.db_connector.DBConnector.create_engine",
            return_value=MagicMock(name="db_engine"),
        ), patch(
            "services.schema_detector.SchemaDetector.detect_live_schema",
            return_value={},
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=10)
            at.run()
            _seed_pg_step1_state(at, password="topsecret")
            at.run()

            at.button(key="pg_db_confirm").click()
            at.run()

            assert not at.exception
            assert "_pg_password" not in at.session_state

    def test_pg_step2_missing_password_warns(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _seed_pg_step1_state(at)
        # Simulate expired session credentials
        del at.session_state["_pg_password"]
        at.run()

        at.button(key="pg_db_confirm").click()
        at.run()

        assert not at.exception
        level, msg = at.session_state["pg_step2_status"]
        assert level == "warning"
        assert "reconnect" in msg.lower()
