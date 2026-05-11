"""MongoDB schema detection service for Eng2SQL.

Samples documents from every collection in a database and infers a schema
(collection names + top-level field names + best-effort BSON type strings)
compatible with the shared TableSchema / SchemaColumn model.
"""
from __future__ import annotations

from models.config import SchemaColumn, TableSchema
from utils.exceptions import SchemaDetectionError
from utils.logger import get_logger

logger = get_logger(__name__)

# MongoDB internal/system collections that must never be sampled. They are
# exposed by ``list_collection_names()`` on some deployments but a typical
# application user lacks the privileges required to ``find`` against them
# (e.g. ``system.profile`` requires the ``dbAdmin`` role). Sampling them
# previously aborted the entire schema-detection step with a misleading
# "Unauthorized" error (BUG-008).
_SYSTEM_COLLECTION_PREFIX: str = "system."

# Substrings that identify a "not authorized" error message coming back from
# MongoDB. Used to detect privilege errors so that a single inaccessible
# collection does not abort schema detection for the entire database.
_UNAUTHORIZED_MARKERS: tuple[str, ...] = (
    "not authorized",
    "Unauthorized",
    "requires authentication",
)

# Mapping from Python / BSON built-in types to human-readable type strings
_BSON_TYPE_MAP: dict[str, str] = {
    "int": "Number",
    "float": "Number",
    "str": "String",
    "bool": "Boolean",
    "dict": "Object",
    "list": "Array",
    "ObjectId": "ObjectId",
    "datetime": "Date",
    "bytes": "Binary",
    "NoneType": "Null",
}


def _infer_type(value: object) -> str:
    """Return a human-readable type string for a Python / BSON value.

    Args:
        value: Any Python or BSON value sampled from a MongoDB document.

    Returns:
        A type string such as ``"String"``, ``"Number"``, or ``"Mixed"``.
    """
    type_name = type(value).__name__
    return _BSON_TYPE_MAP.get(type_name, "Mixed")


class MongoSchemaDetector:
    """Detects MongoDB schema by sampling documents from each collection."""

    def detect_schema(
        self,
        db: object,
        sample_size: int = 100,
    ) -> TableSchema:
        """Sample collections in a database and return a unified TableSchema.

        For each collection, up to *sample_size* documents are sampled. Top-level
        field names are unioned across all sampled documents, and the most common
        Python type for each field is recorded.

        Collections are treated as "tables" and top-level fields as "columns"
        to be compatible with the shared :data:`~models.config.TableSchema` type.

        Args:
            db: A ``pymongo.database.Database`` object.
            sample_size: Maximum number of documents to sample per collection.

        Returns:
            A :data:`~models.config.TableSchema` mapping collection names to
            lists of :class:`~models.config.SchemaColumn` instances.

        Raises:
            SchemaDetectionError: If the driver raises an exception.
        """
        try:
            collection_names: list[str] = db.list_collection_names()  # type: ignore[union-attr]
        except Exception as exc:  # noqa: BLE001
            raise SchemaDetectionError(
                f"Failed to list MongoDB collections: {exc}"
            ) from exc

        # BUG-008 — drop MongoDB internal/system collections (e.g.
        # ``system.profile``, ``system.views``, ``system.js``,
        # ``system.sessions``). These are surfaced by ``list_collection_names``
        # on some deployments but normal application users lack the privileges
        # required to ``find`` against them, which would otherwise abort the
        # entire schema-detection step with an "Unauthorized" error.
        skipped_system: list[str] = [
            name for name in collection_names
            if name.startswith(_SYSTEM_COLLECTION_PREFIX)
        ]
        if skipped_system:
            logger.info(
                "Skipping %d MongoDB system collection(s): %s",
                len(skipped_system),
                skipped_system,
            )
        collection_names = [
            name for name in collection_names
            if not name.startswith(_SYSTEM_COLLECTION_PREFIX)
        ]

        schema: TableSchema = {}

        for collection_name in sorted(collection_names):
            try:
                cursor = db[collection_name].find({}, limit=sample_size)  # type: ignore[index]
                documents = list(cursor)
            except Exception as exc:  # noqa: BLE001
                # BUG-008 — if the user lacks read privileges on a single
                # collection, log a warning and skip it instead of aborting
                # schema detection for the entire database. This matches the
                # behaviour of MongoDB Compass, which renders accessible
                # collections and grays out unauthorised ones.
                error_text = str(exc)
                if any(marker in error_text for marker in _UNAUTHORIZED_MARKERS):
                    logger.warning(
                        "Skipping collection '%s' — user is not authorised to "
                        "read it: %s",
                        collection_name,
                        error_text.splitlines()[0],
                    )
                    continue
                raise SchemaDetectionError(
                    f"Failed to sample collection '{collection_name}': {exc}"
                ) from exc

            # Union field names and track observed types
            field_types: dict[str, str] = {}
            for doc in documents:
                for field_name, value in doc.items():
                    if field_name not in field_types:
                        field_types[field_name] = _infer_type(value)
                    elif field_types[field_name] != _infer_type(value):
                        field_types[field_name] = "Mixed"

            columns: list[SchemaColumn] = [
                SchemaColumn(
                    name=field,
                    type=field_types[field],
                    nullable=True,
                    primary_key=(field == "_id"),
                )
                for field in field_types
            ]

            schema[collection_name] = columns
            logger.debug(
                "Collection '%s': %d fields from %d sampled documents",
                collection_name,
                len(columns),
                len(documents),
            )

        return schema
