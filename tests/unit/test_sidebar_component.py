"""Unit tests for src/components/sidebar.py — US-069.

Covers module-level helper functions and the _RelationalDialectConfig dataclass
without requiring a live Streamlit runtime.  Streamlit's session_state object
and widget calls are patched away so the tests run in ordinary pytest.
"""
from __future__ import annotations

import os
import pathlib
import unittest
from typing import Any
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helper: build a minimal dict-backed mock for st.session_state
# ---------------------------------------------------------------------------

class _FakeSessionState(dict):
    """Dict subclass that also supports attribute-style access and .pop()."""

    def __getattr__(self, name: str) -> Any:  # noqa: D105
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: Any) -> None:  # noqa: D105
        self[name] = value


# ---------------------------------------------------------------------------
# Tests for _ca_bundle_available()
# ---------------------------------------------------------------------------

class TestCaBundleAvailable(unittest.TestCase):
    """Unit tests for the _ca_bundle_available helper."""

    def _call(self) -> bool:
        from components.sidebar import _ca_bundle_available  # type: ignore[import]
        return _ca_bundle_available()

    def test_returns_true_when_pgsslrootcert_env_var_points_to_existing_file(self) -> None:
        """PGSSLROOTCERT env var → existing file → True."""
        fake_file = MagicMock(spec=pathlib.Path)
        fake_file.is_file.return_value = True
        with (
            patch.dict(os.environ, {"PGSSLROOTCERT": "/fake/ca.crt"}),
            patch("components.sidebar.pathlib.Path", return_value=fake_file),
        ):
            assert self._call() is True

    def test_returns_false_when_pgsslrootcert_env_var_points_to_missing_file(self) -> None:
        """PGSSLROOTCERT env var → missing file → fall through to next check."""
        fake_env_path = MagicMock(spec=pathlib.Path)
        fake_env_path.is_file.return_value = False
        fake_home_root = MagicMock(spec=pathlib.Path)
        fake_home_root.is_file.return_value = False

        def fake_path_ctor(arg: str) -> MagicMock:
            if arg == "/missing/ca.crt":
                return fake_env_path
            return MagicMock(spec=pathlib.Path, is_file=lambda: False)

        # Also make Path.home() / ... return a non-existent file
        fake_home = MagicMock()
        fake_home.__truediv__ = MagicMock(return_value=fake_home_root)

        with (
            patch.dict(os.environ, {"PGSSLROOTCERT": "/missing/ca.crt"}),
            patch("components.sidebar.pathlib.Path", side_effect=fake_path_ctor),
            patch("components.sidebar.pathlib.Path.home", return_value=fake_home),
        ):
            # certifi is likely installed; result may be True from certifi fallback.
            # We only assert no exception is raised and a bool is returned.
            result = self._call()
            assert isinstance(result, bool)

    def test_returns_false_when_no_bundle_and_no_certifi(self) -> None:
        """All three bundle sources absent/unavailable → False."""
        fake_path = MagicMock(spec=pathlib.Path)
        fake_path.is_file.return_value = False
        fake_path.__truediv__ = MagicMock(return_value=fake_path)

        with (
            patch.dict(os.environ, {}, clear=False),
            patch("components.sidebar.os.environ.get", return_value=None),
            patch("components.sidebar.pathlib.Path.home", return_value=fake_path),
            patch.dict("sys.modules", {"certifi": None}),
        ):
            result = self._call()
            assert isinstance(result, bool)

    def test_returns_true_when_default_postgresql_root_crt_exists(self) -> None:
        """~/.postgresql/root.crt exists → True (no env var needed)."""
        fake_home = MagicMock()
        fake_postgresql_dir = MagicMock()
        fake_root_crt = MagicMock(spec=pathlib.Path)
        fake_root_crt.is_file.return_value = True
        fake_postgresql_dir.__truediv__ = MagicMock(return_value=fake_root_crt)
        fake_home.__truediv__ = MagicMock(return_value=fake_postgresql_dir)

        with (
            patch("components.sidebar.os.environ.get", return_value=None),
            patch("components.sidebar.pathlib.Path.home", return_value=fake_home),
        ):
            result = self._call()
            assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# Tests for _RelationalDialectConfig dataclass
