"""Step-by-step progress tracker Streamlit component."""
from __future__ import annotations

import streamlit as st


class ProgressTracker:
    """Displays step-by-step status messages during SQL generation."""

    _SESSION_KEY = "progress_steps"

    def reset(self) -> None:
        """Clear all progress steps from the session state."""
        st.session_state[self._SESSION_KEY] = []

    def update(self, message: str) -> None:
        """Append a new step message and re-render the progress list.

        Args:
            message: Human-readable step description to display.
        """
        steps: list[str] = st.session_state.get(self._SESSION_KEY, [])
        steps.append(message)
        st.session_state[self._SESSION_KEY] = steps

        with st.status("Generating SQL…", expanded=True) as status:
            for step in steps:
                st.write(step)
            if "Done ✅" in message:
                status.update(label="Done ✅", state="complete", expanded=False)
