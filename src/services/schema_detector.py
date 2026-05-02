"""Schema detection service for Eng2SQL.

Supports two modes:
1. Static — loads schema from a YAML configuration file.
2. Live — uses SQLAlchemy introspection against a connected database engine.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import Engine, inspect

from models.config import SchemaColumn, TableSchema
from utils.exceptions import SchemaDetectionError
from utils.logger import get_logger

logger = get_logger(__name__)


class SchemaDetector:
    """Detects database schema from a YAML file or a live database connection."""

    def load_static_schema(self, config_path: str) -> TableSchema:
        """Load the schema from a YAML configuration file.

        Expected YAML structure::

            tables:
              customers:
                - name: id
                  type: INT
                  nullable: false
                  primary_key: true
                - name: email
                  type: VARCHAR(200)
                  nullable: true

        Args:
            config_path: Path to the YAML schema file.

        Returns:
            A :data:`~models.config.TableSchema` mapping table names to column lists.

        Raises:
            FileNotFoundError: If the file does not exist at ``config_path``.
            SchemaDetectionError: If the YAML is malformed or has unexpected structure.
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Schema config file not found: {config_path}"
            )

        try:
            with path.open("r", encoding="utf-8") as fh:
                raw = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            raise SchemaDetectionError(
                f"Failed to parse schema YAML at {config_path}: {exc}"
            ) from exc

        if not isinstance(raw, dict) or "tables" not in raw:
            raise SchemaDetectionError(
                f"Schema YAML at {config_path} must have a top-level 'tables' key."
            )

        schema: TableSchema = {}
        for table_name, columns_raw in raw["tables"].items():
            if not isinstance(columns_raw, list):
                raise SchemaDetectionError(
                    f"Columns for table '{table_name}' must be a list."
                )
            columns: list[SchemaColumn] = []
            for col in columns_raw:
                columns.append(
                    SchemaColumn(
                        name=col["name"],
                        type=str(col.get("type", "TEXT")),
                        nullable=bool(col.get("nullable", True)),
                        primary_key=bool(col.get("primary_key", False)),
                        default=col.get("default"),
                    )
                )
            schema[table_name] = columns

        logger.info("Loaded static schema: %d tables from %s", len(schema), config_path)
        return schema

    def detect_live_schema(self, engine: Engine) -> TableSchema:
        """Introspect a live database and return its schema.

        Uses SQLAlchemy's :func:`sqlalchemy.inspect` to enumerate tables and columns.

        Args:
            engine: A connected SQLAlchemy :class:`~sqlalchemy.engine.Engine`.

        Returns:
            A :data:`~models.config.TableSchema` mapping table names to column lists.

        Raises:
            SchemaDetectionError: If introspection fails for any reason.
        """
        try:
            inspector = inspect(engine)
            table_names: list[str] = inspector.get_table_names()
        except Exception as exc:
            raise SchemaDetectionError(
                f"Failed to list tables from database: {exc}"
            ) from exc

        schema: TableSchema = {}
        for table_name in table_names:
            try:
                raw_columns = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                pk_cols: list[str] = pk_constraint.get("constrained_columns", [])
            except Exception as exc:
                raise SchemaDetectionError(
                    f"Failed to inspect table '{table_name}': {exc}"
                ) from exc

            columns: list[SchemaColumn] = [
                SchemaColumn(
                    name=col["name"],
                    type=str(col["type"]),
                    nullable=bool(col.get("nullable", True)),
                    primary_key=col["name"] in pk_cols,
                    default=str(col["default"]) if col.get("default") is not None else None,
                )
                for col in raw_columns
            ]
            schema[table_name] = columns

        logger.info(
            "Detected live schema: %d tables from engine %s",
            len(schema),
            engine.url.render_as_string(hide_password=True),
        )
        return schema
