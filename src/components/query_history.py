"""Session-scoped query history Streamlit component (US-085/087/089 / EPIC-017/018/019)."""
from __future__ import annotations

import streamlit as st

_MAX_ENTRIES: int = 10
_TRUNCATE_LEN: int = 80


def _db_type_badge(db_type: str) -> str:
    """Return a short display string for the given database type.

    Pure helper — no Streamlit dependency; fully unit-testable.

    Args:
        db_type: Database type string, e.g. ``"MySQL"``, ``"MongoDB"``.

    Returns:
        A short emoji-prefixed label for the database type, or *db_type*
        unchanged if the value is not a known type.
    """
    _BADGES: dict[str, str] = {
        "MySQL": "\U0001f42c MySQL",
        "PostgreSQL": "\U0001f418 PostgreSQL",
        "MongoDB": "\U0001f343 MongoDB",
    }
    return _BADGES.get(db_type, db_type)


def _db_type_to_lang(db_type: str) -> str:
    """Map a database type string to a syntax-highlighting language token.

    Pure helper — no Streamlit dependency; fully unit-testable.

    Args:
        db_type: Database type string, e.g. ``"MongoDB"``, ``"MySQL"``.

    Returns:
        ``"json"`` for MongoDB; ``"sql"`` for all other types.
    """
    return "json" if db_type == "MongoDB" else "sql"


def _append_to_history(
    history: list[dict[str, str]],
    question: str,
    sql: str,
    db_type: str = "MySQL",
    max_entries: int = _MAX_ENTRIES,
) -> list[dict[str, str]]:
    """Append a new entry to the front of the query history list.

    Deduplicates by removing any existing entry with the same question, then
    prepends the new entry and caps the list at *max_entries*.

    Pure helper — no Streamlit dependency; fully unit-testable.

    Args:
        history: Current history list (most-recent at index 0).
        question: Plain-English question the user typed.
        sql: Generated SQL or MQL string.
        db_type: Database type used for the query (e.g. ``"MySQL"``).
        max_entries: Maximum number of history items to retain.

    Returns:
        Updated history list with the new entry at index 0.
    """
    entry: dict[str, str] = {"question": question, "sql": sql, "db_type": db_type}
    deduped = [h for h in history if h.get("question") != question]
    return ([entry] + deduped)[:max_entries]


def _truncate(text: str, max_len: int = _TRUNCATE_LEN) -> str:
    """Truncate *text* to *max_len* characters, appending '…' if shortened.

    Pure helper — no Streamlit dependency; fully unit-testable.

    Args:
        text: Input string.
        max_len: Maximum number of characters before truncation.

    Returns:
        Original string, or truncated string with trailing ellipsis.
    """
    if len(text) <= max_len:
        return text
    return text[:max_len] + "\u2026"


class QueryHistoryComponent:
    """Renders the session-scoped query history panel (US-085/088/089)."""

    def render(self, history: list[dict[str, str]]) -> None:  # pragma: no cover
        """Display recent queries in a collapsible expander.

        Excluded from coverage: all statements are ``st.`` widget calls that
        require a live Streamlit render context; not reachable via unit tests.

        Args:
            history: List of history dicts with ``question``, ``sql``, and
                ``db_type`` keys, most-recent first.  An empty list renders
                nothing.
        """
        if not history:
            return
        with st.expander(f"\U0001f552 Query History ({len(history)})", expanded=False):
            if st.button(
                "\U0001f5d1\ufe0f Clear History",
                key="clear_history",
                use_container_width=False,
            ):
                st.session_state["query_history"] = []
                st.rerun()
            for i, entry in enumerate(history):
                col_text, col_btn = st.columns([3, 1])
                with col_text:
                    db_type = entry.get("db_type", "MySQL")
                    st.caption(
                        f"{_db_type_badge(db_type)} · **Q:** {_truncate(entry['question'])}"
                    )
                    lang = _db_type_to_lang(db_type)
                    st.code(_truncate(entry["sql"]), language=lang)
                with col_btn:
                    if st.button(
                        "\u21a9 Re-use",
                        key=f"reuse_{i}",
                        use_container_width=True,
                    ):
                        st.session_state["query_text"] = entry["question"]
                        st.rerun()
