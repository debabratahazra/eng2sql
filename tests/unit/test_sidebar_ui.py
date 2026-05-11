"""Sidebar UI tests using Streamlit AppTest harness (US-038).

Covers widget rendering, db-type switching, connection mode toggling, and
client-side form validation — all without requiring a live database.

Requires Streamlit >= 1.28 (AppTest introduced in 1.28; project pins 1.35+).
"""
from __future__ import annotations

import pytest

APP_PATH = "src/app.py"


# ---------------------------------------------------------------------------
# Tests: default MySQL state
# ---------------------------------------------------------------------------

class TestSidebarDefaultState:
    """Verify the initial render shows MySQL widgets with correct defaults."""

    def test_app_renders_without_exception(self) -> None:
        """Full app renders without raising an exception on first load."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        assert not at.exception

    def test_db_type_radio_defaults_to_mysql(self) -> None:
        """The database-type radio widget defaults to MySQL."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        assert not at.exception
        # First radio in the sidebar is the DB-type selector
        assert at.radio[0].value == "MySQL"

    def test_mysql_connect_button_is_present(self) -> None:
        """MySQL 'Connect' button is rendered when MySQL type is selected."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        assert not at.exception
        button_labels = [b.label for b in at.button]
        assert "Connect" in button_labels

    def test_mysql_empty_credentials_yields_warning(self) -> None:
        """Clicking Connect with empty user/password stores a warning in session state.

        Host defaults to 'localhost', user and password are empty by default.
        ``not all([host, user, password])`` → validation branch fires.
        """
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        # Host defaults to 'localhost', user/password are empty — triggers warning
        at.button(key="mysql_connect").click()
        at.run()
        assert not at.exception
        assert "step1_status" in at.session_state
        level, msg = at.session_state["step1_status"]
        assert level == "warning"
        assert "password" in msg.lower() or "host" in msg.lower() or "user" in msg.lower()


# ---------------------------------------------------------------------------
# Tests: MongoDB mode
# ---------------------------------------------------------------------------

class TestSidebarMongoDBMode:
    """Verify MongoDB sidebar widgets appear after switching the DB-type radio."""

    def test_switch_to_mongodb_updates_session_state(self) -> None:
        """Selecting MongoDB sets db_type='MongoDB' in session state."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        assert at.session_state["db_type"] == "MongoDB"

    def test_mongodb_shows_connection_mode_radio(self) -> None:
        """After switching to MongoDB a 'Connection input mode' radio appears."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        radio_labels = [r.label for r in at.radio]
        assert "Connection input mode" in radio_labels

    def test_mongodb_uri_mode_toggle_updates_session_state(self) -> None:
        """Switching to 'URI + credentials' updates mongo_input_mode in session state."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        at.radio(key="mongo_input_mode_radio").set_value("URI + credentials")
        at.run()
        assert not at.exception
        assert at.session_state["mongo_input_mode"] == "URI + credentials"

    def test_mongodb_fields_mode_is_default(self) -> None:
        """MongoDB connection input mode defaults to 'Fields'."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        # After render, _render_mongo_step1 sets mongo_input_mode in session state
        assert at.session_state["mongo_input_mode"] == "Fields"

    def test_mongodb_empty_credentials_yields_warning(self) -> None:
        """Clicking Connect in MongoDB Fields mode with empty fields stores a warning."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        at.button(key="mongo_connect").click()
        at.run()
        assert not at.exception
        assert "mongo_step1_status" in at.session_state
        level, _msg = at.session_state["mongo_step1_status"]
        assert level == "warning"


# ---------------------------------------------------------------------------
# Tests: switching back from MongoDB to MySQL clears MongoDB state
# ---------------------------------------------------------------------------

class TestSidebarDBTypeSwitching:
    """Verify that switching DB types resets the opposite type's state."""

    def test_switch_to_mongodb_clears_mysql_server_state(self) -> None:
        """Switching from MySQL to MongoDB clears MySQL server connection state.

        The sidebar calls ``_clear_server_state()`` when db_type changes, which
        removes the ``db_server_engine`` and related MySQL keys.
        """
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        # Simulate a connected MySQL state
        at.session_state["db_server_engine"] = "mock_engine"
        at.session_state["available_databases"] = ["mydb"]
        # Switch to MongoDB
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        assert at.session_state["db_type"] == "MongoDB"
        # MySQL server engine must have been cleared — key is popped by _clear_server_state()
        assert "db_server_engine" not in at.session_state or at.session_state["db_server_engine"] is None

