"""SQL / MQL output Streamlit component."""
from __future__ import annotations

import streamlit as st


class SQLOutputComponent:
    """Renders the generated SQL or MQL in a syntax-highlighted code block.

    The label and hint text update dynamically based on the active database
    type (US-057 / EPIC-009).
    """

    def render(self, sql: str, db_type: str = "MySQL") -> None:
        """Display the generated SQL or MQL query.

        Args:
            sql: The query string to display. If empty, shows a placeholder.
            db_type: Active database type (``"MySQL"``, ``"PostgreSQL"``, or
                ``"MongoDB"``). Controls the panel label and hint text.
        """
        is_mongo = db_type == "MongoDB"
        label = "🗒️ Generated MQL" if is_mongo else "🗒️ Generated SQL"
        query_noun = "MQL" if is_mongo else "SQL"
        lang = "json" if is_mongo else "sql"

        st.subheader(label)

        if sql:
            st.code(sql, language=lang)
            col_copy, col_clear = st.columns([1, 1])
            with col_copy:
                st.caption(
                    f"Copy the {query_noun} above to use in your "
                    f"{'MongoDB' if is_mongo else 'database'} client."
                )
            with col_clear:
                if st.button("🗑️ Clear", key="clear_sql"):
                    st.session_state["generated_sql"] = ""
                    st.session_state["query_result"] = None
                    st.rerun()
        else:
            st.info(
                f"Generated {query_noun} will appear here after you submit a question."
            )

