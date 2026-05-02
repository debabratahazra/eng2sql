"""Database connector service for Eng2SQL.

Manages SQLAlchemy engine creation, connection testing, and read-only query execution.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from models.config import DBConfig
from utils.exceptions import DatabaseConnectionError, QueryExecutionError
from utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_DATABASES: frozenset[str] = frozenset(
    {"information_schema", "performance_schema", "mysql", "sys"}
)


class DBConnector:
    """Creates and manages SQLAlchemy database connections."""

    def create_engine(self, config: DBConfig) -> Engine:
        """Create a SQLAlchemy engine from the provided configuration.

        Args:
            config: Database connection parameters.

        Returns:
            A configured SQLAlchemy :class:`~sqlalchemy.engine.Engine`.

        Raises:
            DatabaseConnectionError: If the connection cannot be established.
        """
        try:
            engine = create_engine(
                config.connection_url,
                pool_pre_ping=True,
                pool_size=2,
                max_overflow=2,
                connect_args={"connect_timeout": config.connect_timeout},
            )
            # Verify the connection is actually usable
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except OperationalError as exc:
            raise DatabaseConnectionError(
                f"Could not connect to {config.host}:{config.port}/{config.database} — {exc}"
            ) from exc
        except SQLAlchemyError as exc:
            raise DatabaseConnectionError(
                f"Database error during connection: {exc}"
            ) from exc

        logger.debug(
            "Connected to %s:%s/%s as %s",
            config.host,
            config.port,
            config.database,
            config.user,
        )
        return engine

    def test_connection(self, engine: Engine) -> bool:
        """Ping the database to verify the engine is still alive.

        Args:
            engine: An existing SQLAlchemy engine.

        Returns:
            ``True`` if the database responds, ``False`` otherwise.
        """
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def execute_query(self, engine: Engine, sql: str) -> pd.DataFrame:
        """Execute a SQL SELECT statement and return results as a DataFrame.

        Only SELECT statements are permitted. Any other statement type raises an error.

        Args:
            engine: A connected SQLAlchemy engine.
            sql: The SQL SELECT statement to execute.

        Returns:
            A :class:`pandas.DataFrame` containing the query results.

        Raises:
            ValueError: If the SQL is not a SELECT statement.
            QueryExecutionError: If the query fails at the database level.
        """
        normalised = sql.strip().upper()
        if not normalised.startswith("SELECT"):
            raise ValueError(
                "Only SELECT statements are permitted. "
                f"Received: {sql[:50]!r}…"
            )

        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                columns = list(result.keys())
            return pd.DataFrame(rows, columns=columns)
        except SQLAlchemyError as exc:
            raise QueryExecutionError(
                f"Query execution failed: {exc}"
            ) from exc

    def list_databases(self, engine: Engine) -> list[str]:
        """Return non-system database names visible to the connected MySQL user.

        Executes ``SHOW DATABASES`` and filters out the four standard MySQL
        system schemas: ``information_schema``, ``performance_schema``,
        ``mysql``, and ``sys``.

        Args:
            engine: A server-level SQLAlchemy engine (no database selected).

        Returns:
            Sorted list of user-accessible database names.

        Raises:
            DatabaseConnectionError: If the query fails due to a connection or
                permission issue.
        """
        try:
            with engine.connect() as conn:
                rows = conn.execute(text("SHOW DATABASES")).fetchall()
        except SQLAlchemyError as exc:
            raise DatabaseConnectionError(
                f"Failed to list databases: {exc}"
            ) from exc
        return sorted(row[0] for row in rows if row[0] not in _SYSTEM_DATABASES)
