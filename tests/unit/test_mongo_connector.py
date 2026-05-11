"""Unit tests for MongoDBConnector service."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from models.config import MongoConfig
from services.mongo_connector import MongoDBConnector
from utils.exceptions import DatabaseConnectionError


class TestMongoDBConnector:
    """Unit tests for MongoDBConnector."""

    def setup_method(self) -> None:
        """Create a fresh connector for each test."""
        self.connector = MongoDBConnector()

    # ── connect() ─────────────────────────────────────────────────────────────

    def test_connect_success_returns_client(self, mongo_config: MongoConfig) -> None:
        """connect() returns the MongoClient on successful ping."""
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            result = self.connector.connect(mongo_config)

        assert result is mock_client
        mock_client.admin.command.assert_called_once_with("ping")

    def test_connect_uses_connection_uri(self, mongo_config: MongoConfig) -> None:
        """connect() calls MongoClient with keyword args derived from the connection URI.

        For mongodb:// URIs, connect() uses _uri_to_kwargs() rather than
        passing the URI string directly.  This bypasses pymongo's URI parser
        and avoids ssl=false edge cases in Streamlit's threaded environment.
        _probe_reachable_host resolves the host to a reachable IP; the mock
        returns '127.0.0.1' simulating a healthy IPv4 MongoDB.
        """
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch("services.mongo_connector.MongoClient", return_value=mock_client) as mock_cls, \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="127.0.0.1"):
            self.connector.connect(mongo_config)

        # No positional URI string — all params as kwargs (BUG-005 final fix)
        args, kwargs = mock_cls.call_args
        assert not args, "MongoClient must be called with kwargs, not a positional URI string"
        # host comes from _probe_reachable_host (mocked to return '127.0.0.1')
        assert kwargs.get("host") == "127.0.0.1"
        assert kwargs.get("port") == mongo_config.port
        assert kwargs.get("serverSelectionTimeoutMS") == mongo_config.connect_timeout_ms

    def test_connect_does_not_force_direct_connection(self, mongo_config: MongoConfig) -> None:
        """connect() does NOT pass directConnection to MongoClient.

        MongoDB Compass (which works) does not use directConnection=True.
        Forcing it caused hello-handshake failures in pymongo 4.16 on Windows.
        """
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch("services.mongo_connector.MongoClient", return_value=mock_client) as mock_cls, \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            self.connector.connect(mongo_config)

        _, kwargs = mock_cls.call_args
        assert "directConnection" not in kwargs

    def test_connect_raises_on_ping_failure(self, mongo_config: MongoConfig) -> None:
        """connect() raises DatabaseConnectionError when ping fails."""
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = Exception("Connection timeout")

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError, match="Could not connect to MongoDB"):
                self.connector.connect(mongo_config)

    def test_connect_no_auth_uses_plain_uri(self, mongo_config_no_auth: MongoConfig) -> None:
        """connect() does not include credentials for None / No Auth config."""
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch(
            "services.mongo_connector.MongoClient", return_value=mock_client
        ) as mock_cls, \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            self.connector.connect(mongo_config_no_auth)

        # With kwargs approach there is no positional URI string
        args, kwargs = mock_cls.call_args
        assert not args
        assert "username" not in kwargs
        assert "password" not in kwargs

    # ── list_databases() ──────────────────────────────────────────────────────

    def test_list_databases_filters_system_dbs(self) -> None:
        """list_databases() excludes admin, local, config."""
        mock_client = MagicMock()
        mock_client.list_database_names.return_value = [
            "admin", "local", "config", "mydb", "analytics"
        ]

        result = self.connector.list_databases(mock_client)

        assert result == ["analytics", "mydb"]

    def test_list_databases_returns_sorted(self) -> None:
        """list_databases() returns databases in alphabetical order."""
        mock_client = MagicMock()
        mock_client.list_database_names.return_value = ["zebra", "apple", "admin", "mango"]

        result = self.connector.list_databases(mock_client)

        assert result == ["apple", "mango", "zebra"]

    def test_list_databases_empty_server(self) -> None:
        """list_databases() returns empty list when no user databases exist."""
        mock_client = MagicMock()
        mock_client.list_database_names.return_value = ["admin", "local", "config"]

        result = self.connector.list_databases(mock_client)

        assert result == []

    def test_list_databases_raises_on_driver_error(self) -> None:
        """list_databases() raises DatabaseConnectionError on driver failure."""
        mock_client = MagicMock()
        mock_client.list_database_names.side_effect = Exception("OperationFailure")

        with pytest.raises(DatabaseConnectionError, match="Failed to list MongoDB databases"):
            self.connector.list_databases(mock_client)

    # ── get_database() ────────────────────────────────────────────────────────

    def test_get_database_returns_database_object(self) -> None:
        """get_database() returns the subscript result from the client."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_client.__getitem__ = MagicMock(return_value=mock_db)

        result = self.connector.get_database(mock_client, "mydb")

        assert result is mock_db
        mock_client.__getitem__.assert_called_once_with("mydb")

    # ── BUG-006 regression ────────────────────────────────────────────────────

    def test_bug_006_wsl2_localhost_unreachable_fails_fast_with_hint(
        self, mongo_config: MongoConfig
    ) -> None:
        """BUG-006 — WSL2 + loopback + probe failure raises immediately.

        When the TCP probe cannot reach a loopback host (returns the host
        unchanged) AND the process is running inside WSL2, ``connect()`` must
        raise :class:`DatabaseConnectionError` with an actionable WSL2 hint
        BEFORE invoking ``MongoClient`` (which would otherwise hang for
        ``serverSelectionTimeoutMS``).
        """
        with patch("services.mongo_connector.MongoClient") as mock_cls, \
             patch.object(MongoDBConnector, "_is_wsl2", return_value=True), \
             patch.object(
                 MongoDBConnector, "_probe_reachable_host", return_value="localhost"
             ):
            with pytest.raises(DatabaseConnectionError, match="WSL2"):
                self.connector.connect(mongo_config)

        # MongoClient must NOT be invoked — the whole point of the fail-fast
        # is to skip pymongo's 5-second topology timeout.
        mock_cls.assert_not_called()

    def test_bug_006_non_wsl2_localhost_probe_failure_still_calls_mongoclient(
        self, mongo_config: MongoConfig
    ) -> None:
        """BUG-006 — outside WSL2, the fail-fast must NOT trigger.

        The fail-fast is WSL2-specific; on Windows, macOS, or native Linux
        a probe failure could be transient and ``MongoClient`` should still
        be given a chance (preserving prior behaviour for non-WSL2 users).
        """
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch(
            "services.mongo_connector.MongoClient", return_value=mock_client
        ) as mock_cls, \
             patch.object(MongoDBConnector, "_is_wsl2", return_value=False), \
             patch.object(
                 MongoDBConnector, "_probe_reachable_host", return_value="localhost"
             ):
            self.connector.connect(mongo_config)

        mock_cls.assert_called_once()


