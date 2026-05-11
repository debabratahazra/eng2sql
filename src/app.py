"""Eng2SQL - English to SQL / MQL Generator.

Streamlit application entry point. Renders the UI shell, orchestrates components,
and wires together the query generation and schema detection services.
"""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from components.csv_export import CSVExportComponent
from components.progress_tracker import ProgressTracker
from components.query_history import QueryHistoryComponent, _append_to_history
from components.query_input import QueryInputComponent
from components.schema_viewer import SchemaViewerComponent
from components.sidebar import SidebarComponent
from components.sql_output import SQLOutputComponent
from models.config import AppConfig
from services.db_connector import DBConnector
from services.mongo_query_executor import MongoQueryExecutor
from services.sql_generator import SQLGenerator
from utils.exceptions import QueryExecutionError, SQLGenerationError
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# -- Page configuration -------------------------------------------------------
st.set_page_config(
    page_title="Eng2SQL - English to SQL Generator",
    page_icon="?",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _build_app_config() -> AppConfig:
    """Load application configuration from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY", "")
    return AppConfig(
        openai_api_key=api_key,
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://gpt4ifx.icp.infineon.com"),
        openai_cert_path=os.getenv("OPENAI_CERT_PATH", "cert/ca-bundle.crt"),
        model_name=os.getenv("OPENAI_MODEL", "gpt-5.2"),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "500")),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
    )


def _initialise_session_state() -> None:
    """Ensure all required session-state keys exist."""
    defaults: dict[str, object] = {
        "db_type": "MySQL",
        "generated_sql": "",
        "query_result": None,
        "db_server_engine": None,
        "available_databases": [],
        "selected_database": "",
        "db_engine": None,
        "detected_schema": None,
        # PostgreSQL session keys (EPIC-009 / US-045)
        "pg_host": "localhost",
        "pg_port": 5432,
        "pg_user": "",
        "pg_sslmode": "prefer",
        "pg_admin_db": "postgres",
        "pg_server_engine": None,
        "pg_available_databases": [],
        "pg_selected_database": "",
        "pg_engine": None,
        "mongo_client": None,
        "mongo_available_databases": [],
        "mongo_selected_database": "",
        "mongo_db": None,
        "steps": [],        # US-085 — session-scoped query history
        "query_history": [],    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    """Application entry point."""
    _initialise_session_state()
    app_config = _build_app_config()

    # -- Services -------------------------------------------------------------
    connector = DBConnector()
    generator = SQLGenerator(app_config)

    # -- Sidebar --------------------------------------------------------------
    sidebar = SidebarComponent(connector)
    sidebar.render()

    # -- Page header ----------------------------------------------------------
    db_type: str = st.session_state.get("db_type", "MySQL")
    if db_type == "MongoDB":
        query_label = "MongoDB"
    elif db_type == "PostgreSQL":
        query_label = "PostgreSQL"
    else:
        query_label = "MySQL"

    st.title("Eng2SQL - English to SQL Generator")
    st.markdown(
        f"Type a question in plain English and get a valid **{query_label}** query "
        "instantly. Powered by OpenAI GPT-5.2."
    )
    st.divider()

    # -- Main columns ---------------------------------------------------------
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        query_component = QueryInputComponent()
        question = query_component.render()

    with col_output:
        output_component = SQLOutputComponent()
        output_component.render(st.session_state["generated_sql"], db_type=db_type)

    # -- Query history (US-085) -----------------------------------------------
    history_component = QueryHistoryComponent()
    history_component.render(st.session_state.get("query_history", []))

    # -- Progress tracker -----------------------------------------------------
    progress = ProgressTracker()

    # -- Generate query on button click ---------------------------------------
    if question:
        st.session_state["steps"] = []
        progress.reset()

        try:
            # Step 1: Read pre-detected schema
            progress.update("Step 1/4 - Reading schema...")
            schema = st.session_state.get("detected_schema")
            if schema is None:
                st.warning(
                    "Please connect to a database and select it in the sidebar first."
                )
                return

            # Step 2: Build prompt
            progress.update("Step 2/4 - Building prompt...")

            # Step 3: Generate SQL / MQL
            if db_type == "MongoDB":
                dialect = "MongoDB"
            elif db_type == "PostgreSQL":
                dialect = "PostgreSQL"
            else:
                dialect = "MySQL"
            progress.update(f"Step 3/4 - Generating {dialect} query with OpenAI...")
            sql = generator.generate_sql(question, schema, dialect=dialect)

            # Step 4: Done
            progress.update("Step 4/4 - Done")
            st.session_state["generated_sql"] = sql
            # US-085/087: append to session-scoped query history with db_type
            st.session_state["query_history"] = _append_to_history(
                st.session_state["query_history"], question, sql, db_type=db_type
            )
            st.rerun()

        except SQLGenerationError as exc:
            st.error(f"Query generation failed: {exc}")
            logger.error("SQL generation error", exc_info=exc)

    # -- Schema viewer --------------------------------------------------------
    if st.session_state.get("detected_schema"):
        st.divider()
        viewer = SchemaViewerComponent()
        viewer.render(st.session_state["detected_schema"])

    # -- SQL execution (MySQL / PostgreSQL) -----------------------------------
    if db_type == "MySQL" and st.session_state.get("generated_sql") and st.session_state.get("db_engine"):
        if st.button("Execute SQL", type="secondary"):
            try:
                engine = st.session_state["db_engine"]
                result_df = connector.execute_query(
                    engine, st.session_state["generated_sql"]
                )
                st.session_state["query_result"] = result_df
            except (QueryExecutionError, SQLAlchemyError) as exc:
                st.error(f"Query execution failed: {exc}")
                logger.error("Query execution error", exc_info=exc)

    if (
        db_type == "PostgreSQL"
        and st.session_state.get("generated_sql")
        and st.session_state.get("pg_engine")
    ):
        if st.button("Execute SQL", type="secondary", key="pg_execute"):
            try:
                engine = st.session_state["pg_engine"]
                result_df = connector.execute_query(
                    engine, st.session_state["generated_sql"]
                )
                st.session_state["query_result"] = result_df
            except (QueryExecutionError, SQLAlchemyError) as exc:
                st.error(f"Query execution failed: {exc}")
                logger.error("Query execution error", exc_info=exc)

    if (
        db_type == "MongoDB"
        and st.session_state.get("generated_sql")
        and st.session_state.get("mongo_db") is not None
    ):
        if st.button("▶ Execute MQL", type="secondary", key="mongo_execute"):
            try:
                mongo_db = st.session_state["mongo_db"]
                result_df = MongoQueryExecutor().execute(
                    mongo_db, st.session_state["generated_sql"]
                )
                st.session_state["query_result"] = result_df
            except QueryExecutionError as exc:
                st.error(f"MQL execution failed: {exc}")
                logger.error("MQL execution error", exc_info=exc)
            else:
                st.rerun()
    elif db_type == "MongoDB" and st.session_state.get("generated_sql"):
        st.info(
            "Connect to a MongoDB database (sidebar) to enable query execution."
        )

    if st.session_state.get("query_result") is not None:
        st.subheader("Query Results")
        st.dataframe(st.session_state["query_result"], use_container_width=True)
        # US-086: CSV export button
        csv_component = CSVExportComponent()
        csv_component.render(st.session_state["query_result"])


if __name__ == "__main__":
    main()
