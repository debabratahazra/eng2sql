"""CSV export Streamlit component (US-086 / EPIC-017)."""
from __future__ import annotations

import pandas as pd
import streamlit as st


def _result_to_csv(df: pd.DataFrame) -> bytes:
    """Serialise a DataFrame to UTF-8 encoded CSV bytes.

    Pure helper — no Streamlit dependency; fully unit-testable.

    Args:
        df: Query result DataFrame.

    Returns:
        UTF-8 encoded CSV bytes with header row and no index column.
    """
    return df.to_csv(index=False).encode("utf-8")


def _export_filename(date_str: str) -> str:
    """Build the download filename from a date string.

    Pure helper — no Streamlit dependency; fully unit-testable.

    Args:
        date_str: Date string in ``YYYYMMDD`` format.

    Returns:
        Filename string, e.g. ``"eng2sql_results_20260509.csv"``.
    """
    return f"eng2sql_results_{date_str}.csv"


class CSVExportComponent:
    """Renders the CSV download button below a query result table (US-086)."""

    def render(self, df: pd.DataFrame) -> None:  # pragma: no cover
        """Display a download button for exporting the result set as CSV.

        Excluded from coverage: all statements are ``st.`` widget calls that
        require a live Streamlit render context; not reachable via unit tests.

        Args:
            df: The query result DataFrame.  If empty (0 rows), the button is
                shown as disabled with a ``"No results to export"`` label.
        """
        from datetime import date

        date_str = date.today().strftime("%Y%m%d")
        filename = _export_filename(date_str)

        if df.empty:
            st.button(
                "No results to export",
                disabled=True,
                key="csv_export_disabled",
            )
            return

        csv_bytes = _result_to_csv(df)
        st.download_button(
            label="\u2b07 Download CSV",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv",
            key="csv_export",
        )