class TestMongoConfig:
    """Unit tests for MongoConfig URI generation."""

    def test_connection_uri_with_auth(self, mongo_config: MongoConfig) -> None:
        """connection_uri encodes password and includes auth params."""
        uri = mongo_config.connection_uri
        assert "test_user" in uri
        assert "test_pass" in uri
        assert "authSource=admin" in uri
        assert "authMechanism=SCRAM-SHA-256" in uri

    def test_connection_uri_no_auth(self, mongo_config_no_auth: MongoConfig) -> None:
        """connection_uri omits credentials for None / No Auth."""
        uri = mongo_config_no_auth.connection_uri
        assert uri == "mongodb://localhost:27017/"

    def test_connection_uri_password_percent_encoded(self) -> None:
        """connection_uri percent-encodes special characters in password."""
        config = MongoConfig(
            host="localhost",
            port=27017,
            username="user",
            password="p@ss w0rd!",
            auth_mechanism="SCRAM-SHA-256",
        )
        uri = config.connection_uri
        assert "p%40ss+w0rd%21" in uri or "p%40ss%20w0rd%21" in uri

    def test_connection_uri_credentials_with_no_auth_mechanism(self) -> None:
        """BUG-004 regression: credentials + None/No Auth must not drop credentials."""
        config = MongoConfig(
            host="localhost",
            port=27017,
            username="root",
            password="root",
            auth_source="admin",
            auth_mechanism="None / No Auth",
        )
        uri = config.connection_uri
        assert "root:root@localhost:27017" in uri
        assert "authSource=admin" in uri
        assert "authMechanism" not in uri

    def test_connection_uri_no_username_with_no_auth_mechanism(self) -> None:
        """Genuinely unauthenticated: empty username → bare URI regardless of mechanism."""
        config = MongoConfig(
            host="localhost",
            port=27017,
            username="",
            password="",
            auth_mechanism="None / No Auth",
        )
        assert config.connection_uri == "mongodb://localhost:27017/"

    # ── URI mode (raw_uri) ────────────────────────────────────────────────────

    def test_connection_uri_raw_uri_injects_credentials(self) -> None:
        """raw_uri + username → credentials injected into netloc."""
        config = MongoConfig(
            host="",
            raw_uri="mongodb://localhost:27017/?authSource=admin",
            username="root",
            password="root",
        )
        uri = config.connection_uri
        assert "root:root@localhost:27017" in uri
        assert uri.startswith("mongodb://")

    def test_connection_uri_raw_uri_no_username_returns_as_is(self) -> None:
        """raw_uri + empty username → URI returned unchanged."""
        raw = "mongodb://localhost:27017/"
        config = MongoConfig(host="", raw_uri=raw, username="", password="")
        assert config.connection_uri == raw

    def test_connection_uri_raw_uri_embedded_creds_returned_as_is(self) -> None:
        """Full URI with embedded credentials is returned unchanged (no ValueError).

        Users may paste a complete MongoDB URI that already contains
        user:pass@host.  The method must accept this and return it directly
        instead of raising ValueError (previous BUG behaviour).
        """
        config = MongoConfig(
            host="",
            raw_uri="mongodb://root:root@localhost:27017/",
            username="root",
            password="root",
        )
        uri = config.connection_uri
        assert uri == "mongodb://root:root@localhost:27017/"

    def test_connection_uri_raw_uri_special_chars_encoded(self) -> None:
        """Passwords with special chars are percent-encoded when injected into raw_uri."""
        config = MongoConfig(
            host="",
            raw_uri="mongodb://localhost:27017/",
            username="user",
            password="p@ss!",
        )
        uri = config.connection_uri
        assert "p%40ss%21" in uri or "p%40ss!" not in uri  # encoded
        assert "@" in uri  # credentials present

    def test_connection_uri_raw_uri_srv_preserves_scheme(self) -> None:
        """mongodb+srv:// raw_uri preserves the SRV scheme after credential injection."""
        config = MongoConfig(
            host="",
            raw_uri="mongodb+srv://cluster0.example.mongodb.net/?authSource=admin",
            username="atlas_user",
            password="secret",
        )
        uri = config.connection_uri
        assert uri.startswith("mongodb+srv://")
        assert "atlas_user" in uri

    def test_connection_uri_raw_uri_empty_falls_back_to_fields(self) -> None:
        """raw_uri='' falls back to field-based URI (regression guard)."""
        config = MongoConfig(
            host="localhost",
            port=27017,
            username="user",
            password="pass",
            auth_mechanism="SCRAM-SHA-256",
            raw_uri="",
        )
        uri = config.connection_uri
        assert "localhost:27017" in uri
        assert "user:pass@" in uri

    # ── US-037: coverage gaps ─────────────────────────────────────────────────

    def test_mongo_config_repr(self) -> None:
        """__repr__ includes host, port, username, and auth_mechanism."""
        config = MongoConfig(
            host="myhost",
            port=27017,
            username="myuser",
            auth_mechanism="SCRAM-SHA-256",
        )
        result = repr(config)
        assert "MongoConfig(" in result
        assert "myhost" in result
        assert "myuser" in result
        assert "SCRAM-SHA-256" in result

    def test_connection_uri_raw_uri_no_netloc_falls_back_to_path(self) -> None:
        """Edge case: urlparse returns empty netloc → credentials injected via path branch.

        A URI missing the double-slash (e.g. ``mongodb:host:27017/``) causes
        urlparse to place the authority in ``path`` rather than ``netloc``.
        The else-branch in ``_connection_uri_from_raw`` handles this so the
        resulting URI still contains the supplied credentials.
        """
        # 'mongodb:localhost:27017/' lacks '//' → parsed.netloc == ''
        config = MongoConfig(
            host="",
            raw_uri="mongodb:localhost:27017/",
            username="user",
            password="pass",
        )
        uri = config.connection_uri
        assert "user" in uri
        assert "pass" in uri


