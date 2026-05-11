"""US-048 - Integration tests for ``DBConnector`` against a real PostgreSQL 16 container.

Mirror of ``test_db_connector_live.py`` for the PostgreSQL dialect (EPIC-009).

Run with::

    pytest tests/integration/test_db_connector_postgres_live.py -m docker -v
"""
from __future__ import annotations

import pandas as pd
import pytest

from models.config import DBConfig
from services.db_connector import DBConnector
from utils.exceptions import DatabaseConnectionError


pytestmark = [pytest.mark.integration, pytest.mark.docker]


class TestDBConnectorLivePostgres:
    """Integration tests against a real PostgreSQL 16 container."""

    def test_create_engine_succeeds_against_real_postgres(
        self, postgres_container: DBConfig
    ) -> None:
        connector = DBConnector()
        engine = connector.create_engine(postgres_container)
        try:
            assert engine is not None
            assert engine.dialect.name == "postgresql"
            assert connector.test_connection(engine) is True
        finally:
            engine.dispose()

    def test_list_databases_filters_template_dbs(
        self, postgres_container: DBConfig
    ) -> None:
        """``list_databases`` excludes ``postgres``, ``template0``, ``template1``."""
        connector = DBConnector()
        engine = connector.create_engine(postgres_container)
        try:
            dbs = connector.list_databases(engine)
            # template0 / template1 / postgres must be filtered out
            assert "template0" not in dbs
            assert "template1" not in dbs
            assert "postgres" not in dbs
            # The user-created DB should be visible
            assert postgres_container.database in dbs
        finally:
            engine.dispose()

    def test_execute_query_returns_dataframe(
        self, postgres_container: DBConfig
    ) -> None:
        connector = DBConnector()
        engine = connector.create_engine(postgres_container)
        try:
            df = connector.execute_query(engine, "SELECT 1 AS one, 2 AS two")
            assert isinstance(df, pd.DataFrame)
            assert df.shape == (1, 2)
            assert int(df.iloc[0]["one"]) == 1
            assert int(df.iloc[0]["two"]) == 2
        finally:
            engine.dispose()

    def test_invalid_credentials_raise_connection_error(
        self, postgres_container: DBConfig
    ) -> None:
        bad_config = DBConfig(
            host=postgres_container.host,
            port=postgres_container.port,
            user="nonexistent_user",
            password="wrong_password",
            database=postgres_container.database,
            dialect="postgresql",
            sslmode="disable",
        )
        connector = DBConnector()
        with pytest.raises(DatabaseConnectionError):
            engine = connector.create_engine(bad_config)
            connector.test_connection(engine)
