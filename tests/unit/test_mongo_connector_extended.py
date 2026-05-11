"""Extended unit tests for MongoDBConnector — US-066.

Covers previously uncovered lines in mongo_connector.py:
- Lines 14-15: ImportError fallback sets _PYMONGO_AVAILABLE = False
- Line 232:    guard raises DatabaseConnectionError when pymongo missing
- Lines 341-342: client.close() exception swallowed in ServerSelectionTimeoutError handler
- Lines 351-352: client.close() exception swallowed in generic Exception handler
"""
from __future__ import annotations

import sys
import importlib
from unittest.mock import MagicMock, patch

import pytest

from models.config import MongoConfig
from services.mongo_connector import MongoDBConnector
from utils.exceptions import DatabaseConnectionError


def _mongo_cfg() -> MongoConfig:
    """Return a minimal MongoConfig for testing."""
    return MongoConfig(
        host="localhost",
        port=27017,
        username="user",
        password="pass",
        auth_source="admin",
        auth_mechanism="SCRAM-SHA-256",
    )


# ---------------------------------------------------------------------------
# Lines 14-15 — ImportError fallback branch at module load time
# ---------------------------------------------------------------------------


class TestPyMongoUnavailableBranch:
    """Cover lines 14-15: except ImportError sets _PYMONGO_AVAILABLE = False."""

    def test_pymongo_unavailable_import_sets_flag_false(self) -> None:
        """Lines 14-15: reimporting mongo_connector with pymongo blocked."""
        # Save the real module and all pymongo sub-modules from cache
        real_mc = sys.modules.pop("services.mongo_connector", None)
        saved_pymongo = {k: v for k, v in sys.modules.items() if k.startswith("pymongo")}
        for key in saved_pymongo:
            del sys.modules[key]

        try:
            # Sentinel: sys.modules[name] = None causes `import name` to raise ImportError
            sys.modules["pymongo"] = None  # type: ignore[assignment]
            fresh = importlib.import_module("services.mongo_connector")
            available = fresh._PYMONGO_AVAILABLE  # type: ignore[attr-defined]
        finally:
            # Remove the fake-loaded module
            sys.modules.pop("services.mongo_connector", None)
            # Remove the None sentinel
            sys.modules.pop("pymongo", None)
            # Restore all real pymongo sub-modules
            sys.modules.update(saved_pymongo)
            # Restore the real mongo_connector
            if real_mc is not None:
                sys.modules["services.mongo_connector"] = real_mc

        assert available is False


# ---------------------------------------------------------------------------
# Line 232 — pymongo-not-installed guard in connect()
# ---------------------------------------------------------------------------


class TestPyMongoNotAvailableGuard:
    """Cover line 232: connect() raises when _PYMONGO_AVAILABLE is False."""

    def test_connect_raises_when_pymongo_not_available(self) -> None:
        """Line 232: DatabaseConnectionError raised when pymongo is not installed."""
        connector = MongoDBConnector()
        cfg = _mongo_cfg()

        with patch("services.mongo_connector._PYMONGO_AVAILABLE", False):
            with pytest.raises(DatabaseConnectionError, match="pymongo is not installed"):
                connector.connect(cfg)


# ---------------------------------------------------------------------------
# Lines 341-342 — client.close() exception swallowed in ServerSelectionTimeout
# ---------------------------------------------------------------------------


class TestServerSelectionTimeoutClientCleanup:
    """Cover lines 341-342: close() exception inside ServerSelectionTimeoutError handler."""

    def test_close_exception_swallowed_on_server_selection_timeout(self) -> None:
        """Lines 341-342: RuntimeError from client.close() is swallowed; DatabaseConnectionError raised."""
        from pymongo.errors import ServerSelectionTimeoutError

        connector = MongoDBConnector()
        cfg = _mongo_cfg()

        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ServerSelectionTimeoutError("timed out")
        mock_client.close.side_effect = RuntimeError("close also failed")

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError, match="Could not connect"):
                connector.connect(cfg)

        # close() was called and its exception was swallowed (lines 341-342 executed)
        mock_client.close.assert_called_once()

    def test_close_called_when_server_selection_timeout(self) -> None:
        """Lines 338-342: client.close() is called on ServerSelectionTimeoutError even when close succeeds."""
        from pymongo.errors import ServerSelectionTimeoutError

        connector = MongoDBConnector()
        cfg = _mongo_cfg()

        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ServerSelectionTimeoutError("no server")
        # close() succeeds — lines 340-342 still execute (just no inner exception)

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError):
                connector.connect(cfg)

        mock_client.close.assert_called_once()


# ---------------------------------------------------------------------------
# Lines 351-352 — client.close() exception swallowed in generic Exception handler
# ---------------------------------------------------------------------------


class TestGenericExceptionClientCleanup:
    """Cover lines 351-352: close() exception inside generic Exception handler."""

    def test_close_exception_swallowed_on_generic_exception(self) -> None:
        """Lines 351-352: RuntimeError from client.close() is swallowed; DatabaseConnectionError raised."""
        connector = MongoDBConnector()
        cfg = _mongo_cfg()

        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ValueError("unexpected ping error")
        mock_client.close.side_effect = RuntimeError("close also failed")

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError, match="Could not connect"):
                connector.connect(cfg)

        mock_client.close.assert_called_once()

    def test_close_called_when_generic_exception(self) -> None:
        """Lines 348-352: client.close() is called on generic Exception."""
        connector = MongoDBConnector()
        cfg = _mongo_cfg()

        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ConnectionError("network reset")

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError):
                connector.connect(cfg)

        mock_client.close.assert_called_once()