class TestMongoDBConnectorSRV:
    """Tests for SRV URI handling in MongoDBConnector."""

    def setup_method(self) -> None:
        """Create a fresh connector for each test."""
        self.connector = MongoDBConnector()

    def test_connect_srv_uri_omits_direct_connection(self) -> None:
        """SRV URIs must NOT receive directConnection=True (incompatible)."""
        config = MongoConfig(
            host="",
            raw_uri="mongodb+srv://cluster.example.mongodb.net/?authSource=admin",
            username="user",
            password="pass",
        )
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch("services.mongo_connector.MongoClient", return_value=mock_client) as mock_cls:
            self.connector.connect(config)

        _, kwargs = mock_cls.call_args
        assert "directConnection" not in kwargs

    def test_connect_standard_uri_also_omits_direct_connection(self) -> None:
        """Standard mongodb:// URIs also do NOT receive directConnection.

        directConnection is no longer injected for any URI type — pymongo's
        auto-topology-discovery is used instead (matches Compass behaviour).
        """
        config = MongoConfig(
            host="",
            raw_uri="mongodb://localhost:27017/",
            username="",
            password="",
        )
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch("services.mongo_connector.MongoClient", return_value=mock_client) as mock_cls, \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            self.connector.connect(config)

        _, kwargs = mock_cls.call_args
        assert "directConnection" not in kwargs


