"""Extended unit tests for DBConnector — US-065.

Covers the previously uncovered lines in db_connector.py:
- Lines 84-86: OperationalError handler in create_engine
- Lines 88-90: SQLAlchemyError handler in create_engine
- Lines 110-115: test_connection method (True and False paths)
- Lines 133-149: execute_query method (success, ValueError, QueryExecutionError)
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from models.config import DBConfig
from services.db_connector import DBConnector
from utils.exceptions import DatabaseConnectionError, QueryExecutionError


def _mysql_config(**overrides: object) -> DBConfig:
    """Return a minimal MySQL DBConfig for testing."""
    base: dict[str, object] = {
        "host": "db.example.com",
        "port": 3306,
        "user": "app_user",
        "password": "s3cr3t",
        "database": "app_db",
        "dialect": "mysql",
    }
    base.update(overrides)
    return DBConfig(**base)  # type: ignore[arg-type]


def _mock_engine_ok() -> MagicMock:
    """Return a mock SQLAlchemy engine whose connect() works."""
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_eng = MagicMock()
    mock_eng.connect.return_value = mock_conn
    return mock_eng


# ---------------------------------------------------------------------------
# create_engine — exception paths (lines 84, 88)
# ---------------------------------------------------------------------------


class TestCreateEngineExceptionPaths:
    """create_engine error-handling branches not covered by existing tests."""

    def test_operational_error_raises_database_connection_error(self) -> None:
        """Lines 84-86: OperationalError from connect() is wrapped as DatabaseConnectionError."""
        cfg = _mysql_config()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.side_effect = OperationalError(
            "connection refused", None, None
        )
        mock_eng = MagicMock()
        mock_eng.connect.return_value = mock_conn

        with patch("services.db_connector.create_engine", return_value=mock_eng):
            with pytest.raises(DatabaseConnectionError, match="Could not connect"):
                DBConnector().create_engine(cfg)

    def test_sqlalchemy_error_raises_database_connection_error(self) -> None:
        """Lines 88-90: Generic SQLAlchemyError is wrapped as DatabaseConnectionError."""
        cfg = _mysql_config()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.side_effect = SQLAlchemyError("generic db error")
        mock_eng = MagicMock()
        mock_eng.connect.return_value = mock_conn

        with patch("services.db_connector.create_engine", return_value=mock_eng):
            with pytest.raises(DatabaseConnectionError, match="Database error during connection"):
                DBConnector().create_engine(cfg)

    def test_create_engine_success_returns_engine(self) -> None:
        """Baseline: successful create_engine returns the engine object."""
        cfg = _mysql_config()
        mock_eng = _mock_engine_ok()

        with patch("services.db_connector.create_engine", return_value=mock_eng):
            result = DBConnector().create_engine(cfg)

        assert result is mock_eng


# ---------------------------------------------------------------------------
# test_connection — lines 110-115
# ---------------------------------------------------------------------------


class TestTestConnection:
    """Unit tests for DBConnector.test_connection (lines 110-115)."""

    def test_returns_true_when_query_succeeds(self) -> None:
        """Lines 110-113: True when SELECT 1 executes without error."""
        mock_eng = _mock_engine_ok()
        result = DBConnector().test_connection(mock_eng)
        assert result is True

    def test_returns_false_when_sqlalchemy_error(self) -> None:
        """Lines 114-115: False when SQLAlchemyError is raised during connect."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.side_effect = SQLAlchemyError("timed out")
        mock_eng = MagicMock()
        mock_eng.connect.return_value = mock_conn

        result = DBConnector().test_connection(mock_eng)
        assert result is False

    def test_returns_false_when_connect_raises(self) -> None:
        """Lines 114-115: False when engine.connect() itself raises."""
        mock_eng = MagicMock()
        mock_eng.connect.side_effect = SQLAlchemyError("no route to host")

        result = DBConnector().test_connection(mock_eng)
        assert result is False


# ---------------------------------------------------------------------------
# execute_query — lines 133-149
# ---------------------------------------------------------------------------


class TestExecuteQuery:
    """Unit tests for DBConnector.execute_query (lines 133-149)."""

    def _make_engine_with_rows(
        self,
        rows: list[tuple],
        col_names: list[str],
    ) -> MagicMock:
        """Return a mock engine whose query returns the given rows and columns."""
        mock_result = MagicMock()
        mock_result.fetchall.return_value = rows
        mock_result.keys.return_value = col_names

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.return_value = mock_result

        mock_eng = MagicMock()
        mock_eng.connect.return_value = mock_conn
        return mock_eng

    def test_select_returns_dataframe(self) -> None:
        """Lines 133-145: Valid SELECT returns a populated DataFrame."""
        rows = [("Alice", 30), ("Bob", 25)]
        mock_eng = self._make_engine_with_rows(rows, ["name", "age"])

        df = DBConnector().execute_query(mock_eng, "SELECT name, age FROM users")

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["name", "age"]
        assert len(df) == 2
        assert df.iloc[0]["name"] == "Alice"

    def test_select_empty_result_returns_empty_dataframe(self) -> None:
        """Lines 133-145: Empty result set returns empty DataFrame (not None)."""
        mock_eng = self._make_engine_with_rows([], ["id", "name"])

        df = DBConnector().execute_query(mock_eng, "SELECT id, name FROM t WHERE 1=0")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_non_select_raises_value_error(self) -> None:
        """Lines 133-138: Non-SELECT statement raises ValueError."""
        mock_eng = _mock_engine_ok()

        with pytest.raises(ValueError, match="Only SELECT statements"):
            DBConnector().execute_query(mock_eng, "DROP TABLE users")

    def test_insert_raises_value_error(self) -> None:
        """Lines 133-138: INSERT statement raises ValueError."""
        mock_eng = _mock_engine_ok()

        with pytest.raises(ValueError, match="Only SELECT statements"):
            DBConnector().execute_query(mock_eng, "INSERT INTO t VALUES (1)")

    def test_sqlalchemy_error_raises_query_execution_error(self) -> None:
        """Lines 146-149: SQLAlchemyError during query is wrapped as QueryExecutionError."""
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.side_effect = SQLAlchemyError("syntax error near SELECT")
        mock_eng = MagicMock()
        mock_eng.connect.return_value = mock_conn

        with pytest.raises(QueryExecutionError, match="Query execution failed"):
            DBConnector().execute_query(mock_eng, "SELECT bad_col FROM nonexistent")

    def test_whitespace_padded_select_accepted(self) -> None:
        """Lines 133-145: SELECT with leading whitespace is accepted."""
        rows = [(1,)]
        mock_eng = self._make_engine_with_rows(rows, ["id"])

        df = DBConnector().execute_query(mock_eng, "  SELECT id FROM t  ")

        assert len(df) == 1