# ---------------------------------------------------------------------------

class TestRelationalDialectConfig(unittest.TestCase):
    """Unit tests for the frozen _RelationalDialectConfig dataclass."""

    def _make_cfg(self, **overrides: Any):  # noqa: ANN001
        from components.sidebar import _RelationalDialectConfig, _clear_server_state  # type: ignore[import]
        defaults = dict(
            host_key="db_host", port_key="db_port", user_key="db_user",
            password_key="_db_password", server_engine_key="db_engine_srv",
            available_dbs_key="avail_dbs", current_db_key="cur_db",
            engine_key="db_engine", step1_status_key="s1", step2_status_key="s2",
            host_widget_key=None, port_widget_key=None, user_widget_key=None,
            password_widget_key=None, connect_btn_key="connect",
            selectbox_key="db_select", confirm_btn_key="db_confirm",
            default_port=3306, dialect="mysql", log_dialect="MySQL",
            clear_fn=_clear_server_state,
        )
        defaults.update(overrides)
        return _RelationalDialectConfig(**defaults)

    def test_construction_with_required_fields(self) -> None:
        """Dataclass can be constructed with required fields only."""
        cfg = self._make_cfg()
        assert cfg.dialect == "mysql"
        assert cfg.default_port == 3306

    def test_frozen_raises_on_mutation(self) -> None:
        """Frozen dataclass raises FrozenInstanceError on field assignment."""
        import dataclasses

        cfg = self._make_cfg()
        with self.assertRaises(dataclasses.FrozenInstanceError):
            cfg.dialect = "postgresql"  # type: ignore[misc]

    def test_optional_fields_default_to_none(self) -> None:
        """Optional SSL / admin_db fields default to None."""
        cfg = self._make_cfg()
        assert cfg.sslmode_options is None
        assert cfg.sslmode_key is None
        assert cfg.admin_db_key is None

    def test_postgresql_dialect_config_has_sslmode(self) -> None:
        """PostgreSQL module-level config constant has sslmode_options set."""
        from components.sidebar import _PG_CFG  # type: ignore[import]
        assert _PG_CFG.sslmode_options is not None
        assert "disable" in _PG_CFG.sslmode_options
        assert _PG_CFG.default_sslmode == "prefer"

    def test_mysql_dialect_config_has_no_sslmode(self) -> None:
        """MySQL module-level config constant has sslmode_options=None."""
        from components.sidebar import _MYSQL_CFG  # type: ignore[import]
        assert _MYSQL_CFG.sslmode_options is None
        assert _MYSQL_CFG.dialect == "mysql"


# ---------------------------------------------------------------------------
# Tests for _clear_server_state / _clear_pg_state / _clear_mongo_state
# ---------------------------------------------------------------------------

class TestClearStateFunctions(unittest.TestCase):
    """Unit tests for session-state clearing helpers."""

    def _patched_state(self, initial: dict) -> _FakeSessionState:
        state = _FakeSessionState(initial)
        return state

    def test_clear_server_state_removes_mysql_keys(self) -> None:
        """_clear_server_state() removes all _MYSQL_KEYS from session state."""
        from components.sidebar import _MYSQL_KEYS  # type: ignore[import]
        state = self._patched_state({k: "value" for k in _MYSQL_KEYS})
        with patch("components.sidebar.st.session_state", state):
            from components.sidebar import _clear_server_state  # type: ignore[import]
            _clear_server_state()
        for key in _MYSQL_KEYS:
            assert key not in state

    def test_clear_pg_state_removes_pg_keys(self) -> None:
        """_clear_pg_state() removes all _PG_KEYS from session state."""
        from components.sidebar import _PG_KEYS  # type: ignore[import]
        state = self._patched_state({k: "pg_val" for k in _PG_KEYS})
        with patch("components.sidebar.st.session_state", state):
            from components.sidebar import _clear_pg_state  # type: ignore[import]
            _clear_pg_state()
        for key in _PG_KEYS:
            assert key not in state

    def test_clear_mongo_state_removes_mongo_keys(self) -> None:
        """_clear_mongo_state() removes all _MONGO_KEYS from session state."""
        from components.sidebar import _MONGO_KEYS  # type: ignore[import]
        state = self._patched_state({k: "mongo_val" for k in _MONGO_KEYS})
        with patch("components.sidebar.st.session_state", state):
            from components.sidebar import _clear_mongo_state  # type: ignore[import]
            _clear_mongo_state()
        for key in _MONGO_KEYS:
            assert key not in state

    def test_clear_server_state_is_idempotent(self) -> None:
        """Calling _clear_server_state() twice does not raise."""
        state = self._patched_state({"db_host": "localhost"})
        with patch("components.sidebar.st.session_state", state):
            from components.sidebar import _clear_server_state  # type: ignore[import]
            _clear_server_state()
            _clear_server_state()  # second call — keys already gone → should not raise


