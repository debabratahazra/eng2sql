"""Unit tests for DBConnector PostgreSQL ``create_engine`` happy path (US-055).

Covers TC-055 — pure-mock unit coverage that lifts ``db_connector.py``
coverage above 90 % even when Docker integration tests are skipped.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from models.config import DBConfig
from services.db_connector import DBConnector
from utils.exceptions import DatabaseConnectionError


def _config(**overrides: object) -> DBConfig:
    base: dict[str, object] = {
        "host": "pg.example.com",
        "port": 5432,
        "user": "alice",
        "password": "secret",
        "database": "appdb",
        "dialect": "postgresql",
        "sslmode": "prefer",
    }
    base.update(overrides)
    return DBConfig(**base)  # type: ignore[arg-type]


class TestPostgreSQLCreateEngine:
    """``create_engine`` happy path with PostgreSQL config."""

    def test_create_engine_uses_postgresql_url_and_sslmode(self) -> None:
        cfg = _config()
        with patch("services.db_connector.create_engine") as mock_ce:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_engine.connect.return_value = mock_conn
            mock_ce.return_value = mock_engine

            engine = DBConnector().create_engine(cfg)

        assert engine is mock_engine
        url_passed = mock_ce.call_args.args[0]
        assert url_passed.startswith("postgresql+psycopg://alice:")
        assert "sslmode=prefer" in url_passed

    def test_create_engine_propagates_disable_sslmode(self) -> None:
        cfg = _config(sslmode="disable")
        with patch("services.db_connector.create_engine") as mock_ce:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_conn.__enter__ = MagicMock(return_value=mock_conn)
            mock_conn.__exit__ = MagicMock(return_value=False)
            mock_engine.connect.return_value = mock_conn
            mock_ce.return_value = mock_engine

            DBConnector().create_engine(cfg)

        url_passed = mock_ce.call_args.args[0]
        assert "sslmode=disable" in url_passed

    def test_postgresql_system_databases_excluded(self) -> None:
        from services.db_connector import _SYSTEM_DATABASES

        for sysdb in ("postgres", "template0", "template1"):
            assert sysdb in _SYSTEM_DATABASES

    def test_create_engine_wsl2_loopback_guard_when_unreachable(self) -> None:
        cfg = _config(host="localhost")
        with patch("services.db_connector.is_wsl2", return_value=True):
            with patch(
                "services.db_connector.probe_reachable_host",
                return_value="localhost",
            ):
                with pytest.raises(DatabaseConnectionError, match="WSL2"):
                    DBConnector().create_engine(cfg)

    def test_create_engine_skips_wsl2_guard_when_not_loopback(self) -> None:
        cfg = _config(host="pg.example.com")
        with patch("services.db_connector.is_wsl2", return_value=True) as mock_wsl:
            with patch("services.db_connector.create_engine") as mock_ce:
                mock_engine = MagicMock()
                mock_conn = MagicMock()
                mock_conn.__enter__ = MagicMock(return_value=mock_conn)
                mock_conn.__exit__ = MagicMock(return_value=False)
                mock_engine.connect.return_value = mock_conn
                mock_ce.return_value = mock_engine

                DBConnector().create_engine(cfg)
        # is_wsl2 not consulted for non-loopback hosts
        mock_wsl.assert_not_called()

    def test_create_engine_skips_wsl2_guard_when_not_wsl2(self) -> None:
        cfg = _config(host="localhost")
        with patch("services.db_connector.is_wsl2", return_value=False):
            with patch(
                "services.db_connector.probe_reachable_host"
            ) as mock_probe:
                with patch("services.db_connector.create_engine") as mock_ce:
                    mock_engine = MagicMock()
                    mock_conn = MagicMock()
                    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
                    mock_conn.__exit__ = MagicMock(return_value=False)
                    mock_engine.connect.return_value = mock_conn
                    mock_ce.return_value = mock_engine

                    DBConnector().create_engine(cfg)
        # When not WSL2, we never probe.
        mock_probe.assert_not_called()
