"""Sidebar Streamlit component for Eng2SQL.

Renders the two-step MySQL live database connection flow:
  Step 1 — server credentials → Connect → discover databases
  Step 2 — database dropdown → Select Database → activate engine + detect schema
"""
from __future__ import annotations

import streamlit as st

from models.config import DBConfig
from services.db_connector import DBConnector
from services.schema_detector import SchemaDetector
from utils.exceptions import DatabaseConnectionError, SchemaDetectionError
from utils.logger import get_logger

logger = get_logger(__name__)

# Session-state keys cleared whenever the user reconnects to a new server.
_DOWNSTREAM_KEYS: tuple[str, ...] = (
    "db_server_engine",
    "available_databases",
    "selected_database",
    "db_engine",
    "detected_schema",
    "_db_password",
    "step1_status",
    "step2_status",
)


def _clear_server_state() -> None:
    """Remove all server-connection-dependent keys from session state."""
    for key in _DOWNSTREAM_KEYS:
        st.session_state.pop(key, None)


class SidebarComponent:
    """Renders the two-step MySQL live database connection sidebar."""

    def __init__(self, connector: DBConnector) -> None:
        """Initialise the sidebar with a DBConnector instance.

        Args:
            connector: The database connector service.
        """
        self._connector = connector
        self._detector = SchemaDetector()

    def render(self) -> None:
        """Render the two-step sidebar.

        Populates the following session-state keys on success:

        - ``db_server_engine`` — server-level engine (Step 1)
        - ``available_databases`` — list of user-accessible databases (Step 1)
        - ``db_engine`` — database-level engine (Step 2)
        - ``selected_database`` — chosen database name (Step 2)
        - ``detected_schema`` — introspected schema map (Step 2)
        """
        with st.sidebar:
            st.header("⚙️ Configuration")
            st.subheader("🔌 MySQL Live Database")
            self._render_step1()
            self._render_step2()

    # ── Step 1 ────────────────────────────────────────────────────────────────

    def _render_step1(self) -> None:
        """Render Step 1: server credentials form and Connect button."""
        st.markdown("**Step 1 — Connect to server**")

        host = st.text_input(
            "Host", value=st.session_state.get("db_host", "localhost")
        )
        port = st.number_input(
            "Port",
            value=int(st.session_state.get("db_port", 3306)),
            min_value=1,
            max_value=65535,
        )
        user = st.text_input("User", value=st.session_state.get("db_user", ""))
        password = st.text_input("Password", type="password")

        if st.button("🔗 Connect", type="primary"):
            _clear_server_state()

            if not all([host, user, password]):
                st.session_state["step1_status"] = (
                    "warning",
                    "Please fill in host, user and password.",
                )
            else:
                # Persist non-sensitive connection fields
                st.session_state["db_host"] = host
                st.session_state["db_port"] = int(port)
                st.session_state["db_user"] = user
                # Keep password in memory for Step 2 (in-memory session only, not persisted)
                st.session_state["_db_password"] = password

                config = DBConfig(
                    host=host, port=int(port), user=user, password=password, database=""
                )
                with st.spinner("Connecting to server…"):
                    try:
                        server_engine = self._connector.create_engine(config)
                        databases = self._connector.list_databases(server_engine)
                        st.session_state["db_server_engine"] = server_engine
                        st.session_state["available_databases"] = databases
                        n = len(databases)
                        st.session_state["step1_status"] = (
                            "success",
                            f"✅ Connected to **{host}** — {n} database{'s' if n != 1 else ''} found",
                        )
                        logger.info(
                            "UI: connected to server %s; %d databases found", host, n
                        )
                    except DatabaseConnectionError as exc:
                        st.session_state["step1_status"] = (
                            "error",
                            f"Connection failed: {exc}",
                        )
                        logger.warning("UI: server connection failed: %s", exc)

        # Render persisted status
        self._render_status("step1_status")

    # ── Step 2 ────────────────────────────────────────────────────────────────

    def _render_step2(self) -> None:
        """Render Step 2: database dropdown and Select Database button."""
        if st.session_state.get("db_server_engine") is None:
            return

        st.markdown("---")
        st.markdown("**Step 2 — Select database**")

        available: list[str] = st.session_state.get("available_databases", [])

        if not available:
            st.warning("⚠️ No accessible databases found for this user")
            return

        current = st.session_state.get("selected_database")
        default_index = available.index(current) if current in available else 0

        selected = st.selectbox(
            "Select a database", options=available, index=default_index
        )

        if st.button("✅ Select Database", type="secondary"):
            password = st.session_state.get("_db_password", "")
            if not password:
                st.session_state["step2_status"] = (
                    "warning",
                    "Session credentials expired — please reconnect in Step 1.",
                )
            else:
                config = DBConfig(
                    host=st.session_state.get("db_host", ""),
                    port=int(st.session_state.get("db_port", 3306)),
                    user=st.session_state.get("db_user", ""),
                    password=password,
                    database=selected,
                )
                # Dispose previous db_engine before creating a new one
                old_engine = st.session_state.get("db_engine")
                if old_engine is not None:
                    old_engine.dispose()
                    st.session_state.pop("db_engine", None)
                    st.session_state.pop("detected_schema", None)

                with st.spinner(f"Connecting to **{selected}**…"):
                    try:
                        engine = self._connector.create_engine(config)
                        schema = self._detector.detect_live_schema(engine)
                        st.session_state["db_engine"] = engine
                        st.session_state["selected_database"] = selected
                        st.session_state["detected_schema"] = schema
                        st.session_state["step2_status"] = (
                            "success",
                            f"✅ Using database: **{selected}**",
                        )
                        logger.info("UI: selected database %s", selected)
                    except (DatabaseConnectionError, SchemaDetectionError) as exc:
                        st.session_state["step2_status"] = ("error", str(exc))
                        logger.warning("UI: database selection failed: %s", exc)

        # Render persisted status
        self._render_status("step2_status")

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
            st.error(f"❌ {msg}")
        else:
            st.warning(f"⚠️ {msg}")