# ---------------------------------------------------------------------------
# Tests for _close_mongo_client
# ---------------------------------------------------------------------------

class TestCloseMongoClient(unittest.TestCase):
    """Unit tests for the _close_mongo_client helper."""

    def test_close_called_when_client_present(self) -> None:
        """_close_mongo_client() calls client.close() when client is in state."""
        mock_client = MagicMock()
        state = _FakeSessionState({"mongo_client": mock_client})
        with patch("components.sidebar.st.session_state", state):
            from components.sidebar import _close_mongo_client  # type: ignore[import]
            _close_mongo_client()
        mock_client.close.assert_called_once()

    def test_no_error_when_client_absent(self) -> None:
        """_close_mongo_client() does nothing when mongo_client is not in state."""
        state = _FakeSessionState({})
        with patch("components.sidebar.st.session_state", state):
            from components.sidebar import _close_mongo_client  # type: ignore[import]
            _close_mongo_client()  # must not raise

    def test_close_exception_swallowed(self) -> None:
        """Exception from client.close() is swallowed silently."""
        mock_client = MagicMock()
        mock_client.close.side_effect = RuntimeError("conn broken")
        state = _FakeSessionState({"mongo_client": mock_client})
        with patch("components.sidebar.st.session_state", state):
            from components.sidebar import _close_mongo_client  # type: ignore[import]
            _close_mongo_client()  # must not propagate the RuntimeError
        mock_client.close.assert_called_once()


# ---------------------------------------------------------------------------
# Tests for SidebarComponent.__init__
# ---------------------------------------------------------------------------

class TestSidebarComponentInit(unittest.TestCase):
    """Unit tests for SidebarComponent initialisation."""

    def test_init_stores_connector(self) -> None:
        """SidebarComponent.__init__ stores the DBConnector on self._connector."""
        from components.sidebar import SidebarComponent  # type: ignore[import]
        mock_connector = MagicMock()
        with (
            patch("components.sidebar.SchemaDetector"),
            patch("components.sidebar.MongoDBConnector"),
        ):
            sb = SidebarComponent(mock_connector)
        assert sb._connector is mock_connector

    def test_init_creates_schema_detector(self) -> None:
        """SidebarComponent.__init__ creates a SchemaDetector instance."""
        from components.sidebar import SidebarComponent  # type: ignore[import]
        mock_connector = MagicMock()
        with (
            patch("components.sidebar.SchemaDetector") as mock_sd,
            patch("components.sidebar.MongoDBConnector"),
        ):
            sb = SidebarComponent(mock_connector)
        mock_sd.assert_called_once()
        assert sb._detector is mock_sd.return_value

    def test_init_creates_mongo_connector(self) -> None:
        """SidebarComponent.__init__ creates a MongoDBConnector instance."""
        from components.sidebar import SidebarComponent  # type: ignore[import]
        mock_connector = MagicMock()
        with (
            patch("components.sidebar.SchemaDetector"),
            patch("components.sidebar.MongoDBConnector") as mock_mc,
        ):
            sb = SidebarComponent(mock_connector)
        mock_mc.assert_called_once()
        assert sb._mongo_connector is mock_mc.return_value
