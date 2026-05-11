"""US-042 — Integration tests for ``DBConnector`` against a real MySQL 8 container.

These tests exercise the live-MySQL branches of
:class:`src.services.db_connector.DBConnector` that mock-based unit tests
cannot cover (pymysql connection handshake, real ``information_schema``
queries, real ``DataFrame`` round-trip).

Tests are gated behind two markers:
- ``@pytest.mark.integration`` — skipped by the default unit-test invocation
  (``pytest -m "not integration"``).
- ``@pytest.mark.docker`` — additionally signals that a running Docker
  daemon is required; the ``mysql_container`` fixture skips automatically
  when Docker is unavailable.

Run with::

    pytest tests/integration/test_db_connector_live.py -m docker -v

References:
    - US-042 (Sprint 9) — Docker-based MySQL integration fixture.
    - SPRINT-8-retro.md Action Item 3.
    - tests/conftest.py — ``mysql_container`` session fixture.
"""
from __future__ import annotations

import pandas as pd
import pytest

from models.config import DBConfig
from services.db_connector import DBConnector
from utils.exceptions import DatabaseConnectionError


pytestmark = [pytest.mark.integration, pytest.mark.docker]


class TestDBConnectorLiveMySQL:
    """Integration tests against a real MySQL 8 container."""

    def test_create_engine_succeeds_against_real_mysql(
        self, mysql_container: DBConfig
    ) -> None:
        """``create_engine`` returns a working SQLAlchemy engine."""
        connector = DBConnector()
        engine = connector.create_engine(mysql_container)
        try:
            assert engine is not None
            # A trivial ping confirms the handshake completed
            assert connector.test_connection(engine) is True
        finally:
            engine.dispose()

    def test_list_databases_includes_system_dbs(
        self, mysql_container: DBConfig
    ) -> None:
        """``list_databases`` returns at least the MySQL system databases.

        A fresh ``mysql:8.0`` container always exposes ``information_schema``
        and ``mysql``; the ``testdb`` database created via
        ``MYSQL_DATABASE=testdb`` should also appear.
        """
        connector = DBConnector()
        engine = connector.create_engine(mysql_container)
        try:
            dbs = connector.list_databases(engine)
            assert "information_schema" in dbs
            # The user-created DB should be visible
            assert mysql_container.database in dbs
        finally:
            engine.dispose()

    def test_execute_query_returns_dataframe(
        self, mysql_container: DBConfig
    ) -> None:
        """``execute_query`` returns a non-empty :class:`pandas.DataFrame`."""
        connector = DBConnector()
        engine = connector.create_engine(mysql_container)
        try:
            df = connector.execute_query(engine, "SELECT 1 AS one, 2 AS two")
            assert isinstance(df, pd.DataFrame)
            assert df.shape == (1, 2)
            assert int(df.iloc[0]["one"]) == 1
            assert int(df.iloc[0]["two"]) == 2
        finally:
            engine.dispose()

    def test_invalid_credentials_raise_connection_error(
        self, mysql_container: DBConfig
    ) -> None:
        """Bad credentials surface as :class:`DatabaseConnectionError`.

        Uses the live container's host/port but supplies a bogus user so the
        real pymysql authentication path is exercised.
        """
        bad_config = DBConfig(
            host=mysql_container.host,
            port=mysql_container.port,
            user="nonexistent_user",
            password="wrong_password",
            database=mysql_container.database,
        )
        connector = DBConnector()
        with pytest.raises(DatabaseConnectionError):
            engine = connector.create_engine(bad_config)
            # create_engine may be lazy in SQLAlchemy — force a real connection
            connector.test_connection(engine)
