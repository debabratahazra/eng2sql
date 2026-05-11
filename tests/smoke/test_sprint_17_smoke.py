"""Smoke tests for Sprint 17 — Component Coverage Completion.

Covers Sprint 17 user stories:
- US-075: src/components/* removed from coverage omit; gate passes at ≥ 80%
- US-076: Sidebar rendering-method tests exercise Step 2, URI mode, MongoDB Step 2
- US-077: AppTest fixture-sharing investigation; module-scoped read-only fixture added
- US-078: db_connector.py and mongo_connector.py both at 100% coverage

All tests are smoke-level: they verify the Sprint 17 deliverables are present and
structurally correct without requiring a live database.
"""
from __future__ import annotations

import pathlib

import pytest

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")

pytestmark = pytest.mark.smoke


# ---------------------------------------------------------------------------
# US-075: Coverage configuration validation
# ---------------------------------------------------------------------------

class TestCoverageConfigUS075:
    """Verify pyproject.toml omit no longer contains src/components/*."""

    def _read_pyproject(self) -> str:
        path = pathlib.Path(__file__).parent.parent.parent / "pyproject.toml"
        return path.read_text(encoding="utf-8")

    def test_components_not_in_omit(self) -> None:
        """src/components/* is NOT in pyproject.toml coverage omit list."""
        content = self._read_pyproject()
        # Find the omit section and verify the components line is absent
        assert "src/components/*" not in content

    def test_app_py_still_in_omit(self) -> None:
        """src/app.py remains excluded from coverage measurement."""
        content = self._read_pyproject()
        assert '"src/app.py"' in content

    def test_fail_under_is_80(self) -> None:
        """Coverage gate is set to 80%."""
        content = self._read_pyproject()
        assert "fail_under = 80" in content


# ---------------------------------------------------------------------------
# US-076: Rendering-method test file validation
# ---------------------------------------------------------------------------

class TestRenderingTestFileUS076:
    """Verify tests/unit/test_sidebar_rendering.py exists and has expected shape."""

    def _get_test_file_content(self) -> str:
        path = (
            pathlib.Path(__file__).parent.parent
            / "unit"
            / "test_sidebar_rendering.py"
        )
        assert path.exists(), "test_sidebar_rendering.py not found"
        return path.read_text(encoding="utf-8")

    def test_file_exists(self) -> None:
        """tests/unit/test_sidebar_rendering.py exists."""
        path = (
            pathlib.Path(__file__).parent.parent
            / "unit"
            / "test_sidebar_rendering.py"
        )
        assert path.exists()

    def test_file_has_relational_step2_class(self) -> None:
        """File contains TestRelationalStep2 class."""
        content = self._get_test_file_content()
        assert "class TestRelationalStep2" in content

    def test_file_has_mongo_uri_mode_class(self) -> None:
        """File contains TestMongoURIMode class."""
        content = self._get_test_file_content()
        assert "class TestMongoURIMode" in content

    def test_file_has_mongo_step2_class(self) -> None:
        """File contains TestMongoStep2 class."""
        content = self._get_test_file_content()
        assert "class TestMongoStep2" in content

    def test_file_has_default_timeout_30(self) -> None:
        """All AppTest.from_file() calls use default_timeout=30 (xdist safe)."""
        content = self._get_test_file_content()
        # Check no bare AppTest.from_file call without timeout
        import re
        bare_calls = re.findall(r"AppTest\.from_file\([^)]*\)", content)
        for call in bare_calls:
            assert "default_timeout=30" in call, (
                f"Missing default_timeout=30 in: {call!r}"
            )


# ---------------------------------------------------------------------------
# US-077: Fixture investigation validation
# ---------------------------------------------------------------------------

class TestFixtureInvestigationUS077:
    """Verify the initial_app_state fixture and investigation test file exist."""

    def test_conftest_has_initial_app_state_fixture(self) -> None:
        """tests/conftest.py contains the initial_app_state fixture definition."""
        path = pathlib.Path(__file__).parent.parent / "conftest.py"
        content = path.read_text(encoding="utf-8")
        assert "initial_app_state" in content
        assert 'scope="module"' in content

    def test_investigation_test_file_exists(self) -> None:
        """tests/unit/test_apptest_fixture_investigation.py exists."""
        path = (
            pathlib.Path(__file__).parent.parent
            / "unit"
            / "test_apptest_fixture_investigation.py"
        )
        assert path.exists()

    def test_developer_guide_has_apptest_fixture_section(self) -> None:
        """docs/guides/developer-guide.md contains the AppTest Fixture Scoping section."""
        path = (
            pathlib.Path(__file__).parent.parent.parent
            / "docs"
            / "guides"
            / "developer-guide.md"
        )
        content = path.read_text(encoding="utf-8")
        assert "AppTest Fixture Scoping" in content


# ---------------------------------------------------------------------------
# US-078: db_connector coverage artefact validation
# ---------------------------------------------------------------------------

class TestDBConnectorCoverageUS078:
    """Verify UTR-022 artefact exists and db_connector imports cleanly."""

    def test_utr_022_exists(self) -> None:
        """docs/test-results/UTR-022-us078-db-connector-error-branches.md exists."""
        path = (
            pathlib.Path(__file__).parent.parent.parent
            / "docs"
            / "test-results"
            / "UTR-022-us078-db-connector-error-branches.md"
        )
        assert path.exists()

    def test_db_connector_importable(self) -> None:
        """services.db_connector imports without error."""
        from services.db_connector import DBConnector  # noqa: F401
        assert DBConnector is not None

    def test_mongo_connector_importable(self) -> None:
        """services.mongo_connector imports without error."""
        from services.mongo_connector import MongoDBConnector  # noqa: F401
        assert MongoDBConnector is not None


# ---------------------------------------------------------------------------
# Sprint 17 regression smoke: app renders without crash
# ---------------------------------------------------------------------------

class TestAppRegressionSprint17:
    """Full-app regression smoke test after Sprint 17 coverage changes."""

    def test_app_renders_without_crash(self) -> None:
        """App renders without exception after Sprint 17 pyproject.toml change."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        assert not at.exception

    def test_coverage_does_not_break_rendering(self) -> None:
        """Enabling component coverage does not affect Streamlit rendering."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        assert not at.exception
        # Verify the 3-DB-type radio is still present
        radio_labels = [r.label for r in at.radio]
        assert "Database type" in radio_labels
