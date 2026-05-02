"""Unit tests for DBConnector.list_databases() — US-024 / TC-019."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

from services.db_connector import DBConnector
from utils.exceptions import DatabaseConnectionError


@pytest.fixture
def connector() -> DBConnector:
    """Return a fresh DBConnector instance."""
    return DBConnector()


def _mock_engine(rows: list[tuple[str]]) -> MagicMock:
    """Return a MagicMock engine whose SHOW DATABASES returns *rows*."""
    mock_result = MagicMock()
    mock_result.fetchall.return_value = rows

    mock_conn = MagicMock()
    mock_conn.execute.return_value = mock_result
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    return mock_engine


class TestListDatabases:
    """Unit tests for DBConnector.list_databases() — TC-019."""

    def test_filters_system_databases(self, connector: DBConnector) -> None:
        """TC-019-01: System databases are excluded from the result."""
        rows: list[tuple[str]] = [
            ("information_schema",),
            ("performance_schema",),
            ("mysql",),
            ("sys",),
            ("myapp_db",),
            ("analytics_db",),
        ]
        result = connector.list_databases(_mock_engine(rows))
        assert "information_schema" not in result
        assert "performance_schema" not in result
        assert "mysql" not in result
        assert "sys" not in result

    def test_returns_user_databases(self, connector: DBConnector) -> None:
        """TC-019-02: Non-system databases appear in the result."""
        rows: list[tuple[str]] = [
            ("information_schema",),
            ("myapp_db",),
            ("analytics_db",),
        ]
        result = connector.list_databases(_mock_engine(rows))
        assert "myapp_db" in result
        assert "analytics_db" in result

    def test_result_is_sorted(self, connector: DBConnector) -> None:
        """TC-019-03: Results are returned in alphabetical order."""
        rows: list[tuple[str]] = [
            ("zebra_db",),
            ("alpha_db",),
            ("mysql",),
            ("middle_db",),
        ]
        result = connector.list_databases(_mock_engine(rows))
        assert result == sorted(result)
        assert result == ["alpha_db", "middle_db", "zebra_db"]

    def test_returns_empty_list_when_only_system_databases(
        self, connector: DBConnector
    ) -> None:
        """TC-019-04: Empty list when only system databases are visible."""
        rows: list[tuple[str]] = [
            ("information_schema",),
            ("performance_schema",),
            ("mysql",),
            ("sys",),
        ]
        result = connector.list_databases(_mock_engine(rows))
        assert result == []

    def test_returns_empty_list_for_empty_result(
        self, connector: DBConnector
    ) -> None:
        """TC-019-05: Empty list when SHOW DATABASES returns no rows."""
        result = connector.list_databases(_mock_engine([]))
        assert result == []

    def test_single_user_database(self, connector: DBConnector) -> None:
        """TC-019-06: Single non-system database is returned correctly."""
        rows: list[tuple[str]] = [("information_schema",), ("my_only_db",)]
        result = connector.list_databases(_mock_engine(rows))
        assert result == ["my_only_db"]

    def test_wraps_sqlalchemy_error_as_database_connection_error(
        self, connector: DBConnector
    ) -> None:
        """TC-019-07: SQLAlchemyError is wrapped as DatabaseConnectionError."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.side_effect = SQLAlchemyError("connection refused")

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with pytest.raises(DatabaseConnectionError, match="Failed to list databases"):
            connector.list_databases(mock_engine)

    def test_error_message_contains_original_cause(
        self, connector: DBConnector
    ) -> None:
        """TC-019-08: DatabaseConnectionError message includes original cause."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.side_effect = SQLAlchemyError("Access denied")

        mock_engine = MagicMock()
        mock_engine.connect.return_value = mock_conn

        with pytest.raises(DatabaseConnectionError, match="Access denied"):
            connector.list_databases(mock_engine)
