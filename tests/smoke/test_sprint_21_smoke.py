"""Sprint 21 smoke tests — Query History UX Polish (US-087, US-088).

Verifies that:
- US-087: db_type is stored in history entries; _db_type_to_lang() exists and works.
- US-088: Clear History button string present in query_history.py source.
- Sprint 20 regression: all prior smoke artefacts remain intact.
"""
from __future__ import annotations

import importlib
import inspect
import pathlib

import pytest

pytestmark = pytest.mark.smoke

_SRC = pathlib.Path(__file__).parent.parent.parent / "src"
_DOCS = pathlib.Path(__file__).parent.parent.parent / "docs"


# ---------------------------------------------------------------------------
# US-087 — db_type in history entry
# ---------------------------------------------------------------------------


class TestDbTypeInHistoryUS087:
    """Smoke tests for US-087: Store db_type in History Entry."""

    def test_db_type_to_lang_importable(self) -> None:
        """_db_type_to_lang is exported from query_history module."""
        mod = importlib.import_module("components.query_history")
        assert hasattr(mod, "_db_type_to_lang")

    def test_db_type_to_lang_mongodb_returns_json(self) -> None:
        """_db_type_to_lang('MongoDB') returns 'json'."""
        from components.query_history import _db_type_to_lang
        assert _db_type_to_lang("MongoDB") == "json"

    def test_db_type_to_lang_mysql_returns_sql(self) -> None:
        """_db_type_to_lang('MySQL') returns 'sql'."""
        from components.query_history import _db_type_to_lang
        assert _db_type_to_lang("MySQL") == "sql"

    def test_db_type_to_lang_postgresql_returns_sql(self) -> None:
        """_db_type_to_lang('PostgreSQL') returns 'sql'."""
        from components.query_history import _db_type_to_lang
        assert _db_type_to_lang("PostgreSQL") == "sql"

    def test_append_to_history_accepts_db_type_kwarg(self) -> None:
        """_append_to_history accepts db_type keyword argument."""
        from components.query_history import _append_to_history
        sig = inspect.signature(_append_to_history)
        assert "db_type" in sig.parameters

    def test_append_to_history_db_type_default_mysql(self) -> None:
        """_append_to_history db_type parameter defaults to 'MySQL'."""
        from components.query_history import _append_to_history
        sig = inspect.signature(_append_to_history)
        assert sig.parameters["db_type"].default == "MySQL"

    def test_append_to_history_entry_includes_db_type(self) -> None:
        """History entry dict includes db_type key."""
        from components.query_history import _append_to_history
        result = _append_to_history([], "q", "SELECT 1", db_type="PostgreSQL")
        assert result[0]["db_type"] == "PostgreSQL"

    def test_append_to_history_entry_default_db_type(self) -> None:
        """History entry has db_type='MySQL' when not supplied."""
        from components.query_history import _append_to_history
        result = _append_to_history([], "q", "SELECT 1")
        assert result[0]["db_type"] == "MySQL"

    def test_app_py_passes_db_type_to_append(self) -> None:
        """app.py passes db_type=db_type when calling _append_to_history."""
        app_source = (_SRC / "app.py").read_text(encoding="utf-8")
        assert "db_type=db_type" in app_source

    def test_render_uses_get_with_default_for_db_type(self) -> None:
        """render() uses entry.get('db_type', ...) for backward compat."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert 'entry.get("db_type"' in source or "entry.get('db_type'" in source

    def test_utr_029_exists(self) -> None:
        """UTR-029 artefact file exists."""
        assert (_DOCS / "test-results" / "UTR-029-us087-history-db-type.md").exists()


# ---------------------------------------------------------------------------
# US-088 — Clear History button
# ---------------------------------------------------------------------------


class TestClearHistoryButtonUS088:
    """Smoke tests for US-088: Clear History Button."""

    def test_clear_history_string_in_source(self) -> None:
        """The string 'Clear History' appears in query_history.py source."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert "Clear History" in source

    def test_clear_history_key_in_source(self) -> None:
        """key='clear_history' widget key appears in source."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert "clear_history" in source

    def test_session_state_reset_in_source(self) -> None:
        """Session state reset to [] appears in source."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert 'st.session_state["query_history"] = []' in source

    def test_rerun_after_clear_in_source(self) -> None:
        """st.rerun() call appears after the clear logic."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        clear_idx = source.find('st.session_state["query_history"] = []')
        rerun_idx = source.find("st.rerun()", clear_idx)
        assert rerun_idx > clear_idx

    def test_empty_history_guard_still_present(self) -> None:
        """The 'if not history: return' guard is still in place."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert "if not history:" in source

    def test_utr_030_exists(self) -> None:
        """UTR-030 artefact file exists."""
        assert (_DOCS / "test-results" / "UTR-030-us088-clear-history-button.md").exists()


# ---------------------------------------------------------------------------
# Sprint 21 artefact checks
# ---------------------------------------------------------------------------


class TestSprint21Artefacts:
    """Verify all Sprint 21 pipeline artefacts exist."""

    def test_cr_021_exists(self) -> None:
        """Code review CR-021 exists."""
        assert (_DOCS / "code-reviews" / "CR-021-sprint21-query-history-ux-polish.md").exists()

    def test_tc_137_140_exists(self) -> None:
        """Test cases TC-137-140 exist."""
        assert (_DOCS / "test-cases" / "TC-137-140-sprint21-query-history-ux-polish.md").exists()

    def test_tr_021_exists(self) -> None:
        """TR-021 test results exist."""
        assert (_DOCS / "test-results" / "TR-021-sprint21.md").exists()

    def test_itr_013_exists(self) -> None:
        """ITR-013 integration test results exist."""
        assert (_DOCS / "test-results" / "ITR-013-sprint21.md").exists()


# ---------------------------------------------------------------------------
# Regression — Sprint 20 smoke artefacts intact
# ---------------------------------------------------------------------------


class TestSprint20Regression:
    """Ensure Sprint 20 outputs are still intact after Sprint 21 changes."""

    def test_query_history_module_still_importable(self) -> None:
        """query_history module still imports cleanly."""
        mod = importlib.import_module("components.query_history")
        assert hasattr(mod, "QueryHistoryComponent")
        assert hasattr(mod, "_append_to_history")
        assert hasattr(mod, "_truncate")

    def test_csv_export_module_unaffected(self) -> None:
        """csv_export module is unaffected by Sprint 21 changes."""
        mod = importlib.import_module("components.csv_export")
        assert hasattr(mod, "CSVExportComponent")
        assert hasattr(mod, "_result_to_csv")
        assert hasattr(mod, "_export_filename")

    def test_pragma_audit_passes(self) -> None:
        """pragma_audit.py reports 0 violations."""
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "scripts/pragma_audit.py"],
            capture_output=True,
            text=True,
            cwd=str(_SRC.parent),
        )
        assert result.returncode == 0
        assert "0 violations" in result.stdout

    def test_str_011_sprint20_still_exists(self) -> None:
        """STR-011 Sprint 20 smoke results still present."""
        assert (_DOCS / "test-results" / "STR-011-sprint20-smoke.md").exists()

    def test_tr_020_references_100pct(self) -> None:
        """TR-020 still references 100% coverage."""
        content = (_DOCS / "test-results" / "TR-020-sprint20.md").read_text(encoding="utf-8")
        assert "100" in content
