"""Unit tests for DBConnector dialect dispatch (EPIC-009 / US-046).

Covers TC-046: list_databases dispatches on engine.dialect.name and filters
PostgreSQL system / template databases.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from services.db_connector import DBConnector


def _mock_engine(rows: list[tuple[str]], dialect_name: str) -> MagicMock:
    mock_result = MagicMock()
    mock_result.fetchall.return_value = rows

    mock_conn = MagicMock()
    mock_conn.execute.return_value = mock_result
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    mock_engine.dialect.name = dialect_name
    return mock_engine


class TestPostgreSQLDispatch:
    """list_databases() under PostgreSQL dialect."""

    def test_filters_postgres_system_databases(self) -> None:
        rows = [
            ("postgres",),
            ("template0",),
            ("template1",),
            ("app_db",),
            ("analytics",),
        ]
        engine = _mock_engine(rows, dialect_name="postgresql")
        result = DBConnector().list_databases(engine)
        assert result == ["analytics", "app_db"]

    def test_uses_pg_database_query(self) -> None:
        engine = _mock_engine([("app_db",)], dialect_name="postgresql")
        DBConnector().list_databases(engine)
        # The first positional arg to execute() is a TextClause; render to str
        called_text = str(engine.connect.return_value.execute.call_args[0][0])
        assert "pg_database" in called_text
        assert "datistemplate" in called_text


class TestUnknownDialect:
    def test_unknown_dialect_raises_not_implemented(self) -> None:
        engine = _mock_engine([], dialect_name="oracle")
        with pytest.raises(NotImplementedError, match="oracle"):
            DBConnector().list_databases(engine)
