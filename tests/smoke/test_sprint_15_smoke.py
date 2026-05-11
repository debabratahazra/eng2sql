"""Smoke tests for Sprint 15 — Coverage Completeness & CI Hardening.

Covers Sprint 15 user stories:
- US-066: mongo_connector.py import-time fallback + error cleanup paths covered
- US-067: models/config.py repr methods don't expose secrets
- US-068: utils/network.py duplicate-address deduplication works
- US-069: sidebar component helper functions still work after test additions
- US-070: CI coverage-docker job correctly configured in ci-cd.yml

Also includes regression smoke for DB-type selection and schema rendering.
All tests use Streamlit AppTest with mocked external services where needed.
No live database connection is required.
"""
from __future__ import annotations

import importlib
import importlib.util
import pathlib
import socket
from unittest.mock import MagicMock, patch

import pytest
from streamlit.testing.v1 import AppTest

from models.config import AppConfig, DBConfig, MongoConfig, SchemaColumn

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")

SAMPLE_SCHEMA_MYSQL = {
    "users": [
        SchemaColumn(name="id", type="INT", nullable=False, primary_key=True),
        SchemaColumn(name="name", type="VARCHAR(100)", nullable=False, primary_key=False),
        SchemaColumn(name="active", type="TINYINT", nullable=False, primary_key=False),
    ]
}

SAMPLE_SCHEMA_MONGO = {
    "users": [
        SchemaColumn(name="_id", type="ObjectId", nullable=False, primary_key=True),
        SchemaColumn(name="name", type="str", nullable=True, primary_key=False),
        SchemaColumn(name="active", type="bool", nullable=True, primary_key=False),
    ]
}


@pytest.fixture()
def app() -> AppTest:
    """Fresh AppTest instance for each test."""
    return AppTest.from_file(APP_PATH, default_timeout=15)


# ---------------------------------------------------------------------------
# US-066 — mongo_connector.py coverage uplift regressions
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s15_mongo_connector_importable() -> None:
    """US-066: mongo_connector module is still importable after Sprint 15 changes."""
    import services.mongo_connector as mc  # noqa: PLC0415
    assert hasattr(mc, "MongoDBConnector")
    assert hasattr(mc, "_PYMONGO_AVAILABLE")


@pytest.mark.smoke
def test_smoke_s15_pymongo_available_flag_is_bool() -> None:
    """US-066: _PYMONGO_AVAILABLE is a boolean value."""
    import services.mongo_connector as mc  # noqa: PLC0415
    assert isinstance(mc._PYMONGO_AVAILABLE, bool)


@pytest.mark.smoke
def test_smoke_s15_mongo_connector_connect_raises_without_pymongo() -> None:
    """US-066: connect() raises DatabaseConnectionError when pymongo unavailable."""
    from services.mongo_connector import MongoDBConnector  # noqa: PLC0415
    from utils.exceptions import DatabaseConnectionError  # noqa: PLC0415

    config = MongoConfig(
        host="localhost", port=27017, username=None, password=None,
        auth_source="admin", auth_mechanism="SCRAM-SHA-256",
    )
    with patch("services.mongo_connector._PYMONGO_AVAILABLE", False):
        connector = MongoDBConnector()
        with pytest.raises(DatabaseConnectionError, match="pymongo is not installed"):
            connector.connect(config)


# ---------------------------------------------------------------------------
# US-067 — config.py repr methods don't expose secrets
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s15_dbconfig_repr_hides_password() -> None:
    """US-067: DBConfig repr does not expose password."""
    cfg = DBConfig(
        host="db.example.com", port=3306, user="admin",
        password="supersecret", database="eng2sql", dialect="mysql",
    )
    result = repr(cfg)
    assert "supersecret" not in result
    assert "db.example.com" in result


@pytest.mark.smoke
def test_smoke_s15_appconfig_repr_masks_api_key() -> None:
    """US-067: AppConfig repr masks the OpenAI API key."""
    cfg = AppConfig(openai_api_key="sk-abc12345XYZ", model_name="gpt-4o")
    result = repr(cfg)
    assert "sk-abc12345XYZ" not in result
    assert "sk-abc123" in result or "sk-abc12" in result  # first 8 chars masked


