"""Unit tests for csv_export component pure helpers (US-086 / EPIC-017)."""
from __future__ import annotations

import pandas as pd
import pytest

from components.csv_export import _export_filename, _result_to_csv


class TestResultToCsv:
    """Tests for _result_to_csv()."""

    def test_returns_bytes(self) -> None:
        """Return type is bytes."""
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        result = _result_to_csv(df)
        assert isinstance(result, bytes)

    def test_utf8_encoded(self) -> None:
        """Returned bytes decode as UTF-8."""
        df = pd.DataFrame({"col": ["value"]})
        result = _result_to_csv(df)
        decoded = result.decode("utf-8")
        assert "col" in decoded

    def test_header_row_present(self) -> None:
        """CSV output contains column names in the first line."""
        df = pd.DataFrame({"name": ["Alice"], "age": [30]})
        csv_text = _result_to_csv(df).decode("utf-8")
        first_line = csv_text.splitlines()[0]
        assert "name" in first_line
        assert "age" in first_line

    def test_no_index_column(self) -> None:
        """CSV output does not include a row index column."""
        df = pd.DataFrame({"val": [42]})
        csv_text = _result_to_csv(df).decode("utf-8")
        # Index would appear as a leading empty field or integer in the first col
        first_line = csv_text.splitlines()[0]
        assert first_line.strip() == "val"

    def test_data_rows_present(self) -> None:
        """All data rows are serialised to the CSV output."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        csv_text = _result_to_csv(df).decode("utf-8")
        lines = csv_text.strip().splitlines()
        # Header + 3 data rows
        assert len(lines) == 4

    def test_empty_dataframe_produces_header_only(self) -> None:
        """Empty DataFrame serialises to header row only (no data rows)."""
        df = pd.DataFrame({"col_a": pd.Series([], dtype=str)})
        csv_text = _result_to_csv(df).decode("utf-8")
        lines = [ln for ln in csv_text.strip().splitlines() if ln]
        assert len(lines) == 1
        assert "col_a" in lines[0]

    def test_unicode_values_preserved(self) -> None:
        """Non-ASCII values are preserved in the CSV output."""
        df = pd.DataFrame({"city": ["\u6771\u4eac", "Berlin"]})
        csv_text = _result_to_csv(df).decode("utf-8")
        assert "\u6771\u4eac" in csv_text

    def test_comma_in_value_quoted(self) -> None:
        """Values containing commas are properly quoted."""
        df = pd.DataFrame({"note": ["hello, world"]})
        csv_text = _result_to_csv(df).decode("utf-8")
        # The value with a comma should be wrapped in quotes
        assert '"hello, world"' in csv_text


class TestExportFilename:
    """Tests for _export_filename()."""

    def test_returns_string(self) -> None:
        """Return type is str."""
        assert isinstance(_export_filename("20260509"), str)

    def test_contains_date_str(self) -> None:
        """Filename includes the supplied date string."""
        assert "20260509" in _export_filename("20260509")

    def test_prefix_correct(self) -> None:
        """Filename starts with the expected prefix."""
        assert _export_filename("20260101").startswith("eng2sql_results_")

    def test_csv_extension(self) -> None:
        """Filename ends with '.csv'."""
        assert _export_filename("20260509").endswith(".csv")

    def test_full_filename_format(self) -> None:
        """Full filename matches the expected pattern."""
        assert _export_filename("20260509") == "eng2sql_results_20260509.csv"

    def test_different_date_strings(self) -> None:
        """Different date inputs produce different filenames."""
        f1 = _export_filename("20260101")
        f2 = _export_filename("20261231")
        assert f1 != f2
