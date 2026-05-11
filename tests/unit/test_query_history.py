"""Unit tests for query_history component pure helpers (US-085/087/089 / EPIC-017/018/019)."""
from __future__ import annotations

import pytest

from components.query_history import (
    _MAX_ENTRIES,
    _TRUNCATE_LEN,
    _append_to_history,
    _db_type_badge,
    _db_type_to_lang,
    _truncate,
)


class TestAppendToHistory:
    """Tests for _append_to_history()."""

    def test_empty_history_gets_first_entry(self) -> None:
        """Appending to an empty list returns a single-item list."""
        result = _append_to_history([], "q1", "SELECT 1")
        assert result == [{"question": "q1", "sql": "SELECT 1", "db_type": "MySQL"}]

    def test_new_entry_prepended_at_index_zero(self) -> None:
        """Most-recent entry is always at index 0."""
        existing = [{"question": "old q", "sql": "SELECT 0", "db_type": "MySQL"}]
        result = _append_to_history(existing, "new q", "SELECT 1", db_type="PostgreSQL")
        assert result[0] == {"question": "new q", "sql": "SELECT 1", "db_type": "PostgreSQL"}
        assert result[1] == {"question": "old q", "sql": "SELECT 0", "db_type": "MySQL"}

    def test_duplicate_question_is_deduplicated(self) -> None:
        """Re-submitting the same question removes the old entry."""
        existing = [
            {"question": "q1", "sql": "SELECT 1", "db_type": "MySQL"},
            {"question": "q2", "sql": "SELECT 2", "db_type": "MySQL"},
        ]
        result = _append_to_history(existing, "q1", "SELECT 99")
        # q1 should appear once only, at the front
        assert result[0] == {"question": "q1", "sql": "SELECT 99", "db_type": "MySQL"}
        questions = [h["question"] for h in result]
        assert questions.count("q1") == 1

    def test_list_capped_at_max_entries(self) -> None:
        """History list is capped at max_entries (default 10)."""
        history: list[dict[str, str]] = [
            {"question": f"q{i}", "sql": f"SELECT {i}", "db_type": "MySQL"} for i in range(10)
        ]
        result = _append_to_history(history, "new_q", "SELECT 99")
        assert len(result) == _MAX_ENTRIES

    def test_custom_max_entries_respected(self) -> None:
        """Custom max_entries parameter limits the list length."""
        history: list[dict[str, str]] = [
            {"question": f"q{i}", "sql": f"SELECT {i}", "db_type": "MySQL"} for i in range(5)
        ]
        result = _append_to_history(history, "new_q", "SELECT 99", max_entries=3)
        assert len(result) == 3

    def test_max_entries_one_returns_only_latest(self) -> None:
        """max_entries=1 keeps only the most-recent entry."""
        history = [{"question": "old", "sql": "SELECT 0", "db_type": "MySQL"}]
        result = _append_to_history(history, "new", "SELECT 1", max_entries=1)
        assert result == [{"question": "new", "sql": "SELECT 1", "db_type": "MySQL"}]

    def test_original_history_not_mutated(self) -> None:
        """The input list is not modified in place."""
        original = [{"question": "q1", "sql": "SELECT 1", "db_type": "MySQL"}]
        original_copy = list(original)
        _append_to_history(original, "q2", "SELECT 2")
        assert original == original_copy

    def test_returns_list_of_dicts(self) -> None:
        """Return type is a list of dicts with question, sql, and db_type keys."""
        result = _append_to_history([], "q", "SELECT 1", db_type="PostgreSQL")
        assert isinstance(result, list)
        assert "question" in result[0]
        assert "sql" in result[0]
        assert result[0]["db_type"] == "PostgreSQL"

    def test_order_preserved_for_existing_entries(self) -> None:
        """Existing entries retain their relative order after prepend."""
        history = [
            {"question": "a", "sql": "SELECT 1", "db_type": "MySQL"},
            {"question": "b", "sql": "SELECT 2", "db_type": "MySQL"},
            {"question": "c", "sql": "SELECT 3", "db_type": "MySQL"},
        ]
        result = _append_to_history(history, "z", "SELECT 99")
        assert [h["question"] for h in result] == ["z", "a", "b", "c"]

    def test_db_type_default_is_mysql(self) -> None:
        """Default db_type is MySQL when not supplied."""
        result = _append_to_history([], "q", "SELECT 1")
        assert result[0]["db_type"] == "MySQL"

    def test_db_type_mongodb_stored(self) -> None:
        """MongoDB db_type is persisted into the entry dict."""
        result = _append_to_history([], "q", "{find: {}}", db_type="MongoDB")
        assert result[0]["db_type"] == "MongoDB"


