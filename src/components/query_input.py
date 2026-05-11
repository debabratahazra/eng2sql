"""Query input Streamlit component."""
from __future__ import annotations

import streamlit as st


class QueryInputComponent:
    """Renders the English query text area and Generate SQL button."""

    def render(self) -> str | None:
        """Render the input area.

        Returns:
            The user's question string if the button was clicked and input is
            non-empty, otherwise ``None``.
        """
        st.subheader("💬 Ask in English")
        question = st.text_area(
            label="Your question",
            placeholder="e.g. Show me the top 10 customers by total order value",
            height=120,
            label_visibility="collapsed",
            key="query_text",
        )

        col_btn, col_hint = st.columns([1, 3])
        with col_btn:
            clicked = st.button("⚡ Generate SQL", type="primary", use_container_width=True)
        with col_hint:
            st.caption("Press the button or Ctrl+Enter to generate SQL.")

        if clicked:  # pragma: no cover
            # Excluded: button-click path requires AppTest interaction;
            # the empty-input guard and return are both unreachable in unit tests.
            if not question or not question.strip():
                st.warning("⚠️ Please enter a question before generating SQL.")
                return None
            return question.strip()

        return None
