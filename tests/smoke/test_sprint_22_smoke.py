"""Sprint 22 smoke tests — History Panel Display Polish (US-089).

Verifies that:
- US-089: _db_type_badge() pure helper exists, is importable, and returns correct values.
- render() uses _db_type_badge in its source.
- Sprint 21 regression: all prior smoke artefacts remain intact.
"""
from __future__ import annotations

import importlib
import pathlib

import pytest

pytestmark = pytest.mark.smoke

_SRC = pathlib.Path(__file__).parent.parent.parent / "src"
_DOCS = pathlib.Path(__file__).parent.parent.parent / "docs"


# ---------------------------------------------------------------------------
# US-089 — db_type badge in history entry
# ---------------------------------------------------------------------------


class TestDbTypeBadgeUS089:
    """Smoke tests for US-089: Display db_type Badge in History Entry."""

    def test_db_type_badge_importable(self) -> None:
        """_db_type_badge is exported from query_history module."""
        mod = importlib.import_module("components.query_history")
        assert hasattr(mod, "_db_type_badge")

    def test_db_type_badge_mysql(self) -> None:
        """_db_type_badge('MySQL') returns dolphin-emoji label."""
        from components.query_history import _db_type_badge
        assert _db_type_badge("MySQL") == "\U0001f42c MySQL"

    def test_db_type_badge_postgresql(self) -> None:
        """_db_type_badge('PostgreSQL') returns elephant-emoji label."""
        from components.query_history import _db_type_badge
        assert _db_type_badge("PostgreSQL") == "\U0001f418 PostgreSQL"

    def test_db_type_badge_mongodb(self) -> None:
        """_db_type_badge('MongoDB') returns leaf-emoji label."""
        from components.query_history import _db_type_badge
        assert _db_type_badge("MongoDB") == "\U0001f343 MongoDB"

    def test_db_type_badge_unknown_passthrough(self) -> None:
        """Unknown db_type is returned unchanged by _db_type_badge."""
        from components.query_history import _db_type_badge
        assert _db_type_badge("Oracle") == "Oracle"

    def test_db_type_badge_used_in_render_source(self) -> None:
        """'_db_type_badge' appears in query_history.py source (render method)."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert "_db_type_badge" in source

    def test_render_caption_uses_badge(self) -> None:
        """render() caption string includes the _db_type_badge call."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert "_db_type_badge(db_type)" in source

    def test_utr_031_exists(self) -> None:
        """UTR-031 artefact file exists."""
        assert (_DOCS / "test-results" / "UTR-031-us089-history-db-type-badge.md").exists()


# ---------------------------------------------------------------------------
# Sprint 22 artefact checks
# ---------------------------------------------------------------------------


class TestSprint22Artefacts:
    """Verify all Sprint 22 pipeline artefacts exist."""

    def test_cr_022_exists(self) -> None:
        """Code review CR-022 exists."""
        assert (_DOCS / "code-reviews" / "CR-022-sprint22-history-display-polish.md").exists()

    def test_tc_141_144_exists(self) -> None:
        """Test cases TC-141-144 exist."""
        assert (_DOCS / "test-cases" / "TC-141-144-sprint22-history-display-polish.md").exists()

    def test_tr_022_exists(self) -> None:
        """TR-022 test results exist."""
        assert (_DOCS / "test-results" / "TR-022-sprint22.md").exists()

    def test_itr_014_exists(self) -> None:
        """ITR-014 integration test results exist."""
        assert (_DOCS / "test-results" / "ITR-014-sprint22.md").exists()


# ---------------------------------------------------------------------------
# Regression — Sprint 21 outputs still intact
# ---------------------------------------------------------------------------


class TestSprint21Regression:
    """Ensure Sprint 21 outputs are intact after Sprint 22 changes."""

    def test_append_to_history_signature_unchanged(self) -> None:
        """_append_to_history still accepts db_type kwarg (Sprint 21 feature)."""
        import inspect
        from components.query_history import _append_to_history
        sig = inspect.signature(_append_to_history)
        assert "db_type" in sig.parameters

    def test_db_type_to_lang_still_works(self) -> None:
        """_db_type_to_lang still returns 'json' for MongoDB (Sprint 21 feature)."""
        from components.query_history import _db_type_to_lang
        assert _db_type_to_lang("MongoDB") == "json"

    def test_clear_history_button_still_in_source(self) -> None:
        """Clear History button string still present (Sprint 21 feature)."""
        source = (_SRC / "components" / "query_history.py").read_text(encoding="utf-8")
        assert "Clear History" in source

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

    def test_str_012_sprint21_still_exists(self) -> None:
        """STR-012 Sprint 21 smoke results still present."""
        assert (_DOCS / "test-results" / "STR-012-sprint21-smoke.md").exists()
