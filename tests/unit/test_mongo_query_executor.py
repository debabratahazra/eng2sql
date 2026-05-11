"""Unit tests for MongoQueryExecutor service (US-059 / EPIC-009)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from services.mongo_query_executor import (
    MongoQueryExecutor,
    _DEFAULT_RESULT_LIMIT,
    _needs_auto_limit,
    _strip_markdown_fences,
)
from utils.exceptions import QueryExecutionError


# ── _strip_markdown_fences() ─────────────────────────────────────────────────


class TestStripMarkdownFences:
    """Unit tests for the _strip_markdown_fences helper."""

    def test_strips_triple_backtick_json_fence(self) -> None:
        raw = '```json\n{"collection": "x", "pipeline": []}\n```'
        assert _strip_markdown_fences(raw) == '{"collection": "x", "pipeline": []}'

    def test_strips_plain_triple_backtick_fence(self) -> None:
        raw = '```\n{"collection": "x", "pipeline": []}\n```'
        assert _strip_markdown_fences(raw) == '{"collection": "x", "pipeline": []}'

    def test_leaves_plain_json_unchanged(self) -> None:
        raw = '{"collection": "x", "pipeline": []}'
        assert _strip_markdown_fences(raw) == raw

    def test_strips_leading_whitespace(self) -> None:
        raw = '  \n  {"collection": "x", "pipeline": []}\n  '
        assert _strip_markdown_fences(raw) == '{"collection": "x", "pipeline": []}'


# ── _needs_auto_limit() ───────────────────────────────────────────────────────


class TestNeedsAutoLimit:
    """Unit tests for the _needs_auto_limit helper."""

    def test_empty_pipeline_needs_limit(self) -> None:
        assert _needs_auto_limit([]) is True

    def test_match_only_needs_limit(self) -> None:
        assert _needs_auto_limit([{"$match": {"x": 1}}]) is True

    def test_pipeline_ending_with_limit_does_not_need_auto_limit(self) -> None:
        pipeline = [{"$match": {"x": 1}}, {"$limit": 50}]
        assert _needs_auto_limit(pipeline) is False

    def test_pipeline_ending_with_count_does_not_need_auto_limit(self) -> None:
        assert _needs_auto_limit([{"$count": "total"}]) is False

    def test_pipeline_ending_with_group_does_not_need_auto_limit(self) -> None:
        assert _needs_auto_limit([{"$group": {"_id": "$x"}}]) is False

    def test_pipeline_ending_with_facet_does_not_need_auto_limit(self) -> None:
        assert _needs_auto_limit([{"$facet": {}}]) is False


# ── MongoQueryExecutor.execute() — happy path ─────────────────────────────────


class TestMongoQueryExecutorHappyPath:
    """Happy-path tests for MongoQueryExecutor.execute()."""

    def setup_method(self) -> None:
        self.executor = MongoQueryExecutor()

    def _make_db(self, collection_name: str, documents: list[dict]) -> MagicMock:
        mock_col = MagicMock()
        mock_col.aggregate.return_value = iter(documents)
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_col)
        return mock_db

    def test_returns_dataframe(self) -> None:
        """execute() returns a pd.DataFrame."""
        db = self._make_db("users", [{"_id": 1, "name": "Alice"}])
        mql = '{"collection": "users", "pipeline": [{"$limit": 10}]}'
        result = self.executor.execute(db, mql)
        assert isinstance(result, pd.DataFrame)

    def test_columns_match_document_keys(self) -> None:
        """DataFrame columns match the top-level keys of returned documents."""
        db = self._make_db("orders", [{"_id": 1, "total": 50.0, "status": "paid"}])
        mql = '{"collection": "orders", "pipeline": [{"$limit": 1}]}'
        result = self.executor.execute(db, mql)
        assert set(result.columns) == {"_id", "total", "status"}

    def test_empty_result_returns_empty_dataframe(self) -> None:
        """execute() returns an empty DataFrame when the cursor is empty."""
        db = self._make_db("empty", [])
        mql = '{"collection": "empty", "pipeline": []}'
        result = self.executor.execute(db, mql)
        assert result.empty

    def test_auto_limit_appended_when_missing(self) -> None:
        """When no $limit stage exists, $limit: 1000 is appended to the pipeline."""
        mock_col = MagicMock()
        mock_col.aggregate.return_value = iter([{"_id": 1}])
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_col)

        mql = '{"collection": "logs", "pipeline": [{"$match": {"level": "error"}}]}'
        self.executor.execute(mock_db, mql)

        called_pipeline = mock_col.aggregate.call_args[0][0]
        assert called_pipeline[-1] == {"$limit": _DEFAULT_RESULT_LIMIT}

    def test_existing_limit_not_doubled(self) -> None:
        """When the pipeline ends with $limit, no extra $limit is appended."""
        mock_col = MagicMock()
        mock_col.aggregate.return_value = iter([{"_id": 1}])
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_col)

        mql = '{"collection": "logs", "pipeline": [{"$limit": 5}]}'
        self.executor.execute(mock_db, mql)

        called_pipeline = mock_col.aggregate.call_args[0][0]
        limit_stages = [s for s in called_pipeline if "$limit" in s]
        assert len(limit_stages) == 1
        assert limit_stages[0]["$limit"] == 5

    def test_strips_markdown_fences_before_parsing(self) -> None:
        """execute() succeeds even when the LLM wraps the JSON in backtick fences."""
        db = self._make_db("users", [{"_id": 1}])
        mql = '```json\n{"collection": "users", "pipeline": [{"$limit": 1}]}\n```'
        result = self.executor.execute(db, mql)
        assert isinstance(result, pd.DataFrame)

    def test_objectid_values_converted_to_str(self) -> None:
        """Non-primitive BSON values (ObjectId, etc.) are converted to str."""

        class FakeObjectId:
            def __str__(self) -> str:
                return "507f1f77bcf86cd799439011"

        db = self._make_db("col", [{"_id": FakeObjectId(), "name": "Alice"}])
        mql = '{"collection": "col", "pipeline": [{"$limit": 1}]}'
        result = self.executor.execute(db, mql)
        assert result["_id"].iloc[0] == "507f1f77bcf86cd799439011"

    def test_none_values_preserved(self) -> None:
        """None values (null BSON) pass through as-is."""
        db = self._make_db("col", [{"_id": 1, "optional": None}])
        mql = '{"collection": "col", "pipeline": [{"$limit": 1}]}'
        result = self.executor.execute(db, mql)
        assert result["optional"].iloc[0] is None


# ── MongoQueryExecutor.execute() — error paths ───────────────────────────────


class TestMongoQueryExecutorErrors:
    """Error-path and validation tests for MongoQueryExecutor.execute()."""

    def setup_method(self) -> None:
        self.executor = MongoQueryExecutor()

    def test_raises_on_invalid_json(self) -> None:
        """Malformed JSON raises QueryExecutionError."""
        with pytest.raises(QueryExecutionError, match="not valid JSON"):
            self.executor.execute(MagicMock(), "not json at all")

    def test_raises_on_non_dict_json(self) -> None:
        """A JSON array (not object) raises QueryExecutionError."""
        with pytest.raises(QueryExecutionError, match="JSON object"):
            self.executor.execute(MagicMock(), "[1, 2, 3]")

    def test_raises_on_missing_collection_key(self) -> None:
        """JSON without 'collection' raises QueryExecutionError."""
        with pytest.raises(QueryExecutionError, match="missing a 'collection' key"):
            self.executor.execute(MagicMock(), '{"pipeline": []}')

    def test_raises_on_empty_collection_name(self) -> None:
        """Empty collection string raises QueryExecutionError."""
        with pytest.raises(QueryExecutionError, match="missing a 'collection' key"):
            self.executor.execute(MagicMock(), '{"collection": "", "pipeline": []}')

    def test_raises_on_invalid_collection_name(self) -> None:
        """Collection name with special chars raises QueryExecutionError."""
        mql = '{"collection": "bad;name", "pipeline": []}'
        with pytest.raises(QueryExecutionError, match="Invalid collection name"):
            self.executor.execute(MagicMock(), mql)

    def test_raises_on_pipeline_not_a_list(self) -> None:
        """Non-list pipeline raises QueryExecutionError."""
        mql = '{"collection": "users", "pipeline": {"$match": {}}}'
        with pytest.raises(QueryExecutionError, match="must be a JSON array"):
            self.executor.execute(MagicMock(), mql)

    def test_raises_on_aggregate_failure(self) -> None:
        """pymongo error during aggregate() raises QueryExecutionError."""
        mock_col = MagicMock()
        mock_col.aggregate.side_effect = Exception("cursor failed")
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_col)

        mql = '{"collection": "logs", "pipeline": [{"$limit": 10}]}'
        with pytest.raises(QueryExecutionError, match="Failed to execute MQL"):
            self.executor.execute(mock_db, mql)

    @pytest.mark.parametrize(
        "name",
        [
            "valid_name",
            "my.collection",
            "col-2",
            "MyCollection123",
            "a",
        ],
    )
    def test_valid_collection_names_accepted(self, name: str) -> None:
        """Parametrised check that safe collection names pass validation."""
        mock_col = MagicMock()
        mock_col.aggregate.return_value = iter([])
        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_col)

        mql = f'{{"collection": "{name}", "pipeline": []}}'
        result = self.executor.execute(mock_db, mql)
        assert isinstance(result, pd.DataFrame)
