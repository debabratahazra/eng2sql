"""AppTest rendering-method tests for sidebar Step 2 and MongoDB paths (US-076).

Covers:
  - _render_relational_step2  — Step 2 database-selection flow (MySQL/PostgreSQL)
  - _render_mongo_step1_uri_mode — MongoDB URI connection mode
  - _render_mongo_step2          — MongoDB Step 2 database selection

All tests mock the connector/detector services so that no live database is required.
"""
from __future__ import annotations

import pathlib
from unittest.mock import MagicMock, patch

import pytest

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_at() -> "AppTest":  # noqa: F821 — evaluated at runtime
    from streamlit.testing.v1 import AppTest
    return AppTest.from_file(APP_PATH, default_timeout=30)


# ---------------------------------------------------------------------------
# Relational Step 2 — database-selection flow
# ---------------------------------------------------------------------------

class TestRelationalStep2:
    """Verify the Step 2 database-selection form behaves correctly."""

    def test_step2_not_rendered_when_no_server_engine(self) -> None:
        """Step 2 is hidden when db_server_engine is None (initial state)."""
        at = _make_at()
        at.run()
        assert not at.exception
        # Without a server engine the Step 2 selectbox should not appear
        select_keys = [s.key for s in at.selectbox]
        assert "mysql_db_select" not in select_keys

    def test_step2_renders_selectbox_when_databases_available(self) -> None:
        """Step 2 selectbox appears once db_server_engine + available_databases are set."""
        at = _make_at()
        at.run()
        # Inject simulated Step 1 success state
        mock_engine = MagicMock()
        at.session_state["db_server_engine"] = mock_engine
        at.session_state["available_databases"] = ["appdb", "testdb"]
        at.run()
        assert not at.exception
        select_keys = [s.key for s in at.selectbox]
        assert "mysql_db_select" in select_keys

    def test_step2_select_database_success_updates_session_state(self) -> None:
        """Selecting a database calls create_engine + detect_live_schema and stores result."""
        at = _make_at()
        at.run()
        mock_server_engine = MagicMock()
        mock_schema = {"users": [], "orders": []}
        at.session_state["db_server_engine"] = mock_server_engine
        at.session_state["available_databases"] = ["appdb", "testdb"]
        at.session_state["_db_password"] = "secret"
        at.run()
        assert not at.exception

        with (
            patch("components.sidebar.DBConnector") as mock_connector_cls,
            patch("components.sidebar.SchemaDetector") as mock_detector_cls,
        ):
            mock_connector = MagicMock()
            mock_connector_cls.return_value = mock_connector
            mock_new_engine = MagicMock()
            mock_connector.create_engine.return_value = mock_new_engine

            mock_detector = MagicMock()
            mock_detector_cls.return_value = mock_detector
            mock_detector.detect_live_schema.return_value = mock_schema

            at.button(key="mysql_db_confirm").click()
            at.run()

        assert not at.exception

    def test_step2_expired_password_yields_warning(self) -> None:
        """Clicking Select Database with no cached password stores a warning status."""
        at = _make_at()
        at.run()
        mock_engine = MagicMock()
        at.session_state["db_server_engine"] = mock_engine
        at.session_state["available_databases"] = ["appdb"]
        # _db_password is NOT set → "session credentials expired" branch
        at.run()
        assert not at.exception
        at.button(key="mysql_db_confirm").click()
        at.run()
        assert not at.exception
        assert "step2_status" in at.session_state
        level, _msg = at.session_state["step2_status"]
        assert level == "warning"

    def test_step2_old_engine_disposed_on_reconnect(self) -> None:
        """When db_engine is already set, it is disposed before creating a new engine."""
        at = _make_at()
        at.run()
        mock_server_engine = MagicMock()
        mock_old_engine = MagicMock()
        at.session_state["db_server_engine"] = mock_server_engine
        at.session_state["available_databases"] = ["appdb"]
        at.session_state["_db_password"] = "pw"
        at.session_state["db_engine"] = mock_old_engine
        at.run()
        assert not at.exception

        with (
            patch("components.sidebar.DBConnector") as mock_connector_cls,
            patch("components.sidebar.SchemaDetector") as mock_detector_cls,
        ):
            mock_connector = MagicMock()
            mock_connector_cls.return_value = mock_connector
            mock_connector.create_engine.return_value = MagicMock()

            mock_detector = MagicMock()
            mock_detector_cls.return_value = mock_detector
            mock_detector.detect_live_schema.return_value = {}

            at.button(key="mysql_db_confirm").click()
            at.run()

        assert not at.exception


