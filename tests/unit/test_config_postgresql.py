"""Unit tests for DBConfig PostgreSQL / dialect dispatch (EPIC-009 / US-044).

Covers TC-045: short-form dialect, sslmode, URL builders, validation.
"""
from __future__ import annotations

import pytest

from models.config import DBConfig


class TestMySQLDialect:
    """Default dialect remains MySQL (backwards compatibility)."""

    def test_default_dialect_is_mysql(self) -> None:
        cfg = DBConfig(host="h", port=3306, user="u", password="p", database="d")
        assert cfg.dialect == "mysql"

    def test_mysql_url_uses_pymysql_driver(self) -> None:
        cfg = DBConfig(host="h", port=3306, user="u", password="p", database="d")
        assert cfg.connection_url == "mysql+pymysql://u:p@h:3306/d"

    def test_legacy_long_form_dialect_is_normalised(self) -> None:
        cfg = DBConfig(
            host="h", port=3306, user="u", password="p", database="d",
            dialect="mysql+pymysql",
        )
        assert cfg.dialect == "mysql"
        assert cfg.connection_url == "mysql+pymysql://u:p@h:3306/d"


class TestPostgreSQLDialect:
    """PostgreSQL dialect (EPIC-009 / US-044)."""

    def test_postgresql_url_uses_psycopg_driver(self) -> None:
        cfg = DBConfig(
            host="h", port=5432, user="u", password="p", database="d",
            dialect="postgresql",
        )
        assert cfg.connection_url == "postgresql+psycopg://u:p@h:5432/d?sslmode=prefer"

    def test_postgresql_default_sslmode_is_prefer(self) -> None:
        cfg = DBConfig(
            host="h", port=5432, user="u", password="p", database="d",
            dialect="postgresql",
        )
        assert "sslmode=prefer" in cfg.connection_url

    def test_postgresql_explicit_sslmode_is_honoured(self) -> None:
        cfg = DBConfig(
            host="h", port=5432, user="u", password="p", database="d",
            dialect="postgresql", sslmode="require",
        )
        assert cfg.connection_url.endswith("?sslmode=require")

    def test_password_with_special_chars_is_url_encoded(self) -> None:
        cfg = DBConfig(
            host="h", port=5432, user="u", password="p@ss/word",
            database="d", dialect="postgresql",
        )
        # @ -> %40, / -> %2F
        assert "p%40ss%2Fword" in cfg.connection_url


class TestValidation:
    """Constructor validation."""

    def test_invalid_dialect_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="dialect"):
            DBConfig(host="h", port=1, user="u", password="p", database="d", dialect="oracle")

    def test_invalid_sslmode_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="sslmode"):
            DBConfig(
                host="h", port=5432, user="u", password="p", database="d",
                dialect="postgresql", sslmode="bogus",
            )