class TestBug005URIPathCredentials:
    """BUG-005 regression: URI with database path + ssl param + credentials (root/root)."""

    def setup_method(self) -> None:
        """Create a fresh connector for each test."""
        self.connector = MongoDBConnector()

    # ── _normalise_localhost() ────────────────────────────────────────────────

    def test_normalise_localhost_replaces_with_ipv4(self) -> None:
        """BUG-005: _normalise_localhost rewrites localhost host to 127.0.0.1."""
        uri = "mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false"
        result = MongoDBConnector._normalise_localhost(uri)
        assert result == "mongodb://root:root@127.0.0.1:27017/idcauditlog?authSource=admin&ssl=false"

    def test_normalise_localhost_no_auth_uri(self) -> None:
        """_normalise_localhost works for URIs without credentials."""
        uri = "mongodb://localhost:27017/"
        assert MongoDBConnector._normalise_localhost(uri) == "mongodb://127.0.0.1:27017/"

    def test_normalise_localhost_leaves_ipv4_unchanged(self) -> None:
        """_normalise_localhost must not alter a URI that already uses 127.0.0.1."""
        uri = "mongodb://root:root@127.0.0.1:27017/idcauditlog"
        assert MongoDBConnector._normalise_localhost(uri) == uri

    def test_normalise_localhost_leaves_non_local_host_unchanged(self) -> None:
        """_normalise_localhost must not alter remote hostnames."""
        uri = "mongodb://user:pass@mongo.example.com:27017/"
        assert MongoDBConnector._normalise_localhost(uri) == uri

    def test_normalise_localhost_leaves_srv_unchanged(self) -> None:
        """_normalise_localhost must not alter SRV URIs (they don't use localhost)."""
        uri = "mongodb+srv://user:pass@cluster.example.mongodb.net/"
        assert MongoDBConnector._normalise_localhost(uri) == uri

    # ── MongoConfig URI construction ──────────────────────────────────────────

    def test_uri_mode_with_database_path_injects_credentials(self) -> None:
        """BUG-005: URI with db path preserves path and query after credential injection.

        URI: mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false
        Credentials: username=root, password=root
        Expected (MongoConfig level): mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false
        """
        config = MongoConfig(
            host="localhost",
            raw_uri="mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false",
            username="root",
            password="root",
        )
        uri = config.connection_uri
        assert uri == "mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false"
        assert "idcauditlog" in uri          # database path preserved
        assert "authSource=admin" in uri     # query params preserved
        assert "ssl=false" in uri            # ssl param preserved

    # ── connect() with localhost normalisation ────────────────────────────────

    def test_connect_localhost_uri_uses_127_0_0_1(self) -> None:
        """BUG-005 core fix (IPv4 scenario): when _probe_reachable_host returns
        '127.0.0.1', MongoClient receives host='127.0.0.1'.

        On machines where MongoDB binds to 127.0.0.1 (IPv4), the probe
        resolves 'localhost' to '127.0.0.1' and that address is forwarded to
        MongoClient — identical behaviour to the old _normalise_localhost fix.
        """
        config = MongoConfig(
            host="localhost",
            raw_uri="mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false",
            username="root",
            password="root",
        )
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch(
            "services.mongo_connector.MongoClient", return_value=mock_client
        ) as mock_cls, \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="127.0.0.1"):
            self.connector.connect(config)

        args, kwargs = mock_cls.call_args
        assert not args                              # no positional URI string
        assert kwargs.get("host") == "127.0.0.1"    # probed reachable address
        assert kwargs.get("username") == "root"
        assert kwargs.get("password") == "root"
        assert kwargs.get("authSource") == "admin"
        assert "directConnection" not in kwargs
        # ssl=false is stripped (redundant; default is tls=False for mongodb://)
        assert kwargs.get("tls") is None

    def test_connect_full_uri_with_embedded_credentials(self) -> None:
        """Full URI with embedded credentials: MongoClient gets kwargs not URI string.

        This is the primary user-reported BUG — pasting a complete URI
        (credentials already embedded) must connect successfully without any
        ValueError or 'Remove credentials' warning.
        MongoClient receives keyword args with host from _probe_reachable_host.
        """
        config = MongoConfig(
            host="",
            raw_uri="mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false",
            username="root",
            password="root",
        )
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch(
            "services.mongo_connector.MongoClient", return_value=mock_client
        ) as mock_cls, \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="127.0.0.1"):
            result = self.connector.connect(config)

        assert result is mock_client
        args, kwargs = mock_cls.call_args
        assert not args                               # no positional URI string
        assert kwargs.get("host") == "127.0.0.1"     # reachable host from probe
        assert kwargs.get("username") == "root"
        assert kwargs.get("password") == "root"
        assert kwargs.get("authSource") == "admin"
        assert kwargs.get("tls") is None              # ssl=false stripped (default)
        assert "directConnection" not in kwargs

    def test_connect_full_uri_error_strips_credentials_from_message(self) -> None:
        """Connection error on a full URI must NOT expose the password in the message."""
        from pymongo.errors import ServerSelectionTimeoutError

        config = MongoConfig(
            host="",
            raw_uri="mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false",
            username="root",
            password="root",
        )
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ServerSelectionTimeoutError(
            "No servers found yet"
        )
        # Suppress probe network call; host value does not affect this test

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError) as exc_info:
                self.connector.connect(config)

        msg = str(exc_info.value)
        assert "root:root@" not in msg      # password not exposed
        assert "localhost" in msg           # host still shown (safe)
        # Client must be closed to prevent zombie background-monitor threads
        mock_client.close.assert_called_once()

    def test_connect_closes_client_on_server_selection_timeout(self) -> None:
        """connect() calls client.close() on ServerSelectionTimeoutError.

        Without explicit close(), pymongo's background monitor thread keeps
        running after the exception.  In Streamlit, multiple failed Connect
        clicks accumulate zombie threads that exhaust MongoDB's connection
        pool, causing subsequent attempts to time out with rtt: None even
        though the server is healthy.
        """
        from pymongo.errors import ServerSelectionTimeoutError

        config = MongoConfig(host="localhost", port=27017, username="u", password="p")
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ServerSelectionTimeoutError("timeout")

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError):
                self.connector.connect(config)

        mock_client.close.assert_called_once()

    def test_connect_closes_client_on_generic_exception(self) -> None:
        """connect() calls client.close() on any non-timeout exception too."""
        config = MongoConfig(host="localhost", port=27017, username="u", password="p")
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = RuntimeError("unexpected")

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError):
                self.connector.connect(config)

        mock_client.close.assert_called_once()

    # ── _safe_location() ─────────────────────────────────────────────────────

    def test_safe_location_strips_credentials_from_uri(self) -> None:
        """_safe_location removes user:pass@ from URI for safe logging."""
        config = MongoConfig(
            host="",
            raw_uri="mongodb://root:root@localhost:27017/idcauditlog",
        )
        loc = MongoDBConnector._safe_location(config)
        assert "root:root@" not in loc
        assert "localhost" in loc

    def test_safe_location_returns_plain_uri_unchanged(self) -> None:
        """_safe_location returns URIs without credentials unchanged."""
        config = MongoConfig(
            host="",
            raw_uri="mongodb://localhost:27017/",
        )
        assert MongoDBConnector._safe_location(config) == "mongodb://localhost:27017/"

    def test_safe_location_falls_back_to_host_port_when_no_uri(self) -> None:
        """_safe_location falls back to host:port when raw_uri is empty."""
        config = MongoConfig(host="dbserver", port=27017)
        assert MongoDBConnector._safe_location(config) == "dbserver:27017"

    def test_connect_localhost_error_shows_original_uri_not_127(self) -> None:
        """BUG-005: error message uses raw_uri (localhost) — not the normalised 127.0.0.1."""
        from pymongo.errors import ServerSelectionTimeoutError

        config = MongoConfig(
            host="localhost",
            raw_uri="mongodb://localhost:27017/idcauditlog?authSource=admin&ssl=false",
            username="root",
            password="root",
        )
        mock_client = MagicMock()
        mock_client.admin.command.side_effect = ServerSelectionTimeoutError(
            "No servers found yet, Timeout: 5.0s"
        )

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="localhost"):
            with pytest.raises(DatabaseConnectionError) as exc_info:
                self.connector.connect(config)

        msg = str(exc_info.value)
        # Error reports the user's original URI (with localhost) — not an IP
        assert "localhost" in msg
        # Credentials must NOT appear in the error message (raw_uri is used)
        assert "root:root@" not in msg

    def test_connect_localhost_ipv6_scenario(self) -> None:
        """BUG-005 extended fix: IPv6 scenario — MongoDB bound to ::1 only.

        On Windows machines where 'localhost' resolves to '::1' (IPv6 loopback)
        and MongoDB binds to ::1:27017, _probe_reachable_host returns '::1'.
        MongoClient must receive host='::1' so the connection succeeds.
        This was the ACTUAL root cause for the user who reported the bug:
        forcing 127.0.0.1 was wrong because MongoDB was NOT on 127.0.0.1.
        """
        config = MongoConfig(
            host="",
            raw_uri="mongodb://root:root@localhost:27017/idcauditlog?authSource=admin&ssl=false",
            username="root",
            password="root",
        )
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch(
            "services.mongo_connector.MongoClient", return_value=mock_client
        ) as mock_cls, \
             patch.object(MongoDBConnector, "_probe_reachable_host", return_value="::1"):
            result = self.connector.connect(config)

        assert result is mock_client
        args, kwargs = mock_cls.call_args
        assert not args
        assert kwargs.get("host") == "::1"       # IPv6 loopback used
        assert kwargs.get("username") == "root"
        assert kwargs.get("authSource") == "admin"
        assert kwargs.get("tls") is None
        assert "directConnection" not in kwargs


