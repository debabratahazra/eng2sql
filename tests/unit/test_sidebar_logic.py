"""Unit tests for pure-logic helper functions extracted from sidebar.py (US-072).

These functions have zero Streamlit dependencies and can be tested in isolation.
Coverage target: 100 % of the 6 helper functions.
"""
from __future__ import annotations

import pytest

from components.sidebar import (
    _build_mongo_config,
    _build_relational_config,
    _format_connect_success,
    _select_default_index,
    _validate_mongo_fields_inputs,
    _validate_relational_inputs,
)
from models.config import DBConfig, MongoConfig


# ---------------------------------------------------------------------------
# _validate_relational_inputs
# ---------------------------------------------------------------------------


class TestValidateRelationalInputs:
    """Tests for :func:`_validate_relational_inputs`."""

    def test_all_valid_no_admin_db(self) -> None:
        """Returns None when host/user/password are all non-empty and admin_db is None."""
        result = _validate_relational_inputs("localhost", "user", "pass", None)
        assert result is None

    def test_all_valid_with_admin_db(self) -> None:
        """Returns None when admin_db is a non-empty string."""
        result = _validate_relational_inputs("localhost", "user", "pass", "postgres")
        assert result is None

    def test_missing_host_returns_warning(self) -> None:
        """Returns a warning tuple when host is empty."""
        result = _validate_relational_inputs("", "user", "pass", None)
        assert result is not None
        level, msg = result
        assert level == "warning"
        assert "host" in msg.lower() or "fill" in msg.lower()

    def test_missing_user_returns_warning(self) -> None:
        """Returns a warning tuple when user is empty."""
        result = _validate_relational_inputs("localhost", "", "pass", None)
        assert result is not None
        assert result[0] == "warning"

    def test_missing_password_returns_warning(self) -> None:
        """Returns a warning tuple when password is empty."""
        result = _validate_relational_inputs("localhost", "user", "", None)
        assert result is not None
        assert result[0] == "warning"

    def test_empty_admin_db_with_nonnone_admin_db_key_returns_warning(self) -> None:
        """Returns a warning when admin_db is not None but blank (spaces only)."""
        result = _validate_relational_inputs("localhost", "user", "pass", "   ")
        assert result is not None
        level, msg = result
        assert level == "warning"
        assert "admin" in msg.lower() or "empty" in msg.lower()

    def test_empty_string_admin_db_returns_warning(self) -> None:
        """Returns a warning when admin_db is an empty string (not None)."""
        result = _validate_relational_inputs("localhost", "user", "pass", "")
        assert result is not None
        assert result[0] == "warning"

    def test_none_admin_db_does_not_trigger_warning(self) -> None:
        """admin_db=None means MySQL — no admin DB check performed."""
        result = _validate_relational_inputs("host", "u", "p", None)
        assert result is None


# ---------------------------------------------------------------------------
# _build_relational_config
# ---------------------------------------------------------------------------


class TestBuildRelationalConfig:
    """Tests for :func:`_build_relational_config`."""

    def test_returns_dbconfig_instance(self) -> None:
        """Factory returns a DBConfig object."""
        cfg = _build_relational_config("host", 3306, "u", "p", "db", "mysql", None)
        assert isinstance(cfg, DBConfig)

    def test_field_mapping_mysql(self) -> None:
        """All fields are mapped correctly for MySQL dialect."""
        cfg = _build_relational_config("myhost", 3306, "root", "secret", "mydb", "mysql", None)
        assert cfg.host == "myhost"
        assert cfg.port == 3306
        assert cfg.user == "root"
        assert cfg.password == "secret"
        assert cfg.database == "mydb"
        assert cfg.dialect == "mysql"
        assert cfg.sslmode is None

    def test_field_mapping_postgresql_with_sslmode(self) -> None:
        """All fields are mapped correctly for PostgreSQL dialect with sslmode."""
        cfg = _build_relational_config("pghost", 5432, "pguser", "pgpass", "pgdb", "postgresql", "require")
        assert cfg.host == "pghost"
        assert cfg.port == 5432
        assert cfg.dialect == "postgresql"
        assert cfg.sslmode == "require"

    def test_port_type_preserved(self) -> None:
        """Port must remain an int (not a string)."""
        cfg = _build_relational_config("h", 3307, "u", "p", "d", "mysql", None)
        assert isinstance(cfg.port, int)
        assert cfg.port == 3307


# ---------------------------------------------------------------------------
# _format_connect_success
# ---------------------------------------------------------------------------


class TestFormatConnectSuccess:
    """Tests for :func:`_format_connect_success`."""

    def test_single_database(self) -> None:
        """Uses singular 'database' when n == 1."""
        result = _format_connect_success("myhost", 1)
        assert "1 database found" in result
        assert "databases" not in result

    def test_plural_databases(self) -> None:
        """Uses plural 'databases' when n > 1."""
        result = _format_connect_success("myhost", 5)
        assert "5 databases found" in result

    def test_zero_databases(self) -> None:
        """Uses plural 'databases' when n == 0."""
        result = _format_connect_success("myhost", 0)
        assert "0 databases found" in result

    def test_host_is_bold_markdown(self) -> None:
        """Host is wrapped in Markdown bold markers."""
        result = _format_connect_success("db.example.com", 3)
        assert "**db.example.com**" in result

    def test_format_overall_structure(self) -> None:
        """Full string matches expected pattern."""
        result = _format_connect_success("localhost", 2)
        assert result == "Connected to **localhost** - 2 databases found"


