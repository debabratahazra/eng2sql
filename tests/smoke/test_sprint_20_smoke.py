"""Smoke tests for Sprint 20 — Query History & CSV Export.

Covers Sprint 20 user stories:
- US-085: Session-scoped query history (pure helpers _append_to_history, _truncate)
- US-086: CSV export of most recent result set (pure helpers _result_to_csv, _export_filename)

All tests are smoke-level: they verify Sprint 20 deliverables are present and
structurally correct without requiring a live database or Streamlit runtime.
"""
from __future__ import annotations

import importlib
import inspect
import pathlib

import pandas as pd
import pytest

_ROOT = pathlib.Path(__file__).parent.parent.parent

pytestmark = pytest.mark.smoke


# ---------------------------------------------------------------------------
# US-085: Query history component
# ---------------------------------------------------------------------------


class TestQueryHistoryUS085:
    """Verify query_history.py exists with correct helpers and behaviour."""

    def test_query_history_module_exists(self) -> None:
        """src/components/query_history.py is present."""
        assert (_ROOT / "src" / "components" / "query_history.py").exists()

    def test_append_to_history_is_importable(self) -> None:
        """_append_to_history can be imported from the module."""
        from components.query_history import _append_to_history  # noqa: PLC0415

        assert callable(_append_to_history)

    def test_truncate_is_importable(self) -> None:
        """_truncate can be imported from the module."""
        from components.query_history import _truncate  # noqa: PLC0415

        assert callable(_truncate)

    def test_query_history_component_class_exists(self) -> None:
        """QueryHistoryComponent class is importable."""
        from components.query_history import QueryHistoryComponent  # noqa: PLC0415

        assert inspect.isclass(QueryHistoryComponent)

    def test_append_to_history_empty_list(self) -> None:
        """_append_to_history works on empty list."""
        from components.query_history import _append_to_history  # noqa: PLC0415

        result = _append_to_history([], "test q", "SELECT 1")
        assert len(result) == 1
        assert result[0]["question"] == "test q"

    def test_append_to_history_caps_at_ten(self) -> None:
        """History is capped at 10 entries."""
        from components.query_history import _MAX_ENTRIES, _append_to_history  # noqa: PLC0415

        history = [{"question": f"q{i}", "sql": f"SELECT {i}"} for i in range(10)]
        result = _append_to_history(history, "new", "SELECT 99")
        assert len(result) == _MAX_ENTRIES

    def test_truncate_long_string(self) -> None:
        """_truncate shortens strings beyond 80 chars."""
        from components.query_history import _TRUNCATE_LEN, _truncate  # noqa: PLC0415

        long_text = "x" * (_TRUNCATE_LEN + 20)
        result = _truncate(long_text)
        assert result.endswith("\u2026")
        assert len(result) == _TRUNCATE_LEN + 1

    def test_app_py_imports_query_history(self) -> None:
        """app.py imports QueryHistoryComponent and _append_to_history."""
        app_src = (_ROOT / "src" / "app.py").read_text(encoding="utf-8")
        assert "QueryHistoryComponent" in app_src
        assert "_append_to_history" in app_src

    def test_app_py_initialises_query_history_state(self) -> None:
        """app.py initialises 'query_history' in session state defaults."""
        app_src = (_ROOT / "src" / "app.py").read_text(encoding="utf-8")
        assert '"query_history"' in app_src

    def test_query_input_uses_query_text_key(self) -> None:
        """query_input.py uses key='query_text' for the text_area (Re-use support)."""
        src = (_ROOT / "src" / "components" / "query_input.py").read_text(encoding="utf-8")
        assert 'key="query_text"' in src

    def test_utr_027_exists(self) -> None:
        """UTR-027 test result document exists for US-085."""
        assert (_ROOT / "docs" / "test-results" / "UTR-027-us085-query-history.md").exists()


# ---------------------------------------------------------------------------
# US-086: CSV export component
# ---------------------------------------------------------------------------