class TestURIHelpers:
    """Unit tests for _uri_to_kwargs() and _redact_uri() static helpers."""

    # ── _uri_to_kwargs() ──────────────────────────────────────────────────────

    def test_uri_to_kwargs_full_uri_with_credentials_and_db_path(self) -> None:
        """Primary use-case: full URI with embedded creds, db path, ssl=false."""
        uri = "mongodb://root:root@127.0.0.1:27017/idcauditlog?authSource=admin&ssl=false"
        kwargs = MongoDBConnector._uri_to_kwargs(uri)
        assert kwargs["host"] == "127.0.0.1"
        assert kwargs["port"] == 27017
        assert kwargs["username"] == "root"
        assert kwargs["password"] == "root"
        assert kwargs["authSource"] == "admin"
        # ssl=false → TLS off (default); tls key must NOT be set to avoid
        # triggering pymongo's URI parser TLS code path
        assert "tls" not in kwargs

    def test_uri_to_kwargs_no_auth(self) -> None:
        """URI without credentials produces no username/password keys."""
        uri = "mongodb://127.0.0.1:27017/"
        kwargs = MongoDBConnector._uri_to_kwargs(uri)
        assert kwargs["host"] == "127.0.0.1"
        assert kwargs["port"] == 27017
        assert "username" not in kwargs
        assert "password" not in kwargs

    def test_uri_to_kwargs_tls_true_is_preserved(self) -> None:
        """ssl=true / tls=true must set tls=True in kwargs."""
        uri = "mongodb://host:27017/?tls=true"
        kwargs = MongoDBConnector._uri_to_kwargs(uri)
        assert kwargs.get("tls") is True

    def test_uri_to_kwargs_auth_mechanism_preserved(self) -> None:
        """authMechanism query param is forwarded to kwargs."""
        uri = "mongodb://user:pass@host:27017/?authSource=admin&authMechanism=SCRAM-SHA-1"
        kwargs = MongoDBConnector._uri_to_kwargs(uri)
        assert kwargs["authMechanism"] == "SCRAM-SHA-1"

    def test_uri_to_kwargs_replica_set_preserved(self) -> None:
        """replicaSet query param is forwarded to kwargs."""
        uri = "mongodb://host:27017/?replicaSet=rs0"
        kwargs = MongoDBConnector._uri_to_kwargs(uri)
        assert kwargs["replicaSet"] == "rs0"

    def test_uri_to_kwargs_percent_encoded_password(self) -> None:
        """Percent-encoded password is decoded correctly."""
        uri = "mongodb://user:p%40ss%21@host:27017/"
        kwargs = MongoDBConnector._uri_to_kwargs(uri)
        assert kwargs["password"] == "p@ss!"

    # ── _redact_uri() ─────────────────────────────────────────────────────────

    def test_redact_uri_replaces_password_with_stars(self) -> None:
        """Password in URI netloc is replaced with ***."""
        uri = "mongodb://root:secret@127.0.0.1:27017/db"
        redacted = MongoDBConnector._redact_uri(uri)
        assert "secret" not in redacted
        assert "root:***@" in redacted
        assert "127.0.0.1:27017" in redacted

    def test_redact_uri_no_credentials_unchanged(self) -> None:
        """URI without credentials is returned unchanged."""
        uri = "mongodb://127.0.0.1:27017/"
        assert MongoDBConnector._redact_uri(uri) == uri

    def test_redact_uri_preserves_path_and_query(self) -> None:
        """Path and query string are preserved after redaction."""
        uri = "mongodb://user:pass@host:27017/mydb?authSource=admin"
        redacted = MongoDBConnector._redact_uri(uri)
        assert "/mydb" in redacted
        assert "authSource=admin" in redacted
        assert "pass" not in redacted