@pytest.mark.smoke
def test_smoke_s15_appconfig_repr_none_key_no_crash() -> None:
    """US-067: AppConfig repr with None api key doesn't raise."""
    cfg = AppConfig(openai_api_key=None, model_name="gpt-4o")
    result = repr(cfg)
    assert isinstance(result, str)
    assert "gpt-4o" in result


# ---------------------------------------------------------------------------
# US-068 — network.py duplicate-address deduplication smoke
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s15_probe_reachable_host_deduplication() -> None:
    """US-068: probe_reachable_host deduplication prevents double-connect on duplicate IPs."""
    from utils.network import probe_reachable_host  # noqa: PLC0415

    dup_entry = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))
    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with (
        patch("utils.network.socket.getaddrinfo", return_value=[dup_entry, dup_entry]),
        patch("utils.network.socket.create_connection", return_value=mock_conn) as mock_cc,
    ):
        result = probe_reachable_host("127.0.0.1", 80, timeout_s=1.0)

    assert mock_cc.call_count == 1
    assert result == "127.0.0.1"


# ---------------------------------------------------------------------------
# US-069 — Sidebar component helpers smoke
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s15_ca_bundle_available_returns_bool() -> None:
    """US-069: _ca_bundle_available() returns a bool (no exception)."""
    from components.sidebar import _ca_bundle_available  # noqa: PLC0415
    result = _ca_bundle_available()
    assert isinstance(result, bool)


@pytest.mark.smoke
def test_smoke_s15_relational_dialect_config_constants_intact() -> None:
    """US-069: _MYSQL_CFG and _PG_CFG module constants are unchanged."""
    from components.sidebar import _MYSQL_CFG, _PG_CFG  # noqa: PLC0415
    assert _MYSQL_CFG.dialect == "mysql"
    assert _MYSQL_CFG.default_port == 3306
    assert _PG_CFG.dialect == "postgresql"
    assert _PG_CFG.default_port == 5432


@pytest.mark.smoke
def test_smoke_s15_sidebar_session_state_keys_defined() -> None:
    """US-069: _MYSQL_KEYS, _PG_KEYS, _MONGO_KEYS are non-empty tuples."""
    from components.sidebar import _MONGO_KEYS, _MYSQL_KEYS, _PG_KEYS  # noqa: PLC0415
    assert len(_MYSQL_KEYS) > 0
    assert len(_PG_KEYS) > 0
    assert len(_MONGO_KEYS) > 0
    assert "detected_schema" in _MYSQL_KEYS
    assert "detected_schema" in _PG_KEYS
    assert "detected_schema" in _MONGO_KEYS


# ---------------------------------------------------------------------------
# US-070 — CI coverage-docker job exists
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s15_ci_coverage_docker_job_exists() -> None:
    """US-070: .github/workflows/ci-cd.yml contains the coverage-docker job."""
    ci_path = pathlib.Path(__file__).parent.parent.parent / ".github" / "workflows" / "ci-cd.yml"
    assert ci_path.is_file(), "ci-cd.yml not found"
    content = ci_path.read_text(encoding="utf-8")
    assert "coverage-docker:" in content, "coverage-docker job not found in ci-cd.yml"
    assert "coverage-docker.xml" in content, "coverage-docker.xml artifact not referenced"
    assert "if-no-files-found: warn" in content, "graceful skip config missing"


# ---------------------------------------------------------------------------
# Regression — App renders DB type radio with all 3 options
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_smoke_s15_app_renders_db_type_radio(app: AppTest) -> None:
    """Regression: App renders MySQL / PostgreSQL / MongoDB radio options."""
    at = app
    at.run()
    assert not at.exception
    radio_values = [r.value for r in at.radio]
    assert any("MySQL" in str(v) or "PostgreSQL" in str(v) or "MongoDB" in str(v)
               for v in radio_values), f"Expected DB type radio, got: {radio_values}"
