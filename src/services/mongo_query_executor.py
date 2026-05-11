"""MongoDB MQL query execution service for Eng2SQL.

Parses a structured JSON MQL string produced by the LLM, validates the
collection name and aggregation pipeline, executes the pipeline against a
connected pymongo database, and returns the results as a pandas DataFrame.

Security contract
-----------------
* No ``eval()``, ``exec()``, or shell calls — ever.
* ``json.loads()`` is the sole parser.
* Collection names are validated against ``_SAFE_COLLECTION_RE`` before
  being passed to pymongo.
* Results are capped at ``_DEFAULT_RESULT_LIMIT`` documents unless the
  pipeline already contains a terminal limit/grouping stage.
"""
from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

import pandas as pd

from utils.exceptions import QueryExecutionError
from utils.logger import get_logger

if TYPE_CHECKING:
    pass  # pymongo is an optional dependency — imported lazily below

logger = get_logger(__name__)

# Maximum number of result documents returned when the pipeline has no
# explicit ``$limit`` / ``$count`` / ``$group`` / ``$facet`` / ``$bucketAuto``
# terminal stage.
_DEFAULT_RESULT_LIMIT: int = 1_000

# Aggregation stages that produce a finite or summarised result set.  When
# the last stage is one of these, the auto-limit guard is skipped.
_TERMINAL_STAGES: frozenset[str] = frozenset(
    {"$limit", "$count", "$group", "$facet", "$bucketAuto", "$bucket"}
)

# Collection names are restricted to alphanumerics plus ``_``, ``.``, ``-``.
# This prevents path traversal and command-injection attacks if the collection
# name is ever interpolated into an error message or log line.
_SAFE_COLLECTION_RE: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_.\-]+$")


def _strip_markdown_fences(text: str) -> str:
    """Remove leading/trailing markdown code fences from *text*.

    The LLM sometimes wraps JSON output in triple-backtick fences even when
    instructed not to.  This function strips them so ``json.loads()`` can
    parse the remaining text.

    Args:
        text: Raw string from the LLM.

    Returns:
        The same string with markdown fences removed.
    """
    stripped = text.strip()
    # Remove opening fence (``` or ```json)
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
    # Remove closing fence
    stripped = re.sub(r"\s*```$", "", stripped.strip())
    return stripped.strip()


def _needs_auto_limit(pipeline: list[dict]) -> bool:
    """Return ``True`` if an automatic ``$limit`` stage should be appended.

    A limit is added when the pipeline is empty or when its last stage is not
    one of the "terminal" stages that already bound the result set.

    Args:
        pipeline: The aggregation pipeline list.

    Returns:
        ``True`` when an auto-limit should be appended.
    """
    if not pipeline:
        return True
    last_stage = pipeline[-1]
    last_op = next(iter(last_stage), "")  # first key of the last stage dict
    return last_op not in _TERMINAL_STAGES


class MongoQueryExecutor:
    """Executes a structured MQL aggregation pipeline against a pymongo database.

    The MQL string must be a JSON object produced by the LLM in the format::

        {
          "collection": "collection_name",
          "pipeline": [
            {"$match": {"field": "value"}},
            {"$sort": {"ts": -1}},
            {"$limit": 50}
          ]
        }
    """

    def execute(self, db: object, mql_json: str) -> pd.DataFrame:
        """Parse *mql_json*, execute the pipeline, and return results.

        Args:
            db: A connected ``pymongo.database.Database`` object.
            mql_json: A JSON string (possibly wrapped in markdown fences)
                containing ``collection`` and ``pipeline`` keys.

        Returns:
            A ``pd.DataFrame`` with one row per document.  The ``_id`` column
            (ObjectId) is converted to ``str`` for display compatibility.

        Raises:
            QueryExecutionError: If the JSON is malformed, the collection name
                is invalid, the pipeline is not a list, or the pymongo driver
                raises an exception during execution.
        """
        # ── 1. Strip markdown fences ──────────────────────────────────────────
        clean = _strip_markdown_fences(mql_json)

        # ── 2. Parse JSON ─────────────────────────────────────────────────────
        try:
            payload: dict[str, Any] = json.loads(clean)
        except json.JSONDecodeError as exc:
            raise QueryExecutionError(
                f"MQL query is not valid JSON: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise QueryExecutionError(
                "MQL query must be a JSON object with 'collection' and 'pipeline' keys."
            )

        # ── 3. Validate collection name ───────────────────────────────────────
        collection_name: str = payload.get("collection", "")
        if not isinstance(collection_name, str) or not collection_name:
            raise QueryExecutionError(
                "MQL query is missing a 'collection' key (must be a non-empty string)."
            )
        if not _SAFE_COLLECTION_RE.match(collection_name):
            raise QueryExecutionError(
                f"Invalid collection name '{collection_name}'. "
                "Only alphanumerics, underscores, dots, and hyphens are allowed."
            )

        # ── 4. Validate pipeline ──────────────────────────────────────────────
        pipeline: list[dict] = payload.get("pipeline", [])
        if not isinstance(pipeline, list):
            raise QueryExecutionError(
                "MQL 'pipeline' must be a JSON array of aggregation stage objects."
            )

        # ── 5. Auto-limit guard ───────────────────────────────────────────────
        if _needs_auto_limit(pipeline):
            pipeline = [*pipeline, {"$limit": _DEFAULT_RESULT_LIMIT}]
            logger.debug(
                "Auto-limit: appended {'$limit': %d} to pipeline for '%s'.",
                _DEFAULT_RESULT_LIMIT,
                collection_name,
            )

        # ── 6. Execute ────────────────────────────────────────────────────────
        logger.info(
            "Executing MQL: collection='%s', pipeline=%s",
            collection_name,
            pipeline,
        )
        try:
            cursor = db[collection_name].aggregate(pipeline)  # type: ignore[index]
            documents: list[dict] = list(cursor)
        except Exception as exc:  # noqa: BLE001
            raise QueryExecutionError(
                f"Failed to execute MQL on collection '{collection_name}': {exc}"
            ) from exc

        # ── 7. Convert to DataFrame ───────────────────────────────────────────
        if not documents:
            return pd.DataFrame()

        # Convert ObjectId (and any other non-JSON-serialisable BSON types) to
        # str so that st.dataframe can render the column without errors.
        safe_docs: list[dict] = []
        for doc in documents:
            safe_doc = {}
            for key, value in doc.items():
                # ObjectId, Timestamp, Binary, etc. — fall back to str()
                if not isinstance(value, (str, int, float, bool, type(None))):
                    value = str(value)
                safe_doc[key] = value
            safe_docs.append(safe_doc)

        df = pd.DataFrame(safe_docs)
        logger.info(
            "MQL returned %d rows, %d columns from '%s'.",
            len(df),
            len(df.columns),
            collection_name,
        )
        return df
