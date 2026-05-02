"""Integration tests for DBConnector — TC-008 through TC-010."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine as _create_engine

from services.db_connector import DBConnector
from utils.exceptions import QueryExecutionError


@pytest.fixture
def connector() -> DBConnector:
    return DBConnector()


@pytest.mark.integration
class TestDBConnectorIntegration:
    """Integration tests using in-memory SQLite engine — TC-008 to TC-010."""

    def test_test_connection_returns_true_for_valid_engine(
        self, connector, sqlite_engine
    ):
        """TC-008: test_connection returns True for a healthy engine."""
        assert connector.test_connection(sqlite_engine) is True

    def test_test_connection_returns_false_for_bad_engine(self, connector):
        """TC-008 variant: test_connection returns False for a dead engine."""
        bad_engine = _create_engine("sqlite:////nonexistent/path/db.sqlite")
        try:
            result = connector.test_connection(bad_engine)
            assert result is False
        finally:
            bad_engine.dispose()

    def test_execute_query_returns_dataframe(self, connector, sqlite_engine):
        """TC-009: Execute a valid SELECT and receive a DataFrame."""
        df = connector.execute_query(sqlite_engine, "SELECT * FROM customers")

        assert len(df) == 2
        assert "name" in df.columns
        assert df.iloc[0]["name"] == "Alice Smith"

    def test_execute_query_filtered_results(self, connector, sqlite_engine):
        """TC-009 variant: Filtered SELECT returns correct subset."""
        df = connector.execute_query(
            sqlite_engine,
            "SELECT * FROM orders WHERE status = 'pending'"
        )
        assert len(df) == 1
        assert df.iloc[0]["status"] == "pending"

    def test_execute_query_raises_on_invalid_sql(self, connector, sqlite_engine):
        """TC-010: Invalid SQL raises QueryExecutionError."""
        with pytest.raises(QueryExecutionError):
            connector.execute_query(sqlite_engine, "SELECT * FROM nonexistent_table_xyz")

    def test_execute_query_raises_on_non_select(self, connector, sqlite_engine):
        """TC-010 variant: Non-SELECT SQL raises ValueError."""
        with pytest.raises(ValueError, match="Only SELECT"):
            connector.execute_query(
                sqlite_engine,
                "DROP TABLE customers"
            )

    def test_execute_query_raises_on_insert(self, connector, sqlite_engine):
        """TC-010 variant: INSERT raises ValueError."""
        with pytest.raises(ValueError, match="Only SELECT"):
            connector.execute_query(
                sqlite_engine,
                "INSERT INTO customers VALUES (99, 'Hacker', 'x@y.com')"
            )
