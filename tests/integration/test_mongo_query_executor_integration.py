"""US-061 — Integration tests for ``MongoQueryExecutor`` against a real MongoDB container.

These tests exercise the live-MongoDB branches of
:class:`src.services.mongo_query_executor.MongoQueryExecutor` that mock-based
unit tests cannot cover (real pymongo aggregation cursor, real wire-protocol
query execution, real container teardown).

Tests are gated behind two markers:
- ``@pytest.mark.integration`` — skipped by the default unit-test invocation
  (``pytest -m "not integration"``).
- ``@pytest.mark.docker`` — additionally signals that a running Docker
  daemon is required; the ``mongo_container_db`` fixture skips automatically
  when Docker is unavailable.

Run with::

    pytest tests/integration/test_mongo_query_executor_integration.py -m docker -v

References:
    - US-061 (Sprint 13) — Docker-based MongoDB integration test.
    - docs/bug-reports/BUG-003-max-tokens-unsupported-parameter.md
    - src/services/mongo_query_executor.py
"""
from __future__ import annotations

import json
from typing import Generator

import pandas as pd
import pytest

from services.mongo_query_executor import MongoQueryExecutor
from utils.exceptions import QueryExecutionError


pytestmark = [pytest.mark.integration, pytest.mark.docker]


# ---------------------------------------------------------------------------
# Fixture: real MongoDB container
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def mongo_container_db() -> Generator[object, None, None]:
    """Spin up a real MongoDB 7 container for integration tests.

    Skips the test (rather than failing) when:
    - The optional ``testcontainers`` package is not installed.
    - The ``pymongo`` package is not installed.
    - The Docker daemon is not running / not reachable.

    Yields:
        A connected ``pymongo.database.Database`` object seeded with two
        collections (``orders`` and ``sensors``) for use by the tests.

    Notes:
        - Container is started **once per module** (scope="module") to keep
          integration runtime short.
        - Torn down automatically when the module finishes.
    """
    try:
        from testcontainers.mongodb import MongoDbContainer  # type: ignore[import-not-found]
    except ImportError:
        pytest.skip("testcontainers[mongo] not installed — skipping Docker MongoDB fixture")

    try:
        import pymongo  # type: ignore[import-not-found]
    except ImportError:
        pytest.skip("pymongo not installed — skipping Docker MongoDB fixture")

    try:
        container = MongoDbContainer("mongo:7.0")
        container.start()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Docker not available — skipping Docker MongoDB fixture: {exc}")

    try:
        connection_url = container.get_connection_url()
        client = pymongo.MongoClient(connection_url)
        db = client["testdb"]

        # Seed the orders collection
        db["orders"].insert_many(
            [
                {"customer": "Alice", "amount": 99.99, "status": "delivered"},
                {"customer": "Bob", "amount": 149.50, "status": "pending"},
                {"customer": "Carol", "amount": 49.00, "status": "delivered"},
            ]
        )

        # Seed the sensors collection (for pipeline-variety tests)
        db["sensors"].insert_many(
            [
                {"device": "sensor-1", "temp_c": 21.5},
                {"device": "sensor-2", "temp_c": 22.0},
                {"device": "sensor-3", "temp_c": 19.8},
            ]
        )

        yield db

        client.close()
    finally:
        try:
            container.stop()
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _mql(collection: str, pipeline: list[dict]) -> str:
    """Serialise collection + pipeline to the JSON string expected by the executor."""
    return json.dumps({"collection": collection, "pipeline": pipeline})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMongoQueryExecutorIntegration:
    """Live-MongoDB integration tests for :class:`MongoQueryExecutor`."""

    def test_simple_find_all_returns_dataframe(
        self, mongo_container_db: object
    ) -> None:
        """A ``$match: {}`` pipeline returns all seeded documents as a DataFrame."""
        executor = MongoQueryExecutor()
        mql = _mql("orders", [{"$match": {}}])
        df = executor.execute(mongo_container_db, mql)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "customer" in df.columns
        assert "amount" in df.columns
        assert "status" in df.columns

    def test_match_filter_returns_subset(
        self, mongo_container_db: object
    ) -> None:
        """A ``$match`` with a condition returns only matching documents."""
        executor = MongoQueryExecutor()
        mql = _mql("orders", [{"$match": {"status": "delivered"}}])
        df = executor.execute(mongo_container_db, mql)

        assert len(df) == 2
        assert set(df["status"].tolist()) == {"delivered"}

    def test_empty_pipeline_auto_limit_applied(
        self, mongo_container_db: object
    ) -> None:
        """An empty pipeline triggers the auto-limit guard and still returns data."""
        executor = MongoQueryExecutor()
        # Empty pipeline — executor should append {"$limit": 1000} automatically
        mql = _mql("sensors", [])
        df = executor.execute(mongo_container_db, mql)

        # All 3 seed documents are well below the 1000-doc auto-limit
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "device" in df.columns

    def test_group_stage_aggregates_correctly(
        self, mongo_container_db: object
    ) -> None:
        """A ``$group`` stage returns one row per group — no auto-limit added."""
        executor = MongoQueryExecutor()
        mql = _mql(
            "orders",
            [{"$group": {"_id": "$status", "count": {"$sum": 1}}}],
        )
        df = executor.execute(mongo_container_db, mql)

        # Two distinct statuses: delivered (2), pending (1)
        assert len(df) == 2
        status_counts = dict(zip(df["_id"], df["count"]))
        assert status_counts.get("delivered") == 2
        assert status_counts.get("pending") == 1

    def test_nonexistent_collection_returns_empty_dataframe(
        self, mongo_container_db: object
    ) -> None:
        """Querying a non-existent collection returns an empty DataFrame (MongoDB creates it lazily)."""
        executor = MongoQueryExecutor()
        mql = _mql("does_not_exist_xyz", [{"$match": {}}])
        df = executor.execute(mongo_container_db, mql)

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_invalid_collection_name_raises_query_execution_error(
        self, mongo_container_db: object
    ) -> None:
        """An unsafe collection name is rejected before any DB call is made."""
        executor = MongoQueryExecutor()
        mql = json.dumps(
            {"collection": "orders; DROP DATABASE testdb;", "pipeline": []}
        )
        with pytest.raises(QueryExecutionError, match="Invalid collection name"):
            executor.execute(mongo_container_db, mql)

    def test_objectid_converted_to_string(
        self, mongo_container_db: object
    ) -> None:
        """The ``_id`` field (ObjectId) is converted to str in the result DataFrame."""
        executor = MongoQueryExecutor()
        mql = _mql("orders", [{"$match": {}}, {"$limit": 1}])
        df = executor.execute(mongo_container_db, mql)

        assert len(df) == 1
        # ObjectId → str conversion so Streamlit can display it
        assert isinstance(df["_id"].iloc[0], str)