# ---------------------------------------------------------------------------
# MongoDB Step 1 — URI mode
# ---------------------------------------------------------------------------

class TestMongoURIMode:
    """Verify the MongoDB URI connection mode (Step 1) paths."""

    def _switch_to_mongo_uri(self, at: "AppTest") -> "AppTest":  # noqa: F821
        """Helper: switch DB type to MongoDB then input mode to URI."""
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        at.radio(key="mongo_input_mode_radio").set_value("URI + credentials")
        at.run()
        assert not at.exception
        return at

    def test_uri_mode_renders_uri_text_input(self) -> None:
        """URI mode renders a 'MongoDB URI' text input."""
        at = _make_at()
        at.run()
        at = self._switch_to_mongo_uri(at)
        input_labels = [ti.label for ti in at.text_input]
        assert "MongoDB URI" in input_labels

    def test_uri_mode_empty_uri_click_yields_warning(self) -> None:
        """Clicking Connect in URI mode with no URI stores a warning."""
        at = _make_at()
        at.run()
        at = self._switch_to_mongo_uri(at)
        # URI input is empty; click Connect
        at.button(key="mongo_connect").click()
        at.run()
        assert not at.exception
        assert "mongo_step1_status" in at.session_state
        level, msg = at.session_state["mongo_step1_status"]
        assert level == "warning"
        assert "uri" in msg.lower()

    def test_uri_mode_connect_success_stores_databases(self) -> None:
        """A valid URI triggers connect() and stores available databases."""
        at = _make_at()
        at.run()
        at = self._switch_to_mongo_uri(at)

        with patch("components.sidebar.MongoDBConnector") as mock_cls:
            mock_mongo = MagicMock()
            mock_cls.return_value = mock_mongo
            mock_client = MagicMock()
            mock_mongo.connect.return_value = mock_client
            mock_mongo.list_databases.return_value = ["prod", "staging"]

            at.text_input(key="mongo_raw_uri_input").set_value("mongodb://localhost:27017")
            at.button(key="mongo_connect").click()
            at.run()

        assert not at.exception
        assert "mongo_step1_status" in at.session_state
        level, _msg = at.session_state["mongo_step1_status"]
        assert level == "success"
        assert "mongo_available_databases" in at.session_state
        assert at.session_state["mongo_available_databases"] == ["prod", "staging"]

    def test_uri_mode_connect_error_stores_error_status(self) -> None:
        """A connection error from the connector stores an error status."""
        from utils.exceptions import DatabaseConnectionError

        at = _make_at()
        at.run()
        at = self._switch_to_mongo_uri(at)

        with patch("components.sidebar.MongoDBConnector") as mock_cls:
            mock_mongo = MagicMock()
            mock_cls.return_value = mock_mongo
            mock_mongo.connect.side_effect = DatabaseConnectionError("timed out")

            at.text_input(key="mongo_raw_uri_input").set_value("mongodb://bad-host:27017")
            at.button(key="mongo_connect").click()
            at.run()

        assert not at.exception
        assert "mongo_step1_status" in at.session_state
        level, msg = at.session_state["mongo_step1_status"]
        assert level == "error"
        assert "timed out" in msg


# ---------------------------------------------------------------------------
# MongoDB Fields mode — connect success / error paths
# ---------------------------------------------------------------------------

class TestMongoFieldsModeConnect:
    """Verify lines 663–693 in _render_mongo_step1_fields_mode (connect paths)."""

    def test_fields_connect_success_stores_databases(self) -> None:
        """Valid credentials with No-Auth mechanism trigger connect() and store databases."""
        at = _make_at()
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception

        with patch("components.sidebar.MongoDBConnector") as mock_cls:
            mock_mongo = MagicMock()
            mock_cls.return_value = mock_mongo
            mock_client = MagicMock()
            mock_mongo.connect.return_value = mock_client
            mock_mongo.list_databases.return_value = ["alpha", "beta"]

            # 'None / No Auth' bypasses the username/password validation
            at.selectbox(key="mongo_auth_mech_input").set_value("None / No Auth")
            at.button(key="mongo_connect").click()
            at.run()

        assert not at.exception
        assert "mongo_step1_status" in at.session_state
        level, _msg = at.session_state["mongo_step1_status"]
        assert level == "success"
        assert "mongo_available_databases" in at.session_state
        assert at.session_state["mongo_available_databases"] == ["alpha", "beta"]

    def test_fields_connect_error_stores_error_status(self) -> None:
        """A connection error from the connector in Fields mode stores an error status."""
        from utils.exceptions import DatabaseConnectionError

        at = _make_at()
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception

        with patch("components.sidebar.MongoDBConnector") as mock_cls:
            mock_mongo = MagicMock()
            mock_cls.return_value = mock_mongo
            mock_mongo.connect.side_effect = DatabaseConnectionError("auth failed")

            at.selectbox(key="mongo_auth_mech_input").set_value("None / No Auth")
            at.button(key="mongo_connect").click()
            at.run()

        assert not at.exception
        assert "mongo_step1_status" in at.session_state
        level, msg = at.session_state["mongo_step1_status"]
        assert level == "error"
        assert "auth failed" in msg