# ---------------------------------------------------------------------------
# _select_default_index
# ---------------------------------------------------------------------------


class TestSelectDefaultIndex:
    """Tests for :func:`_select_default_index`."""

    def test_current_found_in_available(self) -> None:
        """Returns the correct index when current is present."""
        idx = _select_default_index(["alpha", "beta", "gamma"], "beta")
        assert idx == 1

    def test_current_not_in_available_returns_zero(self) -> None:
        """Returns 0 when current is not present in the list."""
        idx = _select_default_index(["alpha", "beta"], "delta")
        assert idx == 0

    def test_current_none_returns_zero(self) -> None:
        """Returns 0 when current is None."""
        idx = _select_default_index(["alpha", "beta"], None)
        assert idx == 0

    def test_first_element(self) -> None:
        """Returns 0 when current is the first element."""
        idx = _select_default_index(["alpha", "beta", "gamma"], "alpha")
        assert idx == 0

    def test_last_element(self) -> None:
        """Returns last index when current is the last element."""
        idx = _select_default_index(["alpha", "beta", "gamma"], "gamma")
        assert idx == 2

    def test_empty_list_with_none_returns_zero(self) -> None:
        """Returns 0 gracefully on an empty list with None current."""
        idx = _select_default_index([], None)
        assert idx == 0


# ---------------------------------------------------------------------------
# _validate_mongo_fields_inputs
# ---------------------------------------------------------------------------


class TestValidateMongoFieldsInputs:
    """Tests for :func:`_validate_mongo_fields_inputs`."""

    def test_valid_authenticated(self) -> None:
        """Returns None when host/username/password are all provided and no_auth is False."""
        result = _validate_mongo_fields_inputs("localhost", "user", "pass", False)
        assert result is None

    def test_valid_no_auth(self) -> None:
        """Returns None when no_auth is True even with empty username/password."""
        result = _validate_mongo_fields_inputs("localhost", "", "", True)
        assert result is None

    def test_missing_host_returns_warning(self) -> None:
        """Returns a warning when host is empty."""
        result = _validate_mongo_fields_inputs("", "user", "pass", False)
        assert result is not None
        level, msg = result
        assert level == "warning"
        assert "host" in msg.lower()

    def test_missing_username_without_no_auth_returns_warning(self) -> None:
        """Returns a warning when username is empty and no_auth is False."""
        result = _validate_mongo_fields_inputs("localhost", "", "pass", False)
        assert result is not None
        assert result[0] == "warning"

    def test_missing_password_without_no_auth_returns_warning(self) -> None:
        """Returns a warning when password is empty and no_auth is False."""
        result = _validate_mongo_fields_inputs("localhost", "user", "", False)
        assert result is not None
        assert result[0] == "warning"

    def test_no_auth_bypasses_credential_check(self) -> None:
        """no_auth=True overrides missing username/password validation."""
        result = _validate_mongo_fields_inputs("localhost", "", "", True)
        assert result is None

    def test_warning_message_mentions_no_auth_option(self) -> None:
        """Credential warning message references the 'None / No Auth' option."""
        result = _validate_mongo_fields_inputs("localhost", "", "", False)
        assert result is not None
        _, msg = result
        assert "No Auth" in msg or "no auth" in msg.lower()


# ---------------------------------------------------------------------------
# _build_mongo_config
# ---------------------------------------------------------------------------


class TestBuildMongoConfig:
    """Tests for :func:`_build_mongo_config`."""

    def test_returns_mongoconfig_instance(self) -> None:
        """Factory returns a MongoConfig object."""
        cfg = _build_mongo_config("localhost", 27017, "user", "pass", "admin", "SCRAM-SHA-256")
        assert isinstance(cfg, MongoConfig)

    def test_field_mapping(self) -> None:
        """All keyword arguments are mapped to the correct MongoConfig fields."""
        cfg = _build_mongo_config(
            "mongohost", 27017, "mongouser", "mongosecret", "admin", "SCRAM-SHA-1"
        )
        assert cfg.host == "mongohost"
        assert cfg.port == 27017
        assert cfg.username == "mongouser"
        assert cfg.password == "mongosecret"
        assert cfg.auth_source == "admin"
        assert cfg.auth_mechanism == "SCRAM-SHA-1"

    def test_port_type_preserved(self) -> None:
        """Port must remain an int."""
        cfg = _build_mongo_config("h", 27018, "u", "p", "admin", "SCRAM-SHA-256")
        assert isinstance(cfg.port, int)
        assert cfg.port == 27018

    def test_no_auth_empty_credentials(self) -> None:
        """Empty credentials are passed through without modification."""
        cfg = _build_mongo_config("localhost", 27017, "", "", "admin", "None / No Auth")
        assert cfg.username == ""
        assert cfg.password == ""
        assert cfg.auth_mechanism == "None / No Auth"
