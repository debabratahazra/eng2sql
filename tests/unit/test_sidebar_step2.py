"""US-040 — AppTest tests for `SidebarComponent._render_step2` (MySQL Step 2).

These tests exercise the live-MySQL "select database" branch of the sidebar
without requiring a real database. ``DBConnector.create_engine`` and
``SchemaDetector.detect_live_schema`` are patched at the class level so any
instance created inside the Streamlit app picks up the mock.

Pre-conditions (Step 1 success) are simulated by pre-populating session state
with the keys that ``_render_step1`` would normally write before
``_render_step2`` runs.

References:
    - US-040 (Sprint 9) — mock-patched AppTest tests for `_render_step2`.
    - SPRINT-8-retro.md Action Item 1.
    - tests/unit/test_sidebar_ui.py — canonical AppTest pattern.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from sqlalchemy.exc import OperationalError

from utils.exceptions import DatabaseConnectionError

APP_PATH = "src/app.py"


def _seed_step1_state(at: object, *, password: str = "secret") -> None:
    """Populate session state to simulate a successful Step 1 connection.

    Args:
        at: The :class:`streamlit.testing.v1.AppTest` instance.
        password: Plaintext password to seed into ``_db_password``.
    """
    at.session_state["db_type"] = "MySQL"  # type: ignore[attr-defined]
    at.session_state["db_host"] = "localhost"  # type: ignore[attr-defined]
    at.session_state["db_port"] = 3306  # type: ignore[attr-defined]
    at.session_state["db_user"] = "test_user"  # type: ignore[attr-defined]
    at.session_state["_db_password"] = password  # type: ignore[attr-defined]
    at.session_state["db_server_engine"] = MagicMock(name="server_engine")  # type: ignore[attr-defined]
    at.session_state["available_databases"] = ["mydb", "otherdb"]  # type: ignore[attr-defined]


class TestRenderStep2Success:
    """Successful MySQL engine creation + schema detection."""

    def test_step2_panel_renders_when_step1_completed(self) -> None:
        """When Step 1 state is present, the Step 2 dropdown is rendered."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()  # initial run to create session_state container
        _seed_step1_state(at)
        at.run()
        assert not at.exception
        # The Step 2 selectbox is keyed 'mysql_db_select'
        assert any(s.key == "mysql_db_select" for s in at.selectbox)

    def test_step2_success_populates_detected_schema(self) -> None:
        """Successful Select Database stores engine + schema in session state."""
        from streamlit.testing.v1 import AppTest

        fake_engine = MagicMock(name="db_engine")
        # Use empty schema — SchemaViewerComponent renders "No tables found."
        # without iterating column objects, so we can keep the test free of
        # SchemaColumn fixtures.
        fake_schema: dict = {}

        with patch(
            "services.db_connector.DBConnector.create_engine", return_value=fake_engine
        ), patch(
            "services.schema_detector.SchemaDetector.detect_live_schema",
            return_value=fake_schema,
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=10)
            at.run()
            _seed_step1_state(at)
            at.run()

            at.button(key="mysql_db_confirm").click()
            at.run()

            assert not at.exception
            assert at.session_state["detected_schema"] == fake_schema
            assert at.session_state["selected_database"] == "mydb"
            assert at.session_state["db_engine"] is fake_engine

    def test_step2_success_clears_db_password(self) -> None:
        """After Select Database succeeds, ``_db_password`` is removed."""
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
            _seed_step1_state(at, password="topsecret")
            at.run()

            at.button(key="mysql_db_confirm").click()
            at.run()

            assert not at.exception
            assert "_db_password" not in at.session_state

    def test_step2_success_status_is_success(self) -> None:
        """A successful selection writes a (success, ...) tuple into step2_status."""
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
            _seed_step1_state(at)
            at.run()

            at.button(key="mysql_db_confirm").click()
            at.run()

            level, msg = at.session_state["step2_status"]
            assert level == "success"
            assert "mydb" in msg


class TestRenderStep2Failure:
    """Failed MySQL engine creation + error surfacing."""

    def test_step2_create_engine_failure_records_error_status(self) -> None:
        """When create_engine raises, step2_status is set to ('error', ...)."""
        from streamlit.testing.v1 import AppTest

        with patch(
            "services.db_connector.DBConnector.create_engine",
            side_effect=DatabaseConnectionError("Access denied for user 'test_user'@'localhost'"),
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=10)
            at.run()
            _seed_step1_state(at)
            at.run()

            at.button(key="mysql_db_confirm").click()
            at.run()

            assert not at.exception
            assert "step2_status" in at.session_state
            level, msg = at.session_state["step2_status"]
            assert level == "error"
            assert "denied" in msg.lower() or "access" in msg.lower()
            # detected_schema must NOT be populated on failure (None or absent).
            # app.py initialises the key to None, so we check it's falsy.
            # SafeSessionState supports `in` and `[]` but not `.get()`.
            if "detected_schema" in at.session_state:
                assert not at.session_state["detected_schema"]

    def test_step2_operational_error_wrapped_as_database_error(self) -> None:
        """SQLAlchemy OperationalError from create_engine surfaces as error status.

        DBConnector.create_engine wraps SQLAlchemy errors in
        :class:`DatabaseConnectionError`; we simulate that wrapping here.
        """
        from streamlit.testing.v1 import AppTest

        op_err = OperationalError("SELECT 1", {}, Exception("Lost connection"))
        with patch(
            "services.db_connector.DBConnector.create_engine",
            side_effect=DatabaseConnectionError(f"{op_err}"),
        ):
            at = AppTest.from_file(APP_PATH, default_timeout=10)
            at.run()
            _seed_step1_state(at)
            at.run()

            at.button(key="mysql_db_confirm").click()
            at.run()

            assert not at.exception
            level, _ = at.session_state["step2_status"]
            assert level == "error"

    def test_step2_missing_password_yields_warning(self) -> None:
        """If _db_password is absent (session expired), a warning is recorded."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _seed_step1_state(at)
        # Simulate expired credentials — SafeSessionState supports `del` but
        # not `.pop()`; use `del` per the AppTest quirks documented in US-041.
        del at.session_state["_db_password"]
        at.run()

        at.button(key="mysql_db_confirm").click()
        at.run()

        assert not at.exception
        level, msg = at.session_state["step2_status"]
        assert level == "warning"
        assert "reconnect" in msg.lower() or "expired" in msg.lower()


class TestRenderStep2Spinner:
    """Spinner rendering during Step 2 connection."""

    def test_step2_no_databases_shows_warning(self) -> None:
        """When available_databases is empty the panel shows a warning, not a dropdown."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _seed_step1_state(at)
        at.session_state["available_databases"] = []
        at.run()

        assert not at.exception
        # No selectbox keyed 'mysql_db_select' should be rendered
        assert not any(s.key == "mysql_db_select" for s in at.selectbox)
        # A warning element must be present
        assert len(at.warning) >= 1