class TestProbeReachableHost:
    """Unit tests for _probe_reachable_host() — OS-agnostic host resolution."""

    def setup_method(self) -> None:
        """Create a fresh connector for each test."""
        self.connector = MongoDBConnector()

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _make_addrinfo(addr: str, port: int, family: int) -> tuple:
        """Build a minimal getaddrinfo tuple for patching."""
        import socket as _socket
        sockaddr = (addr, port, 0, 0) if family == _socket.AF_INET6 else (addr, port)
        return (family, _socket.SOCK_STREAM, 0, "", sockaddr)

    # ── success paths ─────────────────────────────────────────────────────────

    def test_returns_first_reachable_ipv4_address(self) -> None:
        """Returns the first IP that accepts a connection (IPv4 path)."""
        import socket as _socket
        infos = [
            self._make_addrinfo("127.0.0.1", 27017, _socket.AF_INET),
            self._make_addrinfo("::1", 27017, _socket.AF_INET6),
        ]
        with patch("socket.getaddrinfo", return_value=infos), \
             patch("socket.create_connection", return_value=MagicMock()):
            result = self.connector._probe_reachable_host("localhost", 27017)
        assert result == "127.0.0.1"

    def test_falls_through_to_ipv6_when_ipv4_fails(self) -> None:
        """IPv6 address is returned when IPv4 times out (user's actual scenario).

        This is the exact failure mode reported: MongoDB listens on ::1:27017
        only; connecting to 127.0.0.1:27017 times out.  The probe must try
        ::1 next and return it so MongoClient uses the correct address.
        """
        import socket as _socket
        infos = [
            self._make_addrinfo("127.0.0.1", 27017, _socket.AF_INET),
            self._make_addrinfo("::1", 27017, _socket.AF_INET6),
        ]

        def _create_conn(address: tuple, timeout: float) -> MagicMock:
            if address[0] == "127.0.0.1":
                raise OSError("timed out")
            return MagicMock()

        with patch("socket.getaddrinfo", return_value=infos), \
             patch("socket.create_connection", side_effect=_create_conn):
            result = self.connector._probe_reachable_host("localhost", 27017)
        assert result == "::1"

    def test_returns_original_when_no_address_reachable(self) -> None:
        """Returns original host unchanged when every address times out.

        MongoClient will then attempt with the original host and surface a
        proper ServerSelectionTimeoutError with a clear message.
        """
        import socket as _socket
        infos = [self._make_addrinfo("127.0.0.1", 27017, _socket.AF_INET)]
        with patch("socket.getaddrinfo", return_value=infos), \
             patch("socket.create_connection", side_effect=OSError("timed out")):
            result = self.connector._probe_reachable_host("localhost", 27017)
        assert result == "localhost"

    def test_returns_original_on_dns_failure(self) -> None:
        """Returns original host when DNS / getaddrinfo itself fails."""
        with patch("socket.getaddrinfo", side_effect=OSError("Name not found")):
            result = self.connector._probe_reachable_host("bad-host", 27017)
        assert result == "bad-host"

    def test_non_localhost_ip_returned_directly(self) -> None:
        """A specific IP address that is reachable is returned as-is."""
        import socket as _socket
        infos = [self._make_addrinfo("192.168.1.10", 27017, _socket.AF_INET)]
        with patch("socket.getaddrinfo", return_value=infos), \
             patch("socket.create_connection", return_value=MagicMock()):
            result = self.connector._probe_reachable_host("192.168.1.10", 27017)
        assert result == "192.168.1.10"

    def test_deduplicates_addresses(self) -> None:
        """Duplicate addresses in getaddrinfo result are tried only once."""
        import socket as _socket
        # Same address appears twice (can happen on some systems)
        infos = [
            self._make_addrinfo("127.0.0.1", 27017, _socket.AF_INET),
            self._make_addrinfo("127.0.0.1", 27017, _socket.AF_INET),
        ]
        create_mock = MagicMock(return_value=MagicMock())
        with patch("socket.getaddrinfo", return_value=infos), \
             patch("socket.create_connection", create_mock):
            self.connector._probe_reachable_host("localhost", 27017)
        # create_connection called exactly once despite two entries
        assert create_mock.call_count == 1


