"""Sidebar Streamlit component for Eng2SQL.

Renders a database-type radio selector (MySQL / MongoDB) plus the two-step
connection flow for the chosen engine:
  MySQL:   Step 1 — server credentials -> Connect -> discover databases
           Step 2 — database dropdown  -> Select Database -> activate engine + detect schema
  MongoDB: Step 1 — server credentials -> Connect -> discover databases
           Step 2 — database dropdown  -> Select Database -> get_database + detect schema
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
from typing import Callable

import streamlit as st

from models.config import DBConfig, MongoConfig
from services.db_connector import DBConnector
from services.mongo_connector import MongoDBConnector
from services.mongo_schema_detector import MongoSchemaDetector
from services.schema_detector import SchemaDetector
from utils.exceptions import DatabaseConnectionError, SchemaDetectionError
from utils.logger import get_logger

logger = get_logger(__name__)

# MySQL session-state keys cleared on reconnect or db_type change
_MYSQL_KEYS: tuple[str, ...] = (
    "db_server_engine",
    "available_databases",
    "selected_database",
    "db_engine",
    "detected_schema",
    "_db_password",
    "step1_status",
    "step2_status",
)

# PostgreSQL session-state keys cleared on reconnect or db_type change (EPIC-009 / US-045)
_PG_KEYS: tuple[str, ...] = (
    "pg_server_engine",
    "pg_available_databases",
    "pg_selected_database",
    "pg_engine",
    "detected_schema",
    "_pg_password",
    "pg_step1_status",
    "pg_step2_status",
)

# MongoDB session-state keys cleared on reconnect or db_type change
_MONGO_KEYS: tuple[str, ...] = (
    "mongo_client",
    "mongo_available_databases",
    "mongo_selected_database",
    "mongo_db",
    "detected_schema",
    "mongo_step1_status",
    "mongo_step2_status",
    "mongo_input_mode",
    "mongo_raw_uri",
)


def _clear_server_state() -> None:
    """Remove all MySQL server-connection-dependent keys from session state."""
    for key in _MYSQL_KEYS:
        st.session_state.pop(key, None)


def _clear_pg_state() -> None:
    """Remove all PostgreSQL connection-dependent keys from session state."""
    for key in _PG_KEYS:
        st.session_state.pop(key, None)


def _clear_mongo_state() -> None:
    """Remove all MongoDB connection-dependent keys from session state."""
    for key in _MONGO_KEYS:
        st.session_state.pop(key, None)


def _close_mongo_client() -> None:
    """Close the active MongoClient stored in session state, if any.

    Calling ``client.close()`` stops pymongo's background monitor thread
    immediately.  Without this, every failed or superseded Connect attempt
    leaves a zombie thread that holds an open socket to MongoDB.  When enough
    zombie threads accumulate they exhaust MongoDB's connection pool and
    subsequent hello handshakes never get a response, causing
    ``ServerSelectionTimeoutError`` with ``rtt: None`` even though the server
    is healthy (Streamlit bug reproduction path).
    """
    client = st.session_state.get("mongo_client")
    if client is not None:
        try:
            client.close()
        except Exception:  # noqa: BLE001
            pass


# US-051: _RelationalDialectConfig consolidates duplicated MySQL / PostgreSQL Step 1+2 code.

@dataclasses.dataclass(frozen=True)
class _RelationalDialectConfig:
    """Per-dialect config for shared relational Step 1 / Step 2 sidebar rendering."""

    host_key: str
    port_key: str
    user_key: str
    password_key: str
    server_engine_key: str
    available_dbs_key: str
    current_db_key: str
    engine_key: str
    step1_status_key: str
    step2_status_key: str
    host_widget_key: str | None
    port_widget_key: str | None
    user_widget_key: str | None
    password_widget_key: str | None
    connect_btn_key: str
    selectbox_key: str
    confirm_btn_key: str
    default_port: int
    dialect: str
    log_dialect: str
    clear_fn: Callable[[], None]
    sslmode_options: tuple[str, ...] | None = None
    sslmode_key: str | None = None
    sslmode_widget_key: str | None = None
    default_sslmode: str | None = None
    admin_db_key: str | None = None
    admin_db_widget_key: str | None = None
    default_admin_db: str | None = None


_MYSQL_CFG = _RelationalDialectConfig(
    host_key="db_host", port_key="db_port", user_key="db_user", password_key="_db_password",
    server_engine_key="db_server_engine", available_dbs_key="available_databases",
    current_db_key="selected_database", engine_key="db_engine",
    step1_status_key="step1_status", step2_status_key="step2_status",
    host_widget_key=None, port_widget_key=None, user_widget_key=None, password_widget_key=None,
    connect_btn_key="mysql_connect",
    selectbox_key="mysql_db_select", confirm_btn_key="mysql_db_confirm",
    default_port=3306, dialect="mysql", log_dialect="MySQL", clear_fn=_clear_server_state,
)

_PG_CFG = _RelationalDialectConfig(
    host_key="pg_host", port_key="pg_port", user_key="pg_user", password_key="_pg_password",
    server_engine_key="pg_server_engine", available_dbs_key="pg_available_databases",
    current_db_key="pg_selected_database", engine_key="pg_engine",
    step1_status_key="pg_step1_status", step2_status_key="pg_step2_status",
    host_widget_key="pg_host_input", port_widget_key="pg_port_input",
    user_widget_key="pg_user_input", password_widget_key="pg_password_input",
    connect_btn_key="pg_connect", selectbox_key="pg_db_select", confirm_btn_key="pg_db_confirm",
    default_port=5432, dialect="postgresql", log_dialect="PostgreSQL", clear_fn=_clear_pg_state,
    sslmode_options=("disable", "allow", "prefer", "require", "verify-ca", "verify-full"),
    sslmode_key="pg_sslmode", sslmode_widget_key="pg_sslmode_input", default_sslmode="prefer",
    admin_db_key="pg_admin_db", admin_db_widget_key="pg_admin_db_input",
    default_admin_db="postgres",
)


def _ca_bundle_available() -> bool:
    """Return True when a CA bundle reachable to libpq exists.

    Resolution order (US-056):
      1. ``PGSSLROOTCERT`` env var must point at an existing file
      2. ``~/.postgresql/root.crt`` must exist
      3. ``certifi.where()`` fallback if certifi is installed
    """
    env_path = os.environ.get("PGSSLROOTCERT")
    if env_path and pathlib.Path(env_path).is_file():
        return True
    default_path = pathlib.Path.home() / ".postgresql" / "root.crt"
    if default_path.is_file():
        return True
    try:
        import certifi  # type: ignore[import-not-found]

        # Excluded: certifi is an optional runtime dep; unreachable in CI/tests where certifi is absent.
        return pathlib.Path(certifi.where()).is_file()  # pragma: no cover
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# US-071: Pure-logic helpers extracted from rendering methods.
# These functions have zero Streamlit dependencies and are fully unit-testable.
# ---------------------------------------------------------------------------


def _validate_relational_inputs(
    host: str,
    user: str,
    password: str,
    admin_db: str | None,
) -> tuple[str, str] | None:
    """Validate Step 1 connection form inputs before attempting a DB connection.

    Args:
        host: Database server hostname.
        user: Database username.
        password: Database password.
        admin_db: Optional admin database name (PostgreSQL only; ``None`` for MySQL).

    Returns:
        ``None`` if all inputs are valid.
        A ``("warning", message)`` tuple if any required field is missing or invalid.
    """
    if not all([host, user, password]):
        return ("warning", "Please fill in host, user and password.")
    if admin_db is not None and not (admin_db or "").strip():
        return ("warning", "Admin DB cannot be empty.")
    return None


def _build_relational_config(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    dialect: str,
    sslmode: str | None,
) -> DBConfig:
    """Construct a :class:`~models.config.DBConfig` from individual connection parameters.

    Args:
        host: Database server hostname.
        port: Database server port (1–65535).
        user: Database username.
        password: Database password.
        database: Target database name (or admin DB for Step 1 discovery).
        dialect: SQL dialect identifier (``"mysql"`` or ``"postgresql"``).
        sslmode: Optional SSL mode string (PostgreSQL only; ``None`` for MySQL).

    Returns:
        A fully initialised :class:`~models.config.DBConfig` instance.
    """
    return DBConfig(
        host=host, port=port, user=user, password=password,
        database=database, dialect=dialect, sslmode=sslmode,
    )


def _format_connect_success(host: str, n: int) -> str:
    """Format a human-readable server connection success message.

    Args:
        host: Hostname of the connected server.
        n: Number of databases discovered on that server.

    Returns:
        Markdown-formatted success string, e.g.
        ``"Connected to **localhost** - 3 databases found"``.
    """
    plural = "s" if n != 1 else ""
    return f"Connected to **{host}** - {n} database{plural} found"


def _select_default_index(available: list[str], current: str | None) -> int:
    """Return the list index of *current* in *available*, falling back to 0.

    Args:
        available: Ordered list of option strings shown in a selectbox.
        current: The currently persisted selection (may be ``None`` or absent).

    Returns:
        Zero-based index of *current* in *available*, or ``0`` when not found.
    """
    if current is not None and current in available:
        return available.index(current)
    return 0


def _validate_mongo_fields_inputs(
    host: str,
    username: str,
    password: str,
    no_auth: bool,
) -> tuple[str, str] | None:
    """Validate MongoDB Fields-mode Step 1 credential inputs.

    Args:
        host: MongoDB server hostname or IP address.
        username: MongoDB username (ignored when *no_auth* is ``True``).
        password: MongoDB password (ignored when *no_auth* is ``True``).
        no_auth: ``True`` when the user selected ``"None / No Auth"`` mechanism.

    Returns:
        ``None`` if all inputs are valid.
        A ``("warning", message)`` tuple if a required field is missing.
    """
    if not host:
        return ("warning", "Please fill in the host.")
    if not no_auth and not (username and password):
        return (
            "warning",
            "Please fill in username and password (or select None / No Auth).",
        )
    return None


def _build_mongo_config(
    host: str,
    port: int,
    username: str,
    password: str,
    auth_source: str,
    auth_mechanism: str,
) -> MongoConfig:
    """Construct a :class:`~models.config.MongoConfig` from individual credentials.

    Args:
        host: MongoDB server hostname.
        port: MongoDB server port (1–65535).
        username: MongoDB username (empty string for unauthenticated access).
        password: MongoDB password (empty string for unauthenticated access).
        auth_source: Authentication source database (typically ``"admin"``).
        auth_mechanism: Authentication mechanism string (e.g. ``"SCRAM-SHA-256"``).

    Returns:
        A fully initialised :class:`~models.config.MongoConfig` instance.
    """
    return MongoConfig(
        host=host, port=port, username=username, password=password,
        auth_source=auth_source, auth_mechanism=auth_mechanism,
    )


class SidebarComponent:
    """Renders the database-type radio and the corresponding connection sidebar."""

    def __init__(self, connector: DBConnector) -> None:
        """Initialise the sidebar with a DBConnector instance.

        Args:
            connector: The MySQL database connector service.
        """
        self._connector = connector
        self._detector = SchemaDetector()
        self._mongo_connector = MongoDBConnector()
        self._mongo_detector = MongoSchemaDetector()

    def render(self) -> None:
        """Render the sidebar with db-type radio and relevant connection form.

        Populates the following session-state keys on success (MySQL):
        - ``db_server_engine`` — server-level engine (Step 1)
        - ``available_databases`` — list of user-accessible databases (Step 1)
        - ``db_engine`` — database-level engine (Step 2)
        - ``selected_database`` — chosen database name (Step 2)
        - ``detected_schema`` — introspected schema map (Step 2)

        Populates the following session-state keys on success (MongoDB):
        - ``mongo_client`` — server-level MongoClient (Step 1)
        - ``mongo_available_databases`` — list of databases (Step 1)
        - ``mongo_db`` — pymongo Database object (Step 2)
        - ``mongo_selected_database`` — chosen database name (Step 2)
        - ``detected_schema`` — introspected schema map (Step 2)
        """
        with st.sidebar:
            st.header("Configuration")

            # ── DB type selector ──────────────────────────────────────────────
            prev_type = st.session_state.get("db_type", "MySQL")
            db_type = st.radio(
                "Database type",
                options=["MySQL", "PostgreSQL", "MongoDB"],
                index=["MySQL", "PostgreSQL", "MongoDB"].index(prev_type)
                if prev_type in ("MySQL", "PostgreSQL", "MongoDB")
                else 0,
                horizontal=True,
            )

            # Clear downstream state when the user switches engine type
            if db_type != prev_type:
                _clear_server_state()
                _clear_pg_state()
                _close_mongo_client()
                _clear_mongo_state()

            st.session_state["db_type"] = db_type

            st.divider()

            if db_type == "MySQL":
                st.subheader("MySQL Live Database")
                self._render_step1()
                self._render_step2()
            elif db_type == "PostgreSQL":
                st.subheader("PostgreSQL Live Database")
                self._render_pg_step1()
                self._render_pg_step2()
            else:
                st.subheader("MongoDB Live Database")
                self._render_mongo_step1()
                self._render_mongo_step2()

    # ── MySQL Step 1 / Step 2 (thin wrappers around the shared relational renderer) ─────

    def _render_step1(self) -> None:
        """Render MySQL Step 1: server credentials form and Connect button."""
        self._render_relational_step1(_MYSQL_CFG)

    def _render_step2(self) -> None:
        """Render MySQL Step 2: database dropdown and Select Database button."""
        self._render_relational_step2(_MYSQL_CFG)

    # ── PostgreSQL Step 1 / Step 2 (thin wrappers) ───────────────────────────

    def _render_pg_step1(self) -> None:
        """Render PostgreSQL Step 1: server credentials form and Connect button."""
        self._render_relational_step1(_PG_CFG)

    def _render_pg_step2(self) -> None:
        """Render PostgreSQL Step 2: database dropdown and Select Database button."""
        self._render_relational_step2(_PG_CFG)

    # ── Shared relational Step 1 ──────────────────────────────────────────────

    def _render_relational_step1(self, cfg: _RelationalDialectConfig) -> None:
        """Render the shared Step 1 connection form for any relational dialect.

        Args:
            cfg: Dialect-specific configuration (use ``_MYSQL_CFG`` or ``_PG_CFG``).
        """
        st.markdown("**Step 1 — Connect to server**")

        host = st.text_input(
            "Host", value=st.session_state.get(cfg.host_key, "localhost"),
            key=cfg.host_widget_key,
        )
        port = st.number_input(
            "Port", value=int(st.session_state.get(cfg.port_key, cfg.default_port)),
            min_value=1, max_value=65535, key=cfg.port_widget_key,
        )
        user = st.text_input(
            "User", value=st.session_state.get(cfg.user_key, ""),
            key=cfg.user_widget_key,
        )
        password = st.text_input("Password", type="password", key=cfg.password_widget_key)

        # ── PostgreSQL-only extras (sslmode + admin DB) ───────────────────────
        sslmode: str | None = None
        admin_db: str | None = None
        if cfg.sslmode_options and cfg.sslmode_key:
            opts = list(cfg.sslmode_options)
            sslmode = st.selectbox(
                "SSL mode", options=opts,
                index=opts.index(st.session_state.get(cfg.sslmode_key, cfg.default_sslmode or opts[0])),
                key=cfg.sslmode_widget_key,
            )
            if sslmode in ("verify-ca", "verify-full") and not _ca_bundle_available():
                st.warning(
                    "verify-ca/verify-full requires a CA bundle. Set the PGSSLROOTCERT "
                    "env var or place one at ~/.postgresql/root.crt."
                )
        if cfg.admin_db_key:
            admin_db = st.text_input(
                "Admin DB",
                value=st.session_state.get(cfg.admin_db_key, cfg.default_admin_db or "postgres"),
                key=cfg.admin_db_widget_key,
                help=(
                    "Database used solely to enumerate other databases. Override if your "
                    "provider has disabled `postgres`."
                ),
            )

        if st.button("Connect", type="primary", key=cfg.connect_btn_key):
            cfg.clear_fn()
            validation_error = _validate_relational_inputs(host, user, password, admin_db)
            if validation_error is not None:
                st.session_state[cfg.step1_status_key] = validation_error
            else:
                st.session_state[cfg.host_key] = host
                st.session_state[cfg.port_key] = int(port)
                st.session_state[cfg.user_key] = user
                st.session_state[cfg.password_key] = password
                if sslmode is not None and cfg.sslmode_key:
                    st.session_state[cfg.sslmode_key] = sslmode
                if admin_db is not None and cfg.admin_db_key:
                    st.session_state[cfg.admin_db_key] = admin_db

                db_for_connect = admin_db or ""
                config = _build_relational_config(
                    host=host, port=int(port), user=user, password=password,
                    database=db_for_connect, dialect=cfg.dialect, sslmode=sslmode,
                )
                with st.spinner("Connecting to server..."):
                    try:
                        server_engine = self._connector.create_engine(config)
                        databases = self._connector.list_databases(server_engine)
                        st.session_state[cfg.server_engine_key] = server_engine
                        st.session_state[cfg.available_dbs_key] = databases
                        n = len(databases)
                        st.session_state[cfg.step1_status_key] = (
                            "success",
                            _format_connect_success(host, n),
                        )
                        logger.info(
                            "UI: connected to %s server %s; %d databases found",
                            cfg.log_dialect, host, n,
                        )
                    except DatabaseConnectionError as exc:
                        st.session_state[cfg.step1_status_key] = (
                            "error", f"Connection failed: {exc}"
                        )
                        logger.warning(
                            "UI: %s server connection failed: %s", cfg.log_dialect, exc
                        )

        self._render_status(cfg.step1_status_key)

    # ── Shared relational Step 2 ──────────────────────────────────────────────

    def _render_relational_step2(self, cfg: _RelationalDialectConfig) -> None:
        """Render the shared Step 2 database-selection form for any relational dialect.

        Args:
            cfg: Dialect-specific configuration (use ``_MYSQL_CFG`` or ``_PG_CFG``).
        """
        if st.session_state.get(cfg.server_engine_key) is None:
            return

        st.markdown("---")
        st.markdown("**Step 2 - Select database**")

        available: list[str] = st.session_state.get(cfg.available_dbs_key, [])
        if not available:
            st.warning("No accessible databases found for this user")
            return

        current = st.session_state.get(cfg.current_db_key)
        default_index = _select_default_index(available, current)
        selected = st.selectbox(
            "Select a database", options=available, index=default_index,
            key=cfg.selectbox_key,
        )

        if st.button("Select Database", type="secondary", key=cfg.confirm_btn_key):
            password = st.session_state.get(cfg.password_key, "")
            if not password:
                st.session_state[cfg.step2_status_key] = (
                    "warning",
                    "Session credentials expired - please reconnect in Step 1.",
                )
            else:
                sslmode_val = (
                    st.session_state.get(cfg.sslmode_key, "prefer")
                    if cfg.sslmode_key else None
                )
                config = _build_relational_config(
                    host=st.session_state.get(cfg.host_key, ""),
                    port=int(st.session_state.get(cfg.port_key, cfg.default_port)),
                    user=st.session_state.get(cfg.user_key, ""),
                    password=password,
                    database=selected,
                    dialect=cfg.dialect,
                    sslmode=sslmode_val,
                )
                old_engine = st.session_state.get(cfg.engine_key)
                if old_engine is not None:
                    old_engine.dispose()
                    st.session_state.pop(cfg.engine_key, None)
                    st.session_state.pop("detected_schema", None)

                with st.spinner(f"Connecting to **{selected}**..."):
                    try:
                        engine = self._connector.create_engine(config)
                        schema = self._detector.detect_live_schema(engine)
                        st.session_state[cfg.engine_key] = engine
                        st.session_state[cfg.current_db_key] = selected
                        st.session_state["detected_schema"] = schema
                        st.session_state.pop(cfg.password_key, None)
                        st.session_state[cfg.step2_status_key] = (
                            "success", f"Using database: **{selected}**"
                        )
                        logger.info(
                            "UI: selected %s database %s", cfg.log_dialect, selected
                        )
                    except (DatabaseConnectionError, SchemaDetectionError) as exc:
                        st.session_state[cfg.step2_status_key] = ("error", str(exc))
                        logger.warning(
                            "UI: %s database selection failed: %s", cfg.log_dialect, exc
                        )

        self._render_status(cfg.step2_status_key)

    # ── MongoDB Step 1 ────────────────────────────────────────────────────────

    def _render_mongo_step1(self) -> None:
        """Render MongoDB Step 1: server credentials form and Connect button.

        Supports two input modes selected by a radio widget:
        - **Fields** (default): Host, Port, Username, Password, Auth Source, Auth Mechanism.
        - **URI + credentials**: MongoDB URI text box + Username + Password only.
        """
        st.markdown("**Step 1 - Connect to server**")

        # ── Input mode toggle ─────────────────────────────────────────────────
        input_mode = st.radio(
            "Connection input mode",
            options=["Fields", "URI + credentials"],
            index=0 if st.session_state.get("mongo_input_mode", "Fields") == "Fields" else 1,
            horizontal=True,
            key="mongo_input_mode_radio",
        )
        st.session_state["mongo_input_mode"] = input_mode

        if input_mode == "URI + credentials":
            self._render_mongo_step1_uri_mode()
        else:
            self._render_mongo_step1_fields_mode()

    def _render_mongo_step1_fields_mode(self) -> None:
        """Render MongoDB Step 1 in Fields input mode (original form)."""
        host = st.text_input(
            "Host", value=st.session_state.get("mongo_host", "localhost"), key="mongo_host_input"
        )
        port = st.number_input(
            "Port",
            value=int(st.session_state.get("mongo_port", 27017)),
            min_value=1,
            max_value=65535,
            key="mongo_port_input",
        )
        username = st.text_input(
            "Username", value=st.session_state.get("mongo_user", ""), key="mongo_user_input"
        )
        password = st.text_input("Password", type="password", key="mongo_password_input")
        auth_source = st.text_input(
            "Auth Source",
            value=st.session_state.get("mongo_auth_source", "admin"),
            key="mongo_auth_source_input",
        )
        auth_mechanism = st.selectbox(
            "Auth Mechanism",
            options=["SCRAM-SHA-256", "SCRAM-SHA-1", "MONGODB-X509", "None / No Auth"],
            index=["SCRAM-SHA-256", "SCRAM-SHA-1", "MONGODB-X509", "None / No Auth"].index(
                st.session_state.get("mongo_auth_mechanism", "SCRAM-SHA-256")
            ),
            key="mongo_auth_mech_input",
        )

        if st.button("Connect", type="primary", key="mongo_connect"):
            # Close any existing client before discarding it from session state
            # — zombie MongoClient background threads exhaust the connection pool.
            _close_mongo_client()
            _clear_mongo_state()

            no_auth = auth_mechanism == "None / No Auth"
            mongo_validation_error = _validate_mongo_fields_inputs(
                host, username, password, no_auth
            )
            if mongo_validation_error is not None:
                st.session_state["mongo_step1_status"] = mongo_validation_error
            else:
                # Persist non-sensitive values
                st.session_state["mongo_host"] = host
                st.session_state["mongo_port"] = int(port)
                st.session_state["mongo_user"] = username
                st.session_state["mongo_auth_source"] = auth_source
                st.session_state["mongo_auth_mechanism"] = auth_mechanism
                st.session_state["_mongo_password"] = password

                config = _build_mongo_config(
                    host=host, port=int(port), username=username, password=password,
                    auth_source=auth_source, auth_mechanism=auth_mechanism,
                )
                with st.spinner("Connecting to MongoDB server..."):
                    try:
                        client = self._mongo_connector.connect(config)
                        databases = self._mongo_connector.list_databases(client)
                        st.session_state["mongo_client"] = client
                        st.session_state["mongo_available_databases"] = databases
                        n = len(databases)
                        st.session_state["mongo_step1_status"] = (
                            "success",
                            _format_connect_success(host, n),
                        )
                        logger.info(
                            "UI: connected to MongoDB server %s; %d databases found", host, n
                        )
                    except DatabaseConnectionError as exc:
                        st.session_state["mongo_step1_status"] = (
                            "error",
                            f"Connection failed: {exc}",
                        )
                        logger.warning("UI: MongoDB server connection failed: %s", exc)

        self._render_status("mongo_step1_status")

    def _render_mongo_step1_uri_mode(self) -> None:
        """Render MongoDB Step 1 in URI + credentials mode."""
        raw_uri = st.text_input(
            "MongoDB URI",
            value=st.session_state.get("mongo_raw_uri", ""),
            placeholder="mongodb://localhost:27017/ or mongodb+srv://...",
            key="mongo_raw_uri_input",
        )
        username = st.text_input(
            "Username",
            value=st.session_state.get("mongo_user", ""),
            key="mongo_uri_user_input",
        )
        password = st.text_input("Password", type="password", key="mongo_uri_password_input")
        st.caption(
            "You can paste a full URI that already contains credentials "
            "(e.g. `mongodb://user:pass@host:27017/db`) — "
            "the Username/Password fields are then optional."
        )

        if st.button("Connect", type="primary", key="mongo_connect"):
            # Close any existing client before discarding it from session state
            # — zombie MongoClient background threads exhaust the connection pool.
            _close_mongo_client()
            _clear_mongo_state()

            if not raw_uri:
                st.session_state["mongo_step1_status"] = (
                    "warning",
                    "Please enter a MongoDB URI.",
                )
                self._render_status("mongo_step1_status")
                return

            # Persist raw URI (non-sensitive) and username
            st.session_state["mongo_raw_uri"] = raw_uri
            st.session_state["mongo_user"] = username
            st.session_state["_mongo_password"] = password

            config = MongoConfig(
                host="",
                raw_uri=raw_uri,
                username=username,
                password=password,
            )
            with st.spinner("Connecting to MongoDB server..."):
                try:
                    client = self._mongo_connector.connect(config)
                    databases = self._mongo_connector.list_databases(client)
                    st.session_state["mongo_client"] = client
                    st.session_state["mongo_available_databases"] = databases
                    n = len(databases)
                    st.session_state["mongo_step1_status"] = (
                        "success",
                        f"Connected via URI - {n} database{'s' if n != 1 else ''} found",
                    )
                    logger.info("UI: connected to MongoDB via URI; %d databases found", n)
                except (DatabaseConnectionError, ValueError) as exc:
                    st.session_state["mongo_step1_status"] = (
                        "error",
                        f"Connection failed: {exc}",
                    )
                    logger.warning("UI: MongoDB URI connection failed: %s", exc)

        self._render_status("mongo_step1_status")

    # ── MongoDB Step 2 ────────────────────────────────────────────────────────

    def _render_mongo_step2(self) -> None:
        """Render MongoDB Step 2: database dropdown and Select Database button."""
        if st.session_state.get("mongo_client") is None:
            return

        st.markdown("---")
        st.markdown("**Step 2 - Select database**")

        available: list[str] = st.session_state.get("mongo_available_databases", [])

        if not available:
            st.warning("No accessible databases found for this user")
            return

        current = st.session_state.get("mongo_selected_database")
        default_index = available.index(current) if current in available else 0

        selected = st.selectbox(
            "Select a database",
            options=available,
            index=default_index,
            key="mongo_db_select",
        )

        if st.button("Select Database", type="secondary", key="mongo_db_confirm"):
            client = st.session_state.get("mongo_client")
            if client is None:  # pragma: no cover
                # Excluded: guard condition unreachable via AppTest when step-2
                # renders only after a successful connect (client is never None here).
                st.session_state["mongo_step2_status"] = (
                    "warning",
                    "Session credentials expired - please reconnect in Step 1.",
                )
            else:
                with st.spinner(f"Connecting to **{selected}**..."):
                    try:
                        mongo_db = self._mongo_connector.get_database(client, selected)
                        schema = self._mongo_detector.detect_schema(mongo_db)
                        st.session_state["mongo_db"] = mongo_db
                        st.session_state["mongo_selected_database"] = selected
                        st.session_state["detected_schema"] = schema
                        n = len(schema)
                        st.session_state["mongo_step2_status"] = (
                            "success",
                            f"{selected} selected - {n} collection{'s' if n != 1 else ''} detected",
                        )
                        logger.info("UI: selected MongoDB database %s (%d collections)", selected, n)
                    except (DatabaseConnectionError, SchemaDetectionError) as exc:
                        st.session_state["mongo_step2_status"] = ("error", str(exc))
                        logger.warning("UI: MongoDB database selection failed: %s", exc)

        self._render_status("mongo_step2_status")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _render_status(key: str) -> None:
        """Display a status message stored under *key* in session state.

        Args:
            key: The session-state key holding a ``(level, message)`` tuple.
                 *level* must be ``"success"``, ``"error"``, or ``"warning"``.
        """
        status = st.session_state.get(key)
        if status is None:
            return
        level, msg = status
        if level == "success":
            st.success(msg)
        elif level == "error":
            st.error(f"{msg}")
        else:
            st.warning(f"{msg}")