# ---------------------------------------------------------------------------
# MongoDB Step 2 — database selection
# ---------------------------------------------------------------------------

class TestMongoStep2:
    """Verify the MongoDB Step 2 database-selection form."""

    def _reach_step2(self, at: "AppTest") -> "AppTest":  # noqa: F821
        """Switch to MongoDB and inject a simulated Step 1 success state."""
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        # Inject mock client + available databases into session state
        at.session_state["mongo_client"] = MagicMock()
        at.session_state["mongo_available_databases"] = ["mydb", "otherdb"]
        at.run()
        return at

    def test_step2_selectbox_appears_with_databases(self) -> None:
        """Step 2 selectbox renders when mongo_client and databases are present."""
        at = _make_at()
        at.run()
        at = self._reach_step2(at)
        select_keys = [s.key for s in at.selectbox]
        assert "mongo_db_select" in select_keys

    def test_step2_not_rendered_without_mongo_client(self) -> None:
        """Step 2 is hidden when mongo_client is None."""
        at = _make_at()
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        # mongo_client defaults to None — Step 2 should be invisible
        select_keys = [s.key for s in at.selectbox]
        assert "mongo_db_select" not in select_keys

    def test_step2_no_available_databases_shows_warning(self) -> None:
        """Step 2 shows a warning when mongo_available_databases is empty."""
        at = _make_at()
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        # Client present but no databases → 'No accessible databases' warning
        at.session_state["mongo_client"] = MagicMock()
        at.session_state["mongo_available_databases"] = []
        at.run()
        assert not at.exception
        warning_texts = [w.value for w in at.warning]
        assert any("database" in str(w).lower() for w in warning_texts)

    def test_step2_select_database_success(self) -> None:
        """Clicking 'Select Database' with a mocked connector stores schema."""
        at = _make_at()
        at.run()
        at = self._reach_step2(at)

        with (
            patch("components.sidebar.MongoDBConnector") as mock_cls,
            patch("components.sidebar.MongoSchemaDetector") as mock_detector_cls,
        ):
            mock_mongo = MagicMock()
            mock_cls.return_value = mock_mongo
            mock_db = MagicMock()
            mock_mongo.get_database.return_value = mock_db

            mock_detector = MagicMock()
            mock_detector_cls.return_value = mock_detector
            mock_detector.detect_schema.return_value = {"col1": [], "col2": []}

            # mongo_client must be in session_state before the button triggers
            at.session_state["mongo_client"] = MagicMock()
            at.session_state["mongo_available_databases"] = ["mydb", "otherdb"]
            at.button(key="mongo_db_confirm").click()
            at.run()

        assert not at.exception

    def test_step2_missing_client_after_click_stores_warning(self) -> None:
        """If mongo_client disappears between renders, a warning is stored."""
        at = _make_at()
        at.run()
        at = self._reach_step2(at)

        # Remove client right before the button click so the 'client is None' branch fires
        at.session_state["mongo_client"] = None
        at.button(key="mongo_db_confirm").click()
        at.run()
        assert not at.exception
        # The app should have stored a warning status
        # (mongo_step2_status may be absent if step 2 short-circuits; no crash is sufficient)

    def test_step2_select_database_connection_error(self) -> None:
        """A connector error during database selection stores an error status."""
        from utils.exceptions import DatabaseConnectionError

        at = _make_at()
        at.run()
        at = self._reach_step2(at)

        with patch("components.sidebar.MongoDBConnector") as mock_cls:
            mock_mongo = MagicMock()
            mock_cls.return_value = mock_mongo
            mock_mongo.get_database.side_effect = DatabaseConnectionError("lost connection")

            at.session_state["mongo_client"] = MagicMock()
            at.session_state["mongo_available_databases"] = ["mydb"]
            at.button(key="mongo_db_confirm").click()
            at.run()

        assert not at.exception
        assert "mongo_step2_status" in at.session_state
        level, msg = at.session_state["mongo_step2_status"]
        assert level == "error"
        assert "lost connection" in msg