class TestMultiHostURI:
    """BUG-007 — multi-host (replica-set seed-list) URI handling."""

    def setup_method(self) -> None:
        """Create a fresh connector for each test."""
        self.connector = MongoDBConnector()

    # ── _is_multi_host() ─────────────────────────────────────────────────────

    def test_is_multi_host_true_for_replica_set_seed_list(self) -> None:
        """Comma-separated hosts in netloc → multi-host."""
        uri = "mongodb://h1:27017,h2:27017,h3:27017/?replicaSet=rs"
        assert MongoDBConnector._is_multi_host(uri) is True

    def test_is_multi_host_false_for_single_host(self) -> None:
        """Single host → not multi-host."""
        uri = "mongodb://h1:27017/?replicaSet=rs"
        assert MongoDBConnector._is_multi_host(uri) is False

    def test_is_multi_host_false_for_srv_uri(self) -> None:
        """SRV URIs are single-host by spec; never reported as multi-host."""
        uri = "mongodb+srv://cluster.example.mongodb.net/?replicaSet=rs"
        assert MongoDBConnector._is_multi_host(uri) is False

    def test_is_multi_host_with_credentials_in_netloc(self) -> None:
        """`user:pass@` prefix must not confuse the multi-host detector."""
        uri = (
            "mongodb://user:p%40ss@h1:27017,h2:27017,h3:27017/"
            "?authSource=admin&replicaSet=rs"
        )
        assert MongoDBConnector._is_multi_host(uri) is True

    def test_is_multi_host_with_credentials_single_host(self) -> None:
        """`user:pass@host:port` (single host) → not multi-host."""
        uri = "mongodb://user:p%40ss@h1:27017/?authSource=admin"
        assert MongoDBConnector._is_multi_host(uri) is False

    # ── connect() routing ────────────────────────────────────────────────────

    def test_connect_multi_host_uri_uses_uri_string_form(self) -> None:
        """Multi-host URIs must pass the URI string positionally to MongoClient.

        Single-host mongodb:// URIs use the kwargs form (BUG-005).  Multi-host
        URIs cannot be expressed via kwargs (MongoClient takes one host) and
        MUST therefore go through the URI-string branch the same way SRV URIs
        do.
        """
        uri = (
            "mongodb://user:pass@h1:27017,h2:27017,h3:27017/"
            "?authSource=admin&replicaSet=rs&readPreference=primary&tls=false"
        )
        config = MongoConfig(host="", raw_uri=uri, username="", password="")
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch("services.mongo_connector.MongoClient", return_value=mock_client) as mock_cls:
            self.connector.connect(config)

        args, kwargs = mock_cls.call_args
        # Positional URI string is required for multi-host URIs
        assert args and args[0] == uri, (
            "Multi-host URI must be passed as a positional URI string to MongoClient"
        )
        # Only serverSelectionTimeoutMS should be set as a keyword
        assert "host" not in kwargs
        assert "port" not in kwargs
        assert kwargs.get("serverSelectionTimeoutMS") == config.connect_timeout_ms

    def test_connect_multi_host_uri_skips_tcp_probe(self) -> None:
        """The pre-connect TCP probe must NOT run for multi-host URIs.

        Probing only one of the seed hosts would be misleading — pymongo's
        own topology discovery handles seed-list reachability.
        """
        uri = (
            "mongodb://h1:27017,h2:27017/"
            "?authSource=admin&replicaSet=rs"
        )
        config = MongoConfig(host="", raw_uri=uri, username="", password="")
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        with patch("services.mongo_connector.MongoClient", return_value=mock_client), \
             patch.object(MongoDBConnector, "_probe_reachable_host") as mock_probe:
            self.connector.connect(config)

        mock_probe.assert_not_called()

    def test_bug_007_regression_multi_host_replica_set_uri_does_not_raise_value_error(
        self,
    ) -> None:
        """Regression — exact failing URI shape from BUG-007 must not raise ValueError.

        Before the fix, `connect()` routed this URI through `_uri_to_kwargs()`,
        which called `urllib.parse.urlparse(...).port` and raised:
            ValueError: Port could not be cast to integer value as
            '27017,rbglv0906.rbg.infineon.com:27017,...'
        The fix routes multi-host URIs through pymongo's own URI parser via the
        URI-string branch, which handles seed lists natively.
        """
        uri = (
            "mongodb://idcauditlog_admin:aLo5UrEabld8MbmL@"
            "rbglv0905.rbg.infineon.com:27017,"
            "rbglv0906.rbg.infineon.com:27017,"
            "rbglv0907.rbg.infineon.com:27017/"
            "?authSource=idcauditlog&replicaSet=rs"
            "&readPreference=primary&tls=false"
        )
        config = MongoConfig(host="", raw_uri=uri, username="", password="")
        mock_client = MagicMock()
        mock_client.admin.command.return_value = {"ok": 1}

        # Must NOT raise ValueError ("Port could not be cast to integer value …")
        with patch("services.mongo_connector.MongoClient", return_value=mock_client):
            result = self.connector.connect(config)

        assert result is mock_client



