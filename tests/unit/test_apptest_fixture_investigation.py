"""AppTest fixture-sharing investigation (US-077).

Tests that verify:
1. The module-scoped ``initial_app_state`` fixture returns a valid read-only snapshot.
2. Interactive (stateful) tests MUST use function-scoped AppTest to remain isolated.
3. Timing comparison is measured and recorded in the docstring below.

INVESTIGATION RESULTS
---------------------
Benchmark environment: Windows 11, Python 3.14.3, Streamlit 1.35+, 12 CPU cores.

                        Function-scoped   Module-scoped (read-only)
  AppTest cold start:   ~1.1 – 4.7 s /   ~1.1 – 4.7 s total for module
  Per-test overhead:    ~1.1 – 4.7 s     ~0 s (reuse shared instance)
  Safety for mutations: ✅ SAFE           ❌ UNSAFE — dirty state bleeds between tests
  Safety for read-only: ✅ SAFE           ✅ SAFE — shared render is identical

CONCLUSION
----------
- **Interactive tests**: always use ``AppTest.from_file(APP_PATH, default_timeout=30)``
  inside the test function (function scope).
- **Read-only initial-state checks**: may use the ``initial_app_state`` module-scoped
  fixture from ``tests/conftest.py`` for a minor speedup (~1–5 s per test saved).
- **xdist compatibility**: module-scoped fixtures are safe with ``-n auto`` because
  xdist distributes entire files to workers; tests within a module run sequentially
  on one worker.  However, since most tests ARE interactive, the function-scoped
  pattern dominates the suite and the overall gain is marginal.
"""
from __future__ import annotations

import pathlib
import time

import pytest

APP_PATH = str(pathlib.Path(__file__).parent.parent.parent / "src" / "app.py")


# ---------------------------------------------------------------------------
# Validate the module-scoped fixture (read-only checks)
# ---------------------------------------------------------------------------

class TestInitialAppStateFixture:
    """Verify the shared ``initial_app_state`` fixture works correctly."""

    def test_no_exception_on_initial_render(self, initial_app_state) -> None:
        """The shared fixture renders the app without exception."""
        assert not initial_app_state.exception

    def test_db_type_defaults_to_mysql(self, initial_app_state) -> None:
        """Initial render has the DB-type radio defaulting to MySQL."""
        assert initial_app_state.radio[0].value == "MySQL"

    def test_initial_session_state_db_type(self, initial_app_state) -> None:
        """Session state key 'db_type' is set to 'MySQL' on first render."""
        assert initial_app_state.session_state["db_type"] == "MySQL"

    def test_generated_sql_empty_on_initial_render(self, initial_app_state) -> None:
        """'generated_sql' starts empty — no query has been run yet."""
        assert initial_app_state.session_state["generated_sql"] == ""

    def test_connect_button_present_in_sidebar(self, initial_app_state) -> None:
        """The MySQL 'Connect' button is present in the sidebar on initial render."""
        button_labels = [b.label for b in initial_app_state.button]
        assert "Connect" in button_labels


# ---------------------------------------------------------------------------
# Demonstrate that interactive tests MUST use function scope
# ---------------------------------------------------------------------------

class TestInteractiveTestsRequireFunctionScope:
    """Show that interactive tests need their own fresh AppTest instance."""

    def test_radio_change_does_not_affect_other_tests(self) -> None:
        """Changing the DB-type radio in one test does NOT bleed into another.

        This test creates its own AppTest, switches to MongoDB, and verifies
        the session state is updated.  Because it's function-scoped it cannot
        contaminate the module-scoped ``initial_app_state`` fixture.
        """
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        at.radio[0].set_value("MongoDB")
        at.run()
        assert not at.exception
        assert at.session_state["db_type"] == "MongoDB"

    def test_subsequent_read_only_check_still_sees_mysql(self, initial_app_state) -> None:
        """The shared fixture still shows MySQL after the previous test mutated its own AT."""
        # This confirms the module-scoped fixture's state is unaffected by
        # the function-scoped test above that switched to MongoDB.
        assert initial_app_state.session_state["db_type"] == "MySQL"


# ---------------------------------------------------------------------------
# Timing measurement (informational — not a correctness test)
# ---------------------------------------------------------------------------

class TestAppTestStartupTiming:
    """Measure AppTest startup overhead for the benchmark record."""

    def test_function_scoped_startup_time_recorded(self) -> None:
        """Record the wall-clock time for a single function-scoped AppTest cold start."""
        from streamlit.testing.v1 import AppTest

        start = time.perf_counter()
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        elapsed = time.perf_counter() - start

        assert not at.exception
        # No strict time assertion — this test records timing for the benchmark.
        # Observed range on dev machine: 1.0 – 4.7 s depending on system load.
        assert elapsed < 30.0, f"AppTest cold start took {elapsed:.2f}s — unexpectedly slow"
