"""Extended unit tests for SchemaDetector — US-064.

Covers the previously uncovered lines in schema_detector.py:
- Line 71: non-list columns branch in load_static_schema
- Lines 104-140: entire detect_live_schema method via mocked sqlalchemy.inspect
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from services.schema_detector import SchemaDetector
from utils.exceptions import SchemaDetectionError


@pytest.fixture
def detector() -> SchemaDetector:
    """Return a fresh SchemaDetector instance."""
    return SchemaDetector()


def _make_inspector(
    table_names: list[str],
    columns_by_table: dict[str, list[dict]],
    pk_by_table: dict[str, list[str]] | None = None,
) -> MagicMock:
    """Return a mock SQLAlchemy inspector."""
    if pk_by_table is None:
        pk_by_table = {}

    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = table_names

    def _get_columns(table_name: str) -> list[dict]:
        return columns_by_table.get(table_name, [])

    def _get_pk_constraint(table_name: str) -> dict:
        return {"constrained_columns": pk_by_table.get(table_name, [])}

    mock_inspector.get_columns.side_effect = _get_columns
    mock_inspector.get_pk_constraint.side_effect = _get_pk_constraint
    return mock_inspector


# ---------------------------------------------------------------------------
# load_static_schema — branch: columns not a list (line 71)
# ---------------------------------------------------------------------------


class TestLoadStaticSchemaExtended:
    """Extended coverage for load_static_schema non-list columns branch."""

    def test_columns_not_a_list_raises_schema_error(
        self, detector: SchemaDetector, tmp_path: Path
    ) -> None:
        """Line 71: SchemaDetectionError when table columns value is a dict not a list."""
        bad_schema = {"tables": {"users": {"name": "id", "type": "INT"}}}
        path = tmp_path / "bad_cols.yaml"
        path.write_text(yaml.dump(bad_schema))

        with pytest.raises(SchemaDetectionError, match="must be a list"):
            detector.load_static_schema(str(path))

    def test_column_with_default_value_parsed(
        self, detector: SchemaDetector, tmp_path: Path
    ) -> None:
        """Column with explicit default value is stored on SchemaColumn."""
        schema = {
            "tables": {
                "settings": [
                    {
                        "name": "enabled",
                        "type": "BOOL",
                        "nullable": False,
                        "primary_key": False,
                        "default": True,
                    }
                ]
            }
        }
        path = tmp_path / "defaults.yaml"
        path.write_text(yaml.dump(schema))

        result = detector.load_static_schema(str(path))
        col = result["settings"][0]
        assert col.default is True

    def test_column_type_defaults_to_text(
        self, detector: SchemaDetector, tmp_path: Path
    ) -> None:
        """Column without 'type' key defaults to 'TEXT'."""
        schema = {"tables": {"t": [{"name": "x"}]}}
        path = tmp_path / "no_type.yaml"
        path.write_text(yaml.dump(schema))

        result = detector.load_static_schema(str(path))
        assert result["t"][0].type == "TEXT"


# ---------------------------------------------------------------------------
# detect_live_schema — lines 104-140 via mocked sqlalchemy.inspect
# ---------------------------------------------------------------------------


class TestDetectLiveSchemaUnit:
    """Unit tests for detect_live_schema using mocked SQLAlchemy inspector."""

    def test_returns_empty_schema_for_empty_database(
        self, detector: SchemaDetector
    ) -> None:
        """Lines 104-140: empty table list returns empty TableSchema."""
        mock_inspector = _make_inspector(table_names=[], columns_by_table={})
        mock_engine = MagicMock()
        mock_engine.url.render_as_string.return_value = "mysql://host/db"

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            schema = detector.detect_live_schema(mock_engine)

        assert schema == {}
        mock_inspector.get_table_names.assert_called_once()

    def test_returns_single_table_with_columns(
        self, detector: SchemaDetector
    ) -> None:
        """Happy path: one table with two columns is returned correctly."""
        columns = [
            {"name": "id", "type": "INTEGER", "nullable": False, "default": None},
            {"name": "email", "type": "VARCHAR", "nullable": True, "default": None},
        ]
        mock_inspector = _make_inspector(
            table_names=["users"],
            columns_by_table={"users": columns},
            pk_by_table={"users": ["id"]},
        )
        mock_engine = MagicMock()
        mock_engine.url.render_as_string.return_value = "mysql://host/db"

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            schema = detector.detect_live_schema(mock_engine)

        assert "users" in schema
        assert len(schema["users"]) == 2
        id_col = schema["users"][0]
        assert id_col.name == "id"
        assert id_col.primary_key is True
        assert id_col.nullable is False

    def test_primary_key_detection(self, detector: SchemaDetector) -> None:
        """Columns listed in pk_constraint are flagged as primary_key=True."""
        columns = [
            {"name": "pk_col", "type": "INT", "nullable": False, "default": None},
            {"name": "data_col", "type": "TEXT", "nullable": True, "default": None},
        ]
        mock_inspector = _make_inspector(
            table_names=["items"],
            columns_by_table={"items": columns},
            pk_by_table={"items": ["pk_col"]},
        )
        mock_engine = MagicMock()
        mock_engine.url.render_as_string.return_value = "mysql://host/db"

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            schema = detector.detect_live_schema(mock_engine)

        cols = {c.name: c for c in schema["items"]}
        assert cols["pk_col"].primary_key is True
        assert cols["data_col"].primary_key is False

    def test_column_default_value_serialised(self, detector: SchemaDetector) -> None:
        """Column with a non-None default is stored as str on SchemaColumn."""
        columns = [
            {
                "name": "status",
                "type": "VARCHAR",
                "nullable": False,
                "default": "active",
            }
        ]
        mock_inspector = _make_inspector(
            table_names=["orders"],
            columns_by_table={"orders": columns},
        )
        mock_engine = MagicMock()
        mock_engine.url.render_as_string.return_value = "mysql://host/db"

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            schema = detector.detect_live_schema(mock_engine)

        assert schema["orders"][0].default == "active"

    def test_column_none_default_stored_as_none(self, detector: SchemaDetector) -> None:
        """Column with default=None stores None on SchemaColumn."""
        columns = [{"name": "x", "type": "INT", "nullable": True, "default": None}]
        mock_inspector = _make_inspector(
            table_names=["t"], columns_by_table={"t": columns}
        )
        mock_engine = MagicMock()
        mock_engine.url.render_as_string.return_value = "sqlite:///test.db"

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            schema = detector.detect_live_schema(mock_engine)

        assert schema["t"][0].default is None

    def test_multiple_tables_returned(self, detector: SchemaDetector) -> None:
        """Multiple tables are all present in the returned schema."""
        cols_a = [{"name": "id", "type": "INT", "nullable": False, "default": None}]
        cols_b = [{"name": "name", "type": "TEXT", "nullable": True, "default": None}]
        mock_inspector = _make_inspector(
            table_names=["table_a", "table_b"],
            columns_by_table={"table_a": cols_a, "table_b": cols_b},
        )
        mock_engine = MagicMock()
        mock_engine.url.render_as_string.return_value = "mysql://host/db"

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            schema = detector.detect_live_schema(mock_engine)

        assert "table_a" in schema
        assert "table_b" in schema
        assert len(schema) == 2

    def test_get_table_names_raises_schema_detection_error(
        self, detector: SchemaDetector
    ) -> None:
        """Lines 107-110: Exception from get_table_names() is wrapped as SchemaDetectionError."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.side_effect = RuntimeError("DB unreachable")
        mock_engine = MagicMock()

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            with pytest.raises(SchemaDetectionError, match="Failed to list tables"):
                detector.detect_live_schema(mock_engine)

    def test_get_columns_raises_schema_detection_error(
        self, detector: SchemaDetector
    ) -> None:
        """Lines 118-121: Exception from get_columns() is wrapped as SchemaDetectionError."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ["bad_table"]
        mock_inspector.get_columns.side_effect = RuntimeError("permission denied")
        mock_engine = MagicMock()

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            with pytest.raises(SchemaDetectionError, match="Failed to inspect table"):
                detector.detect_live_schema(mock_engine)

    def test_no_pk_constraint_defaults_to_no_pk(self, detector: SchemaDetector) -> None:
        """Empty pk_constraint returns all columns with primary_key=False."""
        columns = [{"name": "val", "type": "TEXT", "nullable": True, "default": None}]
        mock_inspector = _make_inspector(
            table_names=["log"],
            columns_by_table={"log": columns},
            pk_by_table={},  # no PK declared
        )
        mock_engine = MagicMock()
        mock_engine.url.render_as_string.return_value = "mysql://host/log_db"

        with patch("services.schema_detector.inspect", return_value=mock_inspector):
            schema = detector.detect_live_schema(mock_engine)

        assert schema["log"][0].primary_key is False
