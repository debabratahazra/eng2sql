"""Smoke tests for Sprint 19 — Maintainability & Developer Experience.

Covers Sprint 19 user stories:
- US-082: README.md contains a shields.io 100% coverage badge
- US-083: scripts/pragma_audit.py exists, passes on src/, and runs in CI
- US-084: developer-guide.md Widget-Component Extraction Guideline + ADR-007

All tests are smoke-level: they verify Sprint 19 deliverables are present and
structurally correct without requiring a live database or Streamlit runtime.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

_ROOT = pathlib.Path(__file__).parent.parent.parent

pytestmark = pytest.mark.smoke


# ---------------------------------------------------------------------------
# US-082: Coverage badge in README.md
# ---------------------------------------------------------------------------


class TestCoverageBadgeUS082:
    """Verify the shields.io 100% coverage badge is present in README.md."""

    def _readme(self) -> str:
        path = _ROOT / "README.md"
        assert path.exists(), "README.md not found"
        return path.read_text(encoding="utf-8")

    def test_shields_io_badge_present(self) -> None:
        """README.md contains a shields.io coverage badge URL."""
        assert "img.shields.io/badge/coverage" in self._readme()

    def test_badge_shows_100_percent(self) -> None:
        """The badge text reflects 100% coverage."""
        assert "100%25" in self._readme()

    def test_badge_has_brightgreen_color(self) -> None:
        """The badge uses brightgreen to indicate full coverage."""
        assert "brightgreen" in self._readme()

    def test_codecov_placeholder_removed(self) -> None:
        """The placeholder Codecov badge pointing at 'your-org' is gone."""
        assert "codecov.io/gh/your-org" not in self._readme()


# ---------------------------------------------------------------------------
# US-083: pragma_audit.py script
# ---------------------------------------------------------------------------


class TestPragmaAuditScriptUS083:
    """Verify scripts/pragma_audit.py is present, correct, and passes."""

    def test_pragma_audit_script_exists(self) -> None:
        """scripts/pragma_audit.py exists."""
        assert (_ROOT / "scripts" / "pragma_audit.py").exists()

    def test_pragma_audit_has_main_function(self) -> None:
        """pragma_audit.py defines a main() function."""
        content = (_ROOT / "scripts" / "pragma_audit.py").read_text(encoding="utf-8")
        assert "def main(" in content

    def test_pragma_audit_has_audit_file_function(self) -> None:
        """pragma_audit.py defines an audit_file() function."""
        content = (_ROOT / "scripts" / "pragma_audit.py").read_text(encoding="utf-8")
        assert "def audit_file(" in content

    def test_pragma_audit_passes_on_src(self) -> None:
        """Running pragma_audit.py on src/ exits with code 0."""
        result = subprocess.run(
            [sys.executable, str(_ROOT / "scripts" / "pragma_audit.py"),
             str(_ROOT / "src")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"pragma_audit failed:\n{result.stderr}"
        )

    def test_pragma_audit_stdout_confirms_pass(self) -> None:
        """pragma_audit.py prints '0 violations' on a clean run."""
        result = subprocess.run(
            [sys.executable, str(_ROOT / "scripts" / "pragma_audit.py"),
             str(_ROOT / "src")],
            capture_output=True,
            text=True,
        )
        assert "0 violations" in result.stdout

    def test_ci_yml_contains_pragma_audit_step(self) -> None:
        """.github/workflows/ci-cd.yml contains the pragma audit step."""
        ci = (_ROOT / ".github" / "workflows" / "ci-cd.yml").read_text(encoding="utf-8")
        assert "pragma_audit.py" in ci

    def test_sidebar_certifi_pragma_has_justification(self) -> None:
        """The certifi pragma in sidebar.py has an adjacent justification comment."""
        content = (_ROOT / "src" / "components" / "sidebar.py").read_text(encoding="utf-8")
        assert "Excluded: certifi is an optional" in content

    def test_unit_test_file_for_pragma_audit_exists(self) -> None:
        """tests/unit/test_pragma_audit.py was created for US-083."""
        assert (_ROOT / "tests" / "unit" / "test_pragma_audit.py").exists()


# ---------------------------------------------------------------------------
# US-083: UTR-025 artefact
# ---------------------------------------------------------------------------


class TestUTRArtefactUS083:
    """Verify UTR-025 result document exists."""

    def test_utr_025_exists(self) -> None:
        """docs/test-results/UTR-025-us083-pragma-audit-ci.md exists."""
        path = _ROOT / "docs" / "test-results" / "UTR-025-us083-pragma-audit-ci.md"
        assert path.exists()

    def test_utr_025_reports_18_tests(self) -> None:
        """UTR-025 documents 18 unit tests for US-083."""
        content = (_ROOT / "docs" / "test-results" / "UTR-025-us083-pragma-audit-ci.md"
                   ).read_text(encoding="utf-8")
        assert "18 passed" in content


# ---------------------------------------------------------------------------
# US-084: Widget-component extraction guideline
# ---------------------------------------------------------------------------


class TestWidgetExtractionGuidelineUS084:
    """Verify developer-guide.md section and ADR-007."""

    def _devguide(self) -> str:
        return (_ROOT / "docs" / "guides" / "developer-guide.md").read_text(
            encoding="utf-8"
        )

    def test_developer_guide_has_extraction_section(self) -> None:
        """developer-guide.md contains 'Widget-Component Extraction Guideline'."""
        assert "Widget-Component Extraction Guideline" in self._devguide()

    def test_developer_guide_section_has_worked_example(self) -> None:
        """The section includes the _append_step worked example."""
        assert "_append_step" in self._devguide()

    def test_developer_guide_section_has_checklist(self) -> None:
        """The section includes a pre-commit checklist."""
        assert "Pre-commit checklist" in self._devguide()

    def test_adr_007_exists(self) -> None:
        """docs/architecture/ADR-007-widget-extraction-pattern.md exists."""
        path = _ROOT / "docs" / "architecture" / "ADR-007-widget-extraction-pattern.md"
        assert path.exists()

    def test_adr_007_has_decision_section(self) -> None:
        """ADR-007 contains a Decision section."""
        content = (
            _ROOT / "docs" / "architecture" / "ADR-007-widget-extraction-pattern.md"
        ).read_text(encoding="utf-8")
        assert "## Decision" in content

    def test_adr_007_has_consequences_section(self) -> None:
        """ADR-007 contains a Consequences section."""
        content = (
            _ROOT / "docs" / "architecture" / "ADR-007-widget-extraction-pattern.md"
        ).read_text(encoding="utf-8")
        assert "## Consequences" in content


# ---------------------------------------------------------------------------
# General regression check
# ---------------------------------------------------------------------------


class TestGeneralRegressionSprint19:
    """Verify Sprint 18 artefacts remain intact after Sprint 19 changes."""

    def test_sprint_18_smoke_file_intact(self) -> None:
        """Sprint 18 smoke test file still exists."""
        assert (_ROOT / "tests" / "smoke" / "test_sprint_18_smoke.py").exists()

    def test_utr_023_intact(self) -> None:
        """Sprint 18 UTR-023 still exists."""
        assert (_ROOT / "docs" / "test-results" / "UTR-023-us079-pragma-no-cover.md"
                ).exists()

    def test_coverage_gate_still_100(self) -> None:
        """TR-019 documents 100.00% coverage for Sprint 19."""
        path = _ROOT / "docs" / "test-results" / "TR-019-sprint19.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "100.00%" in content
