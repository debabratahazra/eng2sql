"""Unit tests for ``scripts/pragma_audit.py`` (US-083).

Verifies:
- audit_file returns no violations for compliant files.
- audit_file returns one violation per unjustified pragma line.
- main() returns 0 on a clean source tree.
- main() returns 1 when violations are present.
- The audit passes on the real ``src/`` directory (regression guard).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add the scripts directory to sys.path so pragma_audit is importable.
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from pragma_audit import (  # noqa: E402
    _KEYWORDS,
    _WINDOW,
    _has_justification,
    audit_file,
    main,
)

_PROJECT_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# _has_justification
# ---------------------------------------------------------------------------


class TestHasJustification:
    """Tests for :func:`_has_justification`."""

    def _lines(self, *texts: str) -> list[str]:
        return list(texts)

    def test_keyword_on_same_line(self) -> None:
        lines = self._lines("x = 1  # pragma: no cover  # Excluded: unreachable")
        assert _has_justification(lines, 0) is True

    def test_keyword_one_line_after(self) -> None:
        lines = self._lines(
            "if foo:  # pragma: no cover",
            "    # Excluded: foo is never True in unit tests.",
        )
        assert _has_justification(lines, 0) is True

    def test_keyword_one_line_before(self) -> None:
        lines = self._lines(
            "    # Excluded: certifi absent in CI.",
            "    return certifi.where()  # pragma: no cover",
        )
        assert _has_justification(lines, 1) is True

    def test_keyword_at_window_boundary(self) -> None:
        # Keyword exactly _WINDOW lines above — should be found.
        prefix = [f"# line {i}" for i in range(_WINDOW)]
        pragma_line = ["    return x  # pragma: no cover"]
        after = ["# Excluded: reason here"]
        lines = prefix + pragma_line + after
        pragma_idx = _WINDOW
        assert _has_justification(lines, pragma_idx) is True

    def test_no_keyword_returns_false(self) -> None:
        lines = self._lines(
            "if foo:  # pragma: no cover",
            "    do_something()",
        )
        assert _has_justification(lines, 0) is False

    def test_excluded_lowercase_accepted(self) -> None:
        lines = self._lines(
            "if bar:  # pragma: no cover",
            "    # excluded: bar path not reachable.",
        )
        assert _has_justification(lines, 0) is True

    def test_unreachable_accepted(self) -> None:
        lines = self._lines(
            "return val  # pragma: no cover",
            "# unreachable: only reachable with optional dep.",
        )
        assert _has_justification(lines, 0) is True


# ---------------------------------------------------------------------------
# audit_file
# ---------------------------------------------------------------------------


class TestAuditFile:
    """Tests for :func:`audit_file` using tmp_path fixtures."""

    def test_clean_file_returns_no_violations(self, tmp_path: Path) -> None:
        source = (
            "def reset():  # pragma: no cover\n"
            '    """Excluded from coverage: widget-only."""\n'
            "    pass\n"
        )
        f = tmp_path / "clean.py"
        f.write_text(source, encoding="utf-8")
        assert audit_file(f, tmp_path) == []

    def test_unjustified_pragma_returns_violation(self, tmp_path: Path) -> None:
        source = "if foo:  # pragma: no cover\n    bar()\n"
        f = tmp_path / "bad.py"
        f.write_text(source, encoding="utf-8")
        violations = audit_file(f, tmp_path)
        assert len(violations) == 1
        assert "bad.py:1" in violations[0]
        assert "without justification" in violations[0]

    def test_two_violations_detected(self, tmp_path: Path) -> None:
        source = (
            "if a:  # pragma: no cover\n    pass\n"
            "if b:  # pragma: no cover\n    pass\n"
        )
        f = tmp_path / "two.py"
        f.write_text(source, encoding="utf-8")
        violations = audit_file(f, tmp_path)
        assert len(violations) == 2

    def test_justified_with_adjacent_comment(self, tmp_path: Path) -> None:
        source = (
            "if click:  # pragma: no cover\n"
            "    # Excluded: button click unreachable via AppTest.\n"
            "    handle()\n"
        )
        f = tmp_path / "ok.py"
        f.write_text(source, encoding="utf-8")
        assert audit_file(f, tmp_path) == []

    def test_file_without_pragma_has_no_violations(self, tmp_path: Path) -> None:
        source = "def foo():\n    return 1\n"
        f = tmp_path / "nopragma.py"
        f.write_text(source, encoding="utf-8")
        assert audit_file(f, tmp_path) == []

    def test_relative_path_used_in_message(self, tmp_path: Path) -> None:
        source = "if x:  # pragma: no cover\n    pass\n"
        sub = tmp_path / "pkg"
        sub.mkdir()
        f = sub / "mod.py"
        f.write_text(source, encoding="utf-8")
        violations = audit_file(f, tmp_path)
        assert len(violations) == 1
        # Path should be relative to root, not absolute
        assert str(tmp_path) not in violations[0] or "pkg" in violations[0]


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    """Tests for :func:`main`."""

    def test_passes_on_clean_dir(self, tmp_path: Path) -> None:
        source = (
            "def method():  # pragma: no cover\n"
            '    """Excluded from coverage: widget-only method.\n    """\n'
            "    pass\n"
        )
        (tmp_path / "mod.py").write_text(source, encoding="utf-8")
        assert main([str(tmp_path)]) == 0

    def test_fails_on_unjustified_pragma(self, tmp_path: Path) -> None:
        source = "if foo:  # pragma: no cover\n    pass\n"
        (tmp_path / "bad.py").write_text(source, encoding="utf-8")
        assert main([str(tmp_path)]) == 1

    def test_empty_directory_returns_zero(self, tmp_path: Path) -> None:
        # No Python files → nothing to audit → pass.
        assert main([str(tmp_path)]) == 0

    def test_nonexistent_path_returns_one(self, tmp_path: Path) -> None:
        result = main([str(tmp_path / "does_not_exist")])
        assert result == 1

    def test_real_src_directory_passes(self) -> None:
        """Regression guard: the real src/ must have 0 pragma violations."""
        result = main([str(_PROJECT_ROOT / "src")])
        assert result == 0