class TestCSVExportUS086:
    """Verify csv_export.py exists with correct helpers and behaviour."""

    def test_csv_export_module_exists(self) -> None:
        """src/components/csv_export.py is present."""
        assert (_ROOT / "src" / "components" / "csv_export.py").exists()

    def test_result_to_csv_importable(self) -> None:
        """_result_to_csv can be imported from the module."""
        from components.csv_export import _result_to_csv  # noqa: PLC0415

        assert callable(_result_to_csv)

    def test_export_filename_importable(self) -> None:
        """_export_filename can be imported from the module."""
        from components.csv_export import _export_filename  # noqa: PLC0415

        assert callable(_export_filename)

    def test_csv_export_component_class_exists(self) -> None:
        """CSVExportComponent class is importable."""
        from components.csv_export import CSVExportComponent  # noqa: PLC0415

        assert inspect.isclass(CSVExportComponent)

    def test_result_to_csv_returns_bytes(self) -> None:
        """_result_to_csv returns bytes for a standard DataFrame."""
        from components.csv_export import _result_to_csv  # noqa: PLC0415

        df = pd.DataFrame({"col": [1, 2]})
        assert isinstance(_result_to_csv(df), bytes)

    def test_result_to_csv_utf8_decodable(self) -> None:
        """CSV bytes decode cleanly as UTF-8."""
        from components.csv_export import _result_to_csv  # noqa: PLC0415

        df = pd.DataFrame({"a": ["hello"]})
        assert _result_to_csv(df).decode("utf-8")

    def test_export_filename_format(self) -> None:
        """_export_filename produces the expected filename pattern."""
        from components.csv_export import _export_filename  # noqa: PLC0415

        assert _export_filename("20260509") == "eng2sql_results_20260509.csv"

    def test_app_py_imports_csv_export(self) -> None:
        """app.py imports CSVExportComponent."""
        app_src = (_ROOT / "src" / "app.py").read_text(encoding="utf-8")
        assert "CSVExportComponent" in app_src

    def test_app_py_renders_csv_export(self) -> None:
        """app.py calls csv_component.render() in the query results section."""
        app_src = (_ROOT / "src" / "app.py").read_text(encoding="utf-8")
        assert "csv_component.render" in app_src

    def test_utr_028_exists(self) -> None:
        """UTR-028 test result document exists for US-086."""
        assert (_ROOT / "docs" / "test-results" / "UTR-028-us086-csv-export.md").exists()


# ---------------------------------------------------------------------------
# General Sprint 20 regression
# ---------------------------------------------------------------------------


class TestGeneralRegressionSprint20:
    """Verify Sprint 20 artefacts and regression against prior sprints."""

    def test_sprint_19_smoke_still_passes(self) -> None:
        """Sprint 19 smoke test file still exists and is non-empty."""
        p = _ROOT / "tests" / "smoke" / "test_sprint_19_smoke.py"
        assert p.exists() and p.stat().st_size > 0

    def test_pragma_audit_still_passes_on_src(self) -> None:
        """pragma_audit.py reports 0 violations on src/ after Sprint 20 additions."""
        import subprocess  # noqa: PLC0415
        import sys  # noqa: PLC0415

        result = subprocess.run(
            [sys.executable, str(_ROOT / "scripts" / "pragma_audit.py")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"pragma_audit.py failed:\n{result.stdout}\n{result.stderr}"

    def test_tr_020_exists(self) -> None:
        """TR-020 test result document exists for Sprint 20."""
        assert (_ROOT / "docs" / "test-results" / "TR-020-sprint20.md").exists()

    def test_cr_020_exists(self) -> None:
        """CR-020 code review document exists for Sprint 20."""
        assert (_ROOT / "docs" / "code-reviews" / "CR-020-sprint20-query-history-csv-export.md").exists()

    def test_coverage_100_percent_referenced_in_tr020(self) -> None:
        """TR-020 references 100% coverage."""
        content = (_ROOT / "docs" / "test-results" / "TR-020-sprint20.md").read_text(encoding="utf-8")
        assert "100.00%" in content or "100%" in content
