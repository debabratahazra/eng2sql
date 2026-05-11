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
from utils.network import LOOPBACK_HOSTS, is_wsl2, probe_reachable_host

logger = get_logger(__name__)

_SYSTEM_DATABASES: frozenset[str] = frozenset(
    {
        # MySQL system schemas
        "information_schema",
        "performance_schema",
        "mysql",
        "sys",
        # PostgreSQL system / template databases (EPIC-009 / US-046)
        "postgres",
        "template0",
        "template1",
    }
)

# Per-dialect query used by ``DBConnector.list_databases`` (EPIC-009 / US-046).
_LIST_DB_QUERIES: dict[str, str] = {
    "mysql": "SHOW DATABASES",
    "postgresql": "SELECT datname FROM pg_database WHERE datistemplate = false",
}


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
            # WSL2 fail-fast: when running inside WSL2 against a loopback host
            # the Windows-side DB is unreachable via WSL2's loopback adapter.
            # Probe the host first; if no address answers within 1 s, raise a
            # clear actionable error instead of waiting for the SQLAlchemy
            # connect_timeout to elapse. Mirrors the BUG-006 fix from
            # ``mongo_connector``; extracted to ``utils.network`` in US-050.
            host_lower = (config.host or "").lower()
            if host_lower in LOOPBACK_HOSTS and is_wsl2():
                probed = probe_reachable_host(config.host, config.port, timeout_s=1.0)
                if probed == config.host:
                    raise DatabaseConnectionError(
                        f"Could not reach {config.dialect} at {config.host}:{config.port} "
                        "from WSL2. WSL2 cannot reach services bound to 'localhost' / "
                        "127.0.0.1 on the Windows host. Bind the database to 0.0.0.0 "
                        "or use the Windows host IP. "
                        "See: https://learn.microsoft.com/windows/wsl/networking"
                    )

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
        """Return non-system database names visible to the connected user.

        Dispatches on ``engine.dialect.name``:

        - ``mysql``      → executes ``SHOW DATABASES`` and filters out the four
          standard MySQL system schemas (``information_schema``,
          ``performance_schema``, ``mysql``, ``sys``).
        - ``postgresql`` → executes
          ``SELECT datname FROM pg_database WHERE datistemplate = false``
          and filters out ``postgres``, ``template0``, ``template1`` (EPIC-009).

        Args:
            engine: A server-level SQLAlchemy engine (no database selected).

        Returns:
            Sorted list of user-accessible database names.

        Raises:
            DatabaseConnectionError: If the query fails due to a connection or
                permission issue.
            NotImplementedError: If the engine's dialect is not supported.
        """
        dialect_name = engine.dialect.name
        query = _LIST_DB_QUERIES.get(dialect_name)
        if query is None:
            raise NotImplementedError(
                f"list_databases is not implemented for dialect {dialect_name!r}. "
                f"Supported: {sorted(_LIST_DB_QUERIES)}."
            )
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(query)).fetchall()
        except SQLAlchemyError as exc:
            raise DatabaseConnectionError(
                f"Failed to list databases: {exc}"
            ) from exc
        return sorted(row[0] for row in rows if row[0] not in _SYSTEM_DATABASES)
