"""Extended unit tests for models/config.py — US-067.

Covers previously uncovered lines:
- Line 79:      DBConfig.__repr__() return statement
- Lines 177-178: AppConfig.__repr__() masked key + return statement
"""
from __future__ import annotations

import pytest

from models.config import AppConfig, DBConfig


# ---------------------------------------------------------------------------
# DBConfig.__repr__ — line 79
# ---------------------------------------------------------------------------


class TestDBConfigRepr:
    """Cover line 79: DBConfig.__repr__ return value."""

    def test_repr_contains_host(self) -> None:
        """Line 79: __repr__ includes host."""
        cfg = DBConfig(
            host="db.example.com",
            port=3306,
            user="alice",
            password="s3cr3t",
            database="shop",
            dialect="mysql",
        )
        r = repr(cfg)
        assert "db.example.com" in r

    def test_repr_contains_dialect(self) -> None:
        """Line 79: __repr__ includes dialect."""
        cfg = DBConfig(
            host="pg.example.com",
            port=5432,
            user="bob",
            password="pw",
            database="analytics",
            dialect="postgresql",
        )
        r = repr(cfg)
        assert "postgresql" in r
        assert "analytics" in r

    def test_repr_does_not_expose_password(self) -> None:
        """DBConfig.__repr__ must never expose the password."""
        cfg = DBConfig(
            host="h",
            port=3306,
            user="u",
            password="supersecret123",
            database="d",
        )
        assert "supersecret123" not in repr(cfg)

    def test_repr_format(self) -> None:
        """Line 79: __repr__ starts with 'DBConfig('."""
        cfg = DBConfig(
            host="myhost",
            port=3306,
            user="myuser",
            password="pw",
            database="mydb",
        )
        assert repr(cfg).startswith("DBConfig(")


# ---------------------------------------------------------------------------
# AppConfig.__repr__ — lines 177-178
# ---------------------------------------------------------------------------


class TestAppConfigRepr:
    """Cover lines 177-178: AppConfig.__repr__ masked key and return value."""

    def test_repr_masks_api_key(self) -> None:
        """Lines 177-178: API key is truncated to first 8 chars + '...'."""
        cfg = AppConfig(openai_api_key="sk-abcdefghij1234567890")
        r = repr(cfg)
        assert "sk-abcde" in r
        assert "..." in r
        assert "ghij1234567890" not in r

    def test_repr_api_key_not_set(self) -> None:
        """Lines 177-178: empty API key shows '(not set)'."""
        cfg = AppConfig(openai_api_key="")
        r = repr(cfg)
        assert "(not set)" in r

    def test_repr_contains_model_name(self) -> None:
        """Lines 177-178: __repr__ includes model_name."""
        cfg = AppConfig(openai_api_key="sk-12345678xxxx", model_name="gpt-4o")
        r = repr(cfg)
        assert "gpt-4o" in r

    def test_repr_format(self) -> None:
        """Lines 177-178: __repr__ starts with 'AppConfig('."""
        cfg = AppConfig(openai_api_key="sk-12345678xxxx")
        assert repr(cfg).startswith("AppConfig(")

    def test_repr_short_api_key_not_truncated(self) -> None:
        """Lines 177-178: API key shorter than 8 chars shows full key (no IndexError)."""
        cfg = AppConfig(openai_api_key="short")
        r = repr(cfg)
        # 'short' is 5 chars; [:8] returns 'short'; still appended with '...'
        assert "short..." in r