class TestDbTypeToLang:
    """Tests for _db_type_to_lang()."""

    def test_mongodb_returns_json(self) -> None:
        """MongoDB maps to json language token."""
        assert _db_type_to_lang("MongoDB") == "json"

    def test_mysql_returns_sql(self) -> None:
        """MySQL maps to sql language token."""
        assert _db_type_to_lang("MySQL") == "sql"

    def test_postgresql_returns_sql(self) -> None:
        """PostgreSQL maps to sql language token."""
        assert _db_type_to_lang("PostgreSQL") == "sql"

    def test_unknown_returns_sql(self) -> None:
        """Any unrecognised type falls back to sql."""
        assert _db_type_to_lang("Oracle") == "sql"

    def test_empty_string_returns_sql(self) -> None:
        """Empty string is not MongoDB so returns sql."""
        assert _db_type_to_lang("") == "sql"


class TestDbTypeBadge:
    """Tests for _db_type_badge() (US-089)."""

    def test_mysql_returns_dolphin_label(self) -> None:
        """MySQL maps to the dolphin-emoji badge."""
        assert _db_type_badge("MySQL") == "\U0001f42c MySQL"

    def test_postgresql_returns_elephant_label(self) -> None:
        """PostgreSQL maps to the elephant-emoji badge."""
        assert _db_type_badge("PostgreSQL") == "\U0001f418 PostgreSQL"

    def test_mongodb_returns_leaf_label(self) -> None:
        """MongoDB maps to the leaf-emoji badge."""
        assert _db_type_badge("MongoDB") == "\U0001f343 MongoDB"

    def test_unknown_type_returned_unchanged(self) -> None:
        """Unknown database types are returned as-is."""
        assert _db_type_badge("Oracle") == "Oracle"

    def test_empty_string_returned_unchanged(self) -> None:
        """Empty string is returned as-is (not a known type)."""
        assert _db_type_badge("") == ""

    def test_returns_string(self) -> None:
        """Return type is always str."""
        assert isinstance(_db_type_badge("MySQL"), str)


class TestTruncate:
    """Tests for _truncate()."""

    def test_short_string_unchanged(self) -> None:
        """Strings within max_len are returned unchanged."""
        assert _truncate("hello") == "hello"

    def test_exact_length_unchanged(self) -> None:
        """String at exactly max_len characters is not truncated."""
        text = "x" * _TRUNCATE_LEN
        assert _truncate(text) == text

    def test_long_string_truncated_with_ellipsis(self) -> None:
        """Strings longer than max_len are cut and an ellipsis appended."""
        text = "x" * (_TRUNCATE_LEN + 10)
        result = _truncate(text)
        assert result.endswith("\u2026")
        assert len(result) == _TRUNCATE_LEN + 1  # 80 chars + ellipsis

    def test_custom_max_len(self) -> None:
        """Custom max_len parameter is respected."""
        result = _truncate("hello world", max_len=5)
        assert result == "hello\u2026"

    def test_empty_string_unchanged(self) -> None:
        """Empty string is returned as-is."""
        assert _truncate("") == ""

    def test_unicode_content_truncated_correctly(self) -> None:
        """Unicode strings are truncated by character count, not byte count."""
        text = "\u4e2d\u6587" * 50  # 100 CJK chars
        result = _truncate(text, max_len=10)
        assert len(result) == 11  # 10 chars + ellipsis
        assert result.endswith("\u2026")
