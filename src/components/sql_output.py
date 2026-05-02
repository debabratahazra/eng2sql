"""SQL output Streamlit component."""
from __future__ import annotations

import streamlit as st


class SQLOutputComponent:
    """Renders the generated SQL in a syntax-highlighted code block."""

    def render(self, sql: str) -> None:
        """Display the generated SQL.

        Args:
            sql: The SQL string to display. If empty, shows a placeholder.
        """
        st.subheader("🗒️ Generated SQL")

        if sql:
            st.code(sql, language="sql")
            col_copy, col_clear = st.columns([1, 1])
            with col_copy:
                st.caption("Copy the SQL above to use in your database client.")
            with col_clear:
                if st.button("🗑️ Clear", key="clear_sql"):
                    st.session_state["generated_sql"] = ""
                    st.session_state["query_result"] = None
                    st.rerun()
        else:
            st.info("Generated SQL will appear here after you submit a question.")
