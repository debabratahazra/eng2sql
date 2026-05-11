"""Unit tests for MongoSchemaDetector service."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from models.config import SchemaColumn
from services.mongo_schema_detector import MongoSchemaDetector, _infer_type
from utils.exceptions import SchemaDetectionError


class TestInferType:
    """Unit tests for the _infer_type helper."""

    @pytest.mark.parametrize(
        "value, expected",
        [
            (42, "Number"),
            (3.14, "Number"),
            ("hello", "String"),
            (True, "Boolean"),
            ({"key": "val"}, "Object"),
            ([1, 2, 3], "Array"),
            (None, "Null"),
        ],
    )
    def test_infer_type_builtin(self, value: object, expected: str) -> None:
        """_infer_type maps Python built-in types correctly."""
        assert _infer_type(value) == expected

    def test_infer_type_unknown_falls_back_to_mixed(self) -> None:
        """_infer_type returns 'Mixed' for unrecognised types."""

        class WeirdType:
            pass

        assert _infer_type(WeirdType()) == "Mixed"


class TestMongoSchemaDetector:
    """Unit tests for MongoSchemaDetector.detect_schema()."""

    def setup_method(self) -> None:
        """Create a fresh detector for each test."""
        self.detector = MongoSchemaDetector()

    def _make_db(self, collections: dict[str, list[dict]]) -> MagicMock:
        """Build a mock pymongo Database with the given collections.

        Args:
            collections: Mapping of collection name to list of mock documents.

        Returns:
            A MagicMock behaving like a pymongo Database.
        """
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = list(collections.keys())

        def getitem(name: str) -> MagicMock:
            mock_col = MagicMock()
            mock_col.find.return_value = iter(collections[name])
            return mock_col

        mock_db.__getitem__ = MagicMock(side_effect=getitem)
        return mock_db

    # ── Happy path ────────────────────────────────────────────────────────────

    def test_detect_schema_returns_table_schema(self) -> None:
        """detect_schema() returns a dict keyed by collection name."""
        db = self._make_db({"users": [{"_id": 1, "name": "Alice", "email": "a@b.com"}]})
        result = self.detector.detect_schema(db)

        assert "users" in result
        assert isinstance(result["users"], list)

    def test_detect_schema_infers_column_names(self) -> None:
        """detect_schema() captures top-level field names."""
        db = self._make_db({"items": [{"_id": 1, "price": 9.99, "label": "Widget"}]})
        schema = self.detector.detect_schema(db)

        field_names = {col.name for col in schema["items"]}
        assert {"_id", "price", "label"} == field_names

    def test_detect_schema_id_is_primary_key(self) -> None:
        """detect_schema() marks _id as primary_key=True."""
        db = self._make_db({"things": [{"_id": 1, "val": "x"}]})
        schema = self.detector.detect_schema(db)

        id_col = next(c for c in schema["things"] if c.name == "_id")
        assert id_col.primary_key is True

    def test_detect_schema_non_id_fields_not_primary_key(self) -> None:
        """detect_schema() marks non-_id fields as primary_key=False."""
        db = self._make_db({"things": [{"_id": 1, "val": "x"}]})
        schema = self.detector.detect_schema(db)

        val_col = next(c for c in schema["things"] if c.name == "val")
        assert val_col.primary_key is False

    def test_detect_schema_all_fields_nullable(self) -> None:
        """detect_schema() sets nullable=True for all columns."""
        db = self._make_db({"docs": [{"_id": 1, "title": "T"}]})
        schema = self.detector.detect_schema(db)

        assert all(col.nullable is True for col in schema["docs"])

    def test_detect_schema_unions_fields_across_documents(self) -> None:
        """detect_schema() unions fields from all sampled documents."""
        db = self._make_db({
            "products": [
                {"_id": 1, "name": "A", "price": 10.0},
                {"_id": 2, "name": "B", "discount": 5.0},
            ]
        })
        schema = self.detector.detect_schema(db)
        field_names = {c.name for c in schema["products"]}

        assert "price" in field_names
        assert "discount" in field_names

    def test_detect_schema_conflicting_types_become_mixed(self) -> None:
        """detect_schema() uses 'Mixed' when a field has different types."""
        db = self._make_db({
            "mixed": [
                {"_id": 1, "value": 42},
                {"_id": 2, "value": "a string"},
            ]
        })
        schema = self.detector.detect_schema(db)

        value_col = next(c for c in schema["mixed"] if c.name == "value")
        assert value_col.type == "Mixed"

    # ── Empty collection ──────────────────────────────────────────────────────

    def test_detect_schema_empty_collection_returns_empty_columns(self) -> None:
        """detect_schema() handles empty collections gracefully."""
        db = self._make_db({"empty_col": []})
        schema = self.detector.detect_schema(db)

        assert "empty_col" in schema
        assert schema["empty_col"] == []

    # ── sample_size limit ─────────────────────────────────────────────────────

    def test_detect_schema_respects_sample_size(self) -> None:
        """detect_schema() passes limit=sample_size to find()."""
        mock_col = MagicMock()
        mock_col.find.return_value = iter([{"_id": 1, "x": 1}])

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["col"]
        mock_db.__getitem__ = MagicMock(return_value=mock_col)

        self.detector.detect_schema(mock_db, sample_size=50)

        mock_col.find.assert_called_once_with({}, limit=50)

    # ── Error handling ────────────────────────────────────────────────────────

    def test_detect_schema_raises_on_list_collection_failure(self) -> None:
        """detect_schema() raises SchemaDetectionError when list_collection_names fails."""
        mock_db = MagicMock()
        mock_db.list_collection_names.side_effect = Exception("driver error")

        with pytest.raises(SchemaDetectionError, match="Failed to list MongoDB collections"):
            self.detector.detect_schema(mock_db)

    def test_detect_schema_raises_on_find_failure(self) -> None:
        """detect_schema() raises SchemaDetectionError when find() fails."""
        mock_col = MagicMock()
        mock_col.find.side_effect = Exception("cursor error")

        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = ["broken_col"]
        mock_db.__getitem__ = MagicMock(return_value=mock_col)

        with pytest.raises(SchemaDetectionError, match="Failed to sample collection"):
            self.detector.detect_schema(mock_db)

    # ── Multiple collections ──────────────────────────────────────────────────

    def test_detect_schema_multiple_collections(self) -> None:
        """detect_schema() processes all collections and returns all in schema."""
        db = self._make_db({
            "users": [{"_id": 1, "name": "Alice"}],
            "orders": [{"_id": 10, "total": 99.99}],
        })
        schema = self.detector.detect_schema(db)

        assert "users" in schema
        assert "orders" in schema


class TestSystemCollectionsAndAuthZ:
    """BUG-008 — skip MongoDB system.* collections and tolerate per-collection
    authorisation failures during schema sampling."""

    def setup_method(self) -> None:
        """Create a fresh detector for each test."""
        self.detector = MongoSchemaDetector()

    @staticmethod
    def _make_db_with_find_handlers(
        handlers: dict[str, "object"],
    ) -> MagicMock:
        """Build a mock pymongo Database where each collection has a custom
        find() behaviour.

        Args:
            handlers: Mapping of collection name to either:
                * a ``list[dict]`` of documents (returned by ``find()``), or
                * an ``Exception`` instance (raised by ``find()``).

        Returns:
            A MagicMock behaving like a pymongo Database.
        """
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = list(handlers.keys())

        def getitem(name: str) -> MagicMock:
            mock_col = MagicMock()
            handler = handlers[name]
            if isinstance(handler, Exception):
                mock_col.find.side_effect = handler
            else:
                mock_col.find.return_value = iter(handler)
            return mock_col

        mock_db.__getitem__ = MagicMock(side_effect=getitem)
        return mock_db

    # ── system.* filtering ────────────────────────────────────────────────────

    def test_detect_schema_skips_system_profile(self) -> None:
        """``system.profile`` is filtered out and never sampled."""
        db = self._make_db_with_find_handlers({
            "system.profile": Exception(
                "not authorized on idcauditlog to execute command find: system.profile"
            ),
            "users": [{"_id": 1, "name": "Alice"}],
        })

        schema = self.detector.detect_schema(db)

        assert "system.profile" not in schema
        assert "users" in schema
        # The find() side_effect for system.profile must never have fired
        db.__getitem__("system.profile").find.assert_not_called()

    def test_detect_schema_skips_all_system_prefixed_collections(self) -> None:
        """Every ``system.*`` collection is dropped before the sampling loop."""
        db = self._make_db_with_find_handlers({
            "system.profile": [{"_id": 1}],
            "system.views": [{"_id": 2}],
            "system.js": [{"_id": 3}],
            "system.sessions": [{"_id": 4}],
            "users": [{"_id": 5, "name": "Alice"}],
        })

        schema = self.detector.detect_schema(db)

        for sys_name in ("system.profile", "system.views", "system.js", "system.sessions"):
            assert sys_name not in schema
        assert "users" in schema

    def test_detect_schema_user_collections_processed_alongside_system(self) -> None:
        """User collections are still processed when system.* collections exist."""
        db = self._make_db_with_find_handlers({
            "system.profile": [{"_id": 1}],
            "users": [{"_id": 2, "email": "a@b.com"}],
            "orders": [{"_id": 3, "total": 50.0}],
        })

        schema = self.detector.detect_schema(db)

        assert {"users", "orders"} <= set(schema.keys())
        user_fields = {col.name for col in schema["users"]}
        assert {"_id", "email"} == user_fields

    # ── Per-collection authorisation tolerance ───────────────────────────────

    def test_detect_schema_skips_collection_on_unauthorized_error(self) -> None:
        """A non-system collection that raises 'not authorized' is skipped, not raised."""
        db = self._make_db_with_find_handlers({
            "secret_audit": Exception(
                "not authorized on db to execute command find: secret_audit"
            ),
            "users": [{"_id": 1, "name": "Alice"}],
        })

        schema = self.detector.detect_schema(db)

        assert "secret_audit" not in schema
        assert "users" in schema

    def test_detect_schema_skips_collection_on_lowercase_unauthorized_error(self) -> None:
        """The 'Unauthorized' marker (capitalised codeName) also triggers skip."""
        db = self._make_db_with_find_handlers({
            "restricted": Exception(
                "OperationFailure: command find requires authentication, full error: ..."
            ),
            "users": [{"_id": 1, "name": "Alice"}],
        })

        schema = self.detector.detect_schema(db)

        assert "restricted" not in schema
        assert "users" in schema

    def test_detect_schema_still_raises_on_non_authz_find_failure(self) -> None:
        """Generic find() failures (non-authz) still raise SchemaDetectionError.

        Guards against accidentally silencing legitimate driver/network errors.
        """
        db = self._make_db_with_find_handlers({
            "broken_col": Exception("cursor error: connection reset by peer"),
        })

        with pytest.raises(SchemaDetectionError, match="Failed to sample collection 'broken_col'"):
            self.detector.detect_schema(db)

    # ── Regression — exact failing scenario from BUG-008 ─────────────────────

    def test_bug_008_regression_system_profile_unauthorized_does_not_block_user_collections(
        self,
    ) -> None:
        """Regression — exact failing shape from BUG-008 succeeds end-to-end.

        Before the fix, hitting ``system.profile`` raised an ``Unauthorized``
        error that aborted schema detection for the whole database. After the
        fix, ``system.profile`` is filtered out entirely and the user
        collection (``audit_logs``) is sampled successfully.
        """
        unauthorized_msg = (
            "not authorized on idcauditlog to execute command "
            "{ find: \"system.profile\", filter: {}, limit: 100, ... } "
            "'code': 13, 'codeName': 'Unauthorized'"
        )
        db = self._make_db_with_find_handlers({
            "system.profile": Exception(unauthorized_msg),
            "audit_logs": [
                {"_id": 1, "ts": "2026-05-07", "action": "login"},
                {"_id": 2, "ts": "2026-05-07", "action": "logout"},
            ],
        })

        schema = self.detector.detect_schema(db)

        assert "system.profile" not in schema
        assert "audit_logs" in schema
        field_names = {col.name for col in schema["audit_logs"]}
        assert {"_id", "ts", "action"} == field_names

