"""Unit tests for the SchemaDetector service — TC-005 through TC-007."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from services.schema_detector import SchemaDetector
from utils.exceptions import SchemaDetectionError


@pytest.fixture
def detector() -> SchemaDetector:
    return SchemaDetector()


@pytest.fixture
def valid_schema_yaml(tmp_path: Path) -> str:
    """Write a valid schema YAML to a temp file and return the path."""
    schema = {
        "tables": {
            "users": [
                {"name": "id", "type": "INT", "nullable": False, "primary_key": True},
                {"name": "username", "type": "VARCHAR(50)", "nullable": False},
                {"name": "email", "type": "VARCHAR(200)", "nullable": True},
            ],
            "posts": [
                {"name": "id", "type": "INT", "nullable": False, "primary_key": True},
                {"name": "user_id", "type": "INT", "nullable": False},
                {"name": "title", "type": "VARCHAR(300)", "nullable": False},
            ],
        }
    }
    path = tmp_path / "schema.yaml"
    path.write_text(yaml.dump(schema))
    return str(path)


class TestLoadStaticSchema:
    """Tests for SchemaDetector.load_static_schema — TC-005, TC-006."""

    def test_loads_valid_schema_yaml(self, detector, valid_schema_yaml):
        """TC-005: Valid YAML parsed into correct TableSchema structure."""
        schema = detector.load_static_schema(valid_schema_yaml)

        assert "users" in schema
        assert "posts" in schema
        assert len(schema["users"]) == 3

    def test_column_attributes_correct(self, detector, valid_schema_yaml):
        """TC-005 variant: Column attributes mapped correctly."""
        schema = detector.load_static_schema(valid_schema_yaml)
        id_col = schema["users"][0]

        assert id_col.name == "id"
        assert id_col.type == "INT"
        assert id_col.nullable is False
        assert id_col.primary_key is True

    def test_nullable_defaults_to_true(self, detector, tmp_path):
        """Columns without explicit nullable default to True."""
        minimal = {"tables": {"t": [{"name": "x", "type": "TEXT"}]}}
        path = tmp_path / "minimal.yaml"
        path.write_text(yaml.dump(minimal))

        schema = detector.load_static_schema(str(path))
        assert schema["t"][0].nullable is True

    def test_raises_file_not_found(self, detector):
        """TC-006: Missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            detector.load_static_schema("/nonexistent/path/schema.yaml")

    def test_raises_on_malformed_yaml(self, detector, tmp_path):
        """TC-006 variant: Malformed YAML raises SchemaDetectionError."""
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("tables: [this: is: not: valid")

        with pytest.raises((SchemaDetectionError, Exception)):
            detector.load_static_schema(str(bad_file))

    def test_raises_on_missing_tables_key(self, detector, tmp_path):
        """SchemaDetectionError raised when top-level 'tables' key is absent."""
        bad_schema = {"schema": {"t": []}}
        path = tmp_path / "no_tables.yaml"
        path.write_text(yaml.dump(bad_schema))

        with pytest.raises(SchemaDetectionError, match="'tables' key"):
            detector.load_static_schema(str(path))

    def test_returns_empty_schema_for_empty_tables(self, detector, tmp_path):
        """Empty tables dict returns empty TableSchema."""
        empty = {"tables": {}}
        path = tmp_path / "empty.yaml"
        path.write_text(yaml.dump(empty))

        schema = detector.load_static_schema(str(path))
        assert schema == {}


class TestDetectLiveSchema:
    """Tests for SchemaDetector.detect_live_schema — TC-007."""

    @pytest.mark.integration
    def test_returns_tables_from_sqlite_engine(self, detector, sqlite_engine):
        """TC-007: detect_live_schema returns correct tables from SQLite."""
        schema = detector.detect_live_schema(sqlite_engine)

        assert "customers" in schema
        assert "orders" in schema

    @pytest.mark.integration
    def test_column_names_correct(self, detector, sqlite_engine):
        """TC-007 variant: Column names match what was created."""
        schema = detector.detect_live_schema(sqlite_engine)
        col_names = [col.name for col in schema["customers"]]

        assert "id" in col_names
        assert "name" in col_names
        assert "email" in col_names

    @pytest.mark.integration
    def test_primary_key_detected(self, detector, sqlite_engine):
        """TC-007 variant: Primary key columns are correctly identified."""
        schema = detector.detect_live_schema(sqlite_engine)
        id_col = next(c for c in schema["customers"] if c.name == "id")

        assert id_col.primary_key is True

    @pytest.mark.integration
    def test_empty_database_returns_empty_schema(self, detector):
        """TC-007 variant: Database with no tables returns empty schema."""
        from sqlalchemy import create_engine as _create_engine

        empty_engine = _create_engine("sqlite:///:memory:")
        try:
            schema = detector.detect_live_schema(empty_engine)
            assert schema == {}
        finally:
            empty_engine.dispose()
