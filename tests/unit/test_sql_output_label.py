"""Unit tests for SQLOutputComponent dynamic label (US-057 / EPIC-009)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from components.sql_output import SQLOutputComponent


class TestSQLOutputComponentLabel:
    """Tests for the dynamic label / hint text logic in SQLOutputComponent."""

    def setup_method(self) -> None:
        self.component = SQLOutputComponent()

    @staticmethod
    def _make_st_mock() -> MagicMock:
        """Return a MagicMock that records calls to streamlit functions."""
        mock = MagicMock()
        # st.columns returns two context-manager-compatible objects
        col1, col2 = MagicMock(), MagicMock()
        col1.__enter__ = MagicMock(return_value=col1)
        col1.__exit__ = MagicMock(return_value=False)
        col2.__enter__ = MagicMock(return_value=col2)
        col2.__exit__ = MagicMock(return_value=False)
        mock.columns.return_value = [col1, col2]
        mock.session_state = {}
        return mock

    # ── MongoDB label ─────────────────────────────────────────────────────────

    def test_mongodb_shows_generated_mql_subheader(self) -> None:
        """When db_type='MongoDB', subheader must contain 'Generated MQL'."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql='{"collection":"x","pipeline":[]}', db_type="MongoDB")
        call_args = [str(c) for c in st_mock.subheader.call_args_list]
        assert any("Generated MQL" in arg for arg in call_args)

    def test_mongodb_uses_json_language_for_code_block(self) -> None:
        """When db_type='MongoDB', st.code is called with language='json'."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql='{"collection":"x","pipeline":[]}', db_type="MongoDB")
        _, kwargs = st_mock.code.call_args
        assert kwargs.get("language") == "json"

    def test_mongodb_hint_text_references_mql(self) -> None:
        """When db_type='MongoDB', the copy-hint caption mentions 'MQL'."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql='{"collection":"x","pipeline":[]}', db_type="MongoDB")
        # st.caption() is called inside `with col_copy:` which patches st.* calls
        captions = [str(c) for c in st_mock.caption.call_args_list]
        assert any("MQL" in cap for cap in captions)

    def test_mongodb_empty_state_shows_mql_placeholder(self) -> None:
        """When db_type='MongoDB' and sql='', placeholder mentions 'MQL'."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql="", db_type="MongoDB")
        info_calls = [str(c) for c in st_mock.info.call_args_list]
        assert any("MQL" in c for c in info_calls)

    # ── MySQL label ───────────────────────────────────────────────────────────

    def test_mysql_shows_generated_sql_subheader(self) -> None:
        """When db_type='MySQL', subheader must contain 'Generated SQL'."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql="SELECT 1", db_type="MySQL")
        call_args = [str(c) for c in st_mock.subheader.call_args_list]
        assert any("Generated SQL" in arg for arg in call_args)

    def test_mysql_uses_sql_language_for_code_block(self) -> None:
        """When db_type='MySQL', st.code is called with language='sql'."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql="SELECT 1", db_type="MySQL")
        _, kwargs = st_mock.code.call_args
        assert kwargs.get("language") == "sql"

    def test_mysql_empty_state_shows_sql_placeholder(self) -> None:
        """When db_type='MySQL' and sql='', placeholder mentions 'SQL'."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql="", db_type="MySQL")
        info_calls = [str(c) for c in st_mock.info.call_args_list]
        assert any("SQL" in c for c in info_calls)

    # ── Default / backward-compat ─────────────────────────────────────────────

    def test_default_db_type_renders_sql_label(self) -> None:
        """Calling render() without db_type defaults to MySQL/SQL label."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql="SELECT 1")
        call_args = [str(c) for c in st_mock.subheader.call_args_list]
        assert any("Generated SQL" in arg for arg in call_args)

    # ── PostgreSQL ────────────────────────────────────────────────────────────

    def test_postgresql_shows_generated_sql_subheader(self) -> None:
        """PostgreSQL also shows 'Generated SQL' (not MQL)."""
        st_mock = self._make_st_mock()
        with patch("components.sql_output.st", st_mock):
            self.component.render(sql="SELECT 1", db_type="PostgreSQL")
        call_args = [str(c) for c in st_mock.subheader.call_args_list]
        assert any("Generated SQL" in arg for arg in call_args)
