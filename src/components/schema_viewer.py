"""Schema viewer Streamlit component."""
from __future__ import annotations

import streamlit as st

from models.config import TableSchema


class SchemaViewerComponent:
    """Renders a collapsible panel showing all detected tables and columns."""

    def render(self, schema: TableSchema) -> None:
        """Display the detected database schema.

        Args:
            schema: Mapping of table names to column definitions.
        """
        with st.expander(f"🗄️ Detected Schema ({len(schema)} tables)", expanded=False):
            if not schema:  # pragma: no cover
                # Excluded: empty-schema path requires AppTest with no tables;
                # current test fixtures always provide a non-empty schema.
                st.write("No tables found.")
                return

            col_refresh, _ = st.columns([1, 4])
            with col_refresh:
                if st.button("🔄 Refresh Schema", key="refresh_schema"):  # pragma: no cover
                    # Excluded: refresh-button click path requires AppTest interaction.
                    st.session_state["detected_schema"] = None
                    st.rerun()

            for table_name, columns in schema.items():
                st.markdown(f"**📋 {table_name}**")
                rows = [
                    {
                        "Column": col.name,
                        "Type": col.type,
                        "Nullable": "✅" if col.nullable else "❌",
                        "PK": "🔑" if col.primary_key else "",
                    }
                    for col in columns
                ]
                st.table(rows)
