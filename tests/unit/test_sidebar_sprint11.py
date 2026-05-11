"""Sprint 11 sidebar tests — US-052 (configurable admin DB) + US-056 (sslmode pre-validation)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

APP_PATH = "src/app.py"


def _select_postgres(at: object) -> None:
    at.session_state["db_type"] = "PostgreSQL"  # type: ignore[attr-defined]


class TestConfigurableAdminDb:
    """US-052 — Step 1 admin DB is configurable."""

    def test_admin_db_default_is_postgres(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _select_postgres(at)
        at.run()
        assert at.session_state["pg_admin_db"] == "postgres"

    def test_custom_admin_db_propagates_into_dbconfig(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _select_postgres(at)
        at.run()
        # Pre-seed the custom admin DB and form values
        at.session_state["pg_admin_db"] = "defaultdb"
        at.session_state["pg_host"] = "pg.example.com"
        at.session_state["pg_user"] = "alice"

        # Patch the connector to capture the DBConfig.database value
        captured: dict[str, object] = {}

        def fake_create_engine(cfg: object) -> object:
            captured["database"] = cfg.database  # type: ignore[attr-defined]
            captured["dialect"] = cfg.dialect  # type: ignore[attr-defined]
            return MagicMock()

        with patch(
            "services.db_connector.DBConnector.create_engine",
            side_effect=fake_create_engine,
        ), patch(
            "services.db_connector.DBConnector.list_databases",
            return_value=["a", "b"],
        ):
            at.run()
            # Provide password via the password input widget; AppTest stores it
            # in the widget key, but we can simulate by writing the input value
            # and clicking Connect.
            for ti in at.text_input:
                if ti.key == "pg_admin_db_input":
                    ti.set_value("defaultdb")
                if ti.key == "pg_user_input":
                    ti.set_value("alice")
                if ti.key == "pg_host_input":
                    ti.set_value("pg.example.com")
            for pwd in at.text_input:
                if pwd.key == "pg_password_input":
                    pwd.set_value("secret")
            # Click Connect button
            for btn in at.button:
                if btn.key == "pg_connect":
                    btn.click()
            at.run()

        assert captured.get("database") == "defaultdb"
        assert captured.get("dialect") == "postgresql"

    def test_empty_admin_db_rejected(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _select_postgres(at)
        at.run()
        for ti in at.text_input:
            if ti.key == "pg_admin_db_input":
                ti.set_value("")
            if ti.key == "pg_host_input":
                ti.set_value("h")
            if ti.key == "pg_user_input":
                ti.set_value("u")
            if ti.key == "pg_password_input":
                ti.set_value("p")
        for btn in at.button:
            if btn.key == "pg_connect":
                btn.click()
        at.run()
        status = at.session_state["pg_step1_status"] if "pg_step1_status" in at.session_state else None
        assert status is not None
        assert status[0] == "warning"
        assert "Admin DB" in status[1]


class TestSslmodeCaPrevalidation:
    """US-056 — verify-* sslmode warns when no CA bundle is available."""

    def test_warning_shown_for_verify_ca_without_bundle(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _select_postgres(at)
        at.session_state["pg_sslmode"] = "verify-ca"
        with patch(
            "components.sidebar._ca_bundle_available", return_value=False
        ):
            at.run()
        warning_texts = [w.value for w in at.warning]
        assert any("CA bundle" in t for t in warning_texts)

    def test_no_warning_for_prefer_sslmode(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _select_postgres(at)
        at.session_state["pg_sslmode"] = "prefer"
        with patch(
            "components.sidebar._ca_bundle_available", return_value=False
        ):
            at.run()
        warning_texts = [w.value for w in at.warning]
        assert not any("CA bundle" in t for t in warning_texts)

    def test_no_warning_when_bundle_available(self) -> None:
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(APP_PATH, default_timeout=10)
        at.run()
        _select_postgres(at)
        at.session_state["pg_sslmode"] = "verify-full"
        with patch(
            "components.sidebar._ca_bundle_available", return_value=True
        ):
            at.run()
        warning_texts = [w.value for w in at.warning]
        assert not any("CA bundle" in t for t in warning_texts)


class TestCaBundleHelper:
    """Direct tests for the helper itself."""

    def test_returns_true_when_env_var_points_at_existing_file(
        self, tmp_path: object
    ) -> None:
        from components.sidebar import _ca_bundle_available

        ca = tmp_path / "ca.crt"  # type: ignore[operator]
        ca.write_text("dummy")
        with patch.dict("os.environ", {"PGSSLROOTCERT": str(ca)}, clear=False):
            assert _ca_bundle_available() is True

    def test_returns_false_when_no_source_exists(self, tmp_path: object) -> None:
        from components.sidebar import _ca_bundle_available

        # Point env at non-existent path; mock home() so default path also misses
        with patch.dict(
            "os.environ", {"PGSSLROOTCERT": str(tmp_path / "missing.crt")},  # type: ignore[operator]
            clear=False,
        ):
            with patch("components.sidebar.pathlib.Path.home", return_value=tmp_path):
                with patch.dict("sys.modules", {"certifi": None}):
                    # When certifi import fails, helper returns False
                    assert _ca_bundle_available() is False
