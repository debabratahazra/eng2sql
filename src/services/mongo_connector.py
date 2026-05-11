"""MongoDB connector service for Eng2SQL.

Manages pymongo client creation, database listing, and database object retrieval.
"""
from __future__ import annotations

import urllib.parse

try:
    from pymongo import MongoClient  # type: ignore[import-untyped]
    from pymongo.database import Database  # type: ignore[import-untyped]
    from pymongo.errors import ServerSelectionTimeoutError  # type: ignore[import-untyped]
    _PYMONGO_AVAILABLE = True
except ImportError:
    _PYMONGO_AVAILABLE = False

from models.config import MongoConfig
from utils.exceptions import DatabaseConnectionError
from utils.logger import get_logger
from utils.network import LOOPBACK_HOSTS, is_wsl2, probe_reachable_host

logger = get_logger(__name__)

_SYSTEM_DATABASES: frozenset[str] = frozenset({"admin", "local", "config"})


class MongoDBConnector:
    """Creates and manages pymongo MongoDB connections."""

    @staticmethod
    def _redact_uri(uri: str) -> str:
        """Return the URI with the password replaced by ``***`` for safe logging.

        Args:
            uri: Any ``mongodb://`` or ``mongodb+srv://`` URI string.

        Returns:
            The URI with ``:<password>@`` replaced by ``:***@``.
        """
        parsed = urllib.parse.urlparse(uri)
        if "@" in (parsed.netloc or ""):
            userinfo, hostinfo = parsed.netloc.rsplit("@", 1)
            safe_userinfo = userinfo.split(":", 1)[0] + ":***" if ":" in userinfo else userinfo
            return urllib.parse.urlunparse(parsed._replace(netloc=f"{safe_userinfo}@{hostinfo}"))
        return uri

    # Hosts that map to a local loopback interface — used by the WSL2
    # fail-fast check below. Re-exported here as a class attribute for
    # backward compatibility with existing tests; the source of truth lives
    # in ``utils.network.LOOPBACK_HOSTS``.
    _LOOPBACK_HOSTS: frozenset[str] = LOOPBACK_HOSTS

    @staticmethod
    def _is_wsl2() -> bool:
        """Backwards-compatible wrapper around :func:`utils.network.is_wsl2`."""
        return is_wsl2()

    @staticmethod
    def _normalise_localhost(uri: str) -> str:
        """Replace ``localhost`` with ``127.0.0.1`` in the URI host component.

        On Windows ``localhost`` can resolve to the IPv6 loopback address
        ``::1`` while MongoDB typically binds only to the IPv4 loopback
        ``127.0.0.1``.  Normalising before the ``MongoClient`` call ensures
        that IPv4 is always used, avoiding topology-selection timeouts
        (BUG-005).

        Args:
            uri: A ``mongodb://`` or ``mongodb+srv://`` connection string.

        Returns:
            The same URI with ``localhost`` replaced by ``127.0.0.1`` in the
            host field.  URIs that do not contain ``localhost`` are returned
            unchanged.
        """
        parsed = urllib.parse.urlparse(uri)
        if (parsed.hostname or "").lower() != "localhost":
            return uri
        port = parsed.port
        old_host = f"localhost:{port}" if port else "localhost"
        new_host = f"127.0.0.1:{port}" if port else "127.0.0.1"
        new_netloc = parsed.netloc.replace(old_host, new_host, 1)
        return urllib.parse.urlunparse(parsed._replace(netloc=new_netloc))

    def _probe_reachable_host(self, host: str, port: int, timeout_s: float = 1.0) -> str:
        """Backwards-compatible wrapper around :func:`utils.network.probe_reachable_host`."""
        return probe_reachable_host(host, port, timeout_s)

    @staticmethod
    def _is_multi_host(uri: str) -> bool:
        """Return ``True`` when ``uri`` lists more than one host (replica set).

        A standard ``mongodb://`` URI may list multiple seed hosts separated by
        commas, e.g. ``mongodb://h1:27017,h2:27017,h3:27017/?replicaSet=rs``.
        Such URIs cannot be parsed with :func:`urllib.parse.urlparse`'s
        ``.port`` accessor (it raises ``ValueError`` because the comma-joined
        hosts string is treated as a single port value — BUG-007).  This helper
        detects the multi-host case so the caller can route the URI through
        pymongo's own URI parser instead of :meth:`_uri_to_kwargs`.

        Args:
            uri: A ``mongodb://`` or ``mongodb+srv://`` connection string.

        Returns:
            ``True`` if the URI contains more than one comma-separated host in
            its netloc, ``False`` otherwise.  ``mongodb+srv://`` URIs always
            return ``False`` (SRV URIs are single-host by spec).
        """
        if not uri.startswith("mongodb://"):
            return False
        parsed = urllib.parse.urlparse(uri)
        netloc = parsed.netloc or ""
        # Strip ``user:pass@`` prefix if present so we only inspect the hosts.
        hosts_part = netloc.rsplit("@", 1)[-1]
        return "," in hosts_part

    @staticmethod
    def _uri_to_kwargs(uri: str) -> dict:
        """Parse a ``mongodb://`` URI into ``MongoClient`` keyword arguments.

        Using keyword arguments is significantly more reliable than passing a
        URI string in environments such as Streamlit where pymongo's URI
        parser can interact poorly with ``ssl=false`` / ``tls=false`` query
        parameters.  Keyword arguments bypass the URI parser entirely.

        Only ``mongodb://`` (single-host) URIs are supported here.
        ``mongodb+srv://`` URIs must use the URI string form.

        Args:
            uri: A ``mongodb://`` connection string.

        Returns:
            Dict of keyword arguments suitable for ``MongoClient(**kwargs)``.
        """
        parsed = urllib.parse.urlparse(uri)
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=False)

        kwargs: dict = {}

        # Host and port — extracted from the URI as-is; caller may override
        # host with the result of _probe_reachable_host() before passing to
        # MongoClient so that the correct loopback address is used.
        if parsed.hostname:
            kwargs["host"] = parsed.hostname
        if parsed.port:
            kwargs["port"] = parsed.port

        # Credentials — percent-decode any special characters
        if parsed.username:
            kwargs["username"] = urllib.parse.unquote_plus(parsed.username)
        if parsed.password:
            kwargs["password"] = urllib.parse.unquote_plus(parsed.password)

        # Auth source
        if "authSource" in params:
            kwargs["authSource"] = params["authSource"][0]

        # Auth mechanism
        if "authMechanism" in params:
            kwargs["authMechanism"] = params["authMechanism"][0]

        # TLS / SSL — strip the redundant ssl=false / tls=false by simply not
        # setting tls=True (the default for mongodb:// is already tls=False).
        # Only set tls=True when explicitly requested.
        for tls_key in ("tls", "ssl"):
            if tls_key in params:
                val = params[tls_key][0].lower()
                if val not in ("false", "0", "no"):
                    kwargs["tls"] = True
                break  # only process the first tls/ssl param found

        # Replica set
        if "replicaSet" in params:
            kwargs["replicaSet"] = params["replicaSet"][0]

        return kwargs

    @staticmethod
    def _safe_location(config: MongoConfig) -> str:
        """Return a credential-free location string for error messages and logs.

        When ``config.raw_uri`` contains embedded credentials
        (``user:pass@host``), they are stripped before returning so that
        passwords never appear in log output or exception messages.

        Args:
            config: MongoDB connection configuration.

        Returns:
            A safe, credential-free string identifying the connection target.
        """
        if config.raw_uri:
            parsed = urllib.parse.urlparse(config.raw_uri)
            if parsed.username:
                # Strip user:pass — keep scheme + host:port + path + query
                safe_netloc = parsed.netloc.split("@", 1)[1]
                return urllib.parse.urlunparse(parsed._replace(netloc=safe_netloc))
            return config.raw_uri
        return f"{config.host}:{config.port}"

    def connect(self, config: MongoConfig) -> object:
        """Create a MongoClient and verify connectivity with a ping.

        Connection is established in five logged steps:

        1. Resolve the final URI from ``config``
           (raw_uri with credential injection, or field-assembled URI).
        2. Parse URI to keyword arguments (``mongodb://`` only) and log the
           extracted host.
        3. TCP probe — call :meth:`_probe_reachable_host` which resolves the
           hostname via :func:`socket.getaddrinfo` and returns the first IP
           address (IPv4 or IPv6) that accepts a TCP connection.  This
           correctly handles Windows machines where ``localhost`` resolves to
           ``::1`` (IPv6) rather than ``127.0.0.1`` (IPv4).
        4. Build ``MongoClient`` — ``mongodb://`` URIs are parsed into keyword
           arguments (bypasses pymongo's URI parser, avoids ``ssl=false``
           edge cases in Streamlit's multi-threaded environment).
           ``mongodb+srv://`` URIs use the URI string form.
        5. ``admin.ping`` — validates authentication and server health.

        Args:
            config: MongoDB connection parameters.

        Returns:
            A connected ``pymongo.MongoClient`` instance.

        Raises:
            DatabaseConnectionError: If pymongo is not installed or the
                connection cannot be established.
        """
        if not _PYMONGO_AVAILABLE:
            raise DatabaseConnectionError(
                "pymongo is not installed. Run: pip install pymongo>=4.7"
            )

        logger.info("── MongoDB connect START ──────────────────────────────────")
        logger.info("  mode     : %s", "URI" if config.raw_uri else "fields")
        logger.info(
            "  raw_uri  : %s",
            self._redact_uri(config.raw_uri) if config.raw_uri else "(none)",
        )
        logger.info(
            "  host:port: %s:%d",
            config.host or "(from URI)",
            config.port,
        )
        logger.info("  username : %s", config.username or "(none)")
        logger.info("  timeout  : %d ms", config.connect_timeout_ms)

        client: object | None = None
        try:
            # Step 1 — resolve URI
            resolved_uri = config.connection_uri
            logger.info("  [1/5] resolved URI   : %s", self._redact_uri(resolved_uri))

            # Step 2 — parse URI to kwargs (mongodb://) or keep for SRV
            # Step 3 — TCP probe: find the reachable address for this hostname
            # Step 4 — create MongoClient
            # For standard mongodb:// URIs, parse to keyword arguments.  This
            # bypasses pymongo's URI string parser and avoids the ssl=false
            # edge case that causes the background monitor thread to stall in
            # Streamlit's multi-threaded server environment.
            #
            # Multi-host (replica-set seed-list) URIs cannot be handled by
            # ``_uri_to_kwargs`` because :func:`urllib.parse.urlparse` cannot
            # parse the comma-joined hosts (BUG-007).  Route them through
            # pymongo's own URI parser via the URI string form, the same way
            # ``mongodb+srv://`` URIs are handled.
            if resolved_uri.startswith("mongodb://") and not self._is_multi_host(resolved_uri):
                client_kwargs = self._uri_to_kwargs(resolved_uri)
                client_kwargs["serverSelectionTimeoutMS"] = config.connect_timeout_ms

                _host = client_kwargs.get("host", "localhost")
                _port = client_kwargs.get("port", 27017)
                logger.info("  [2/5] parsed host    : %s:%d", _host, _port)
                logger.info("  [3/5] TCP probe      : resolving %s …", _host)
                client_kwargs["host"] = self._probe_reachable_host(_host, _port)

                # BUG-006 — WSL2 fail-fast: if the TCP probe failed (probe
                # returned the host unchanged) AND the requested host is a
                # loopback address AND we are running inside WSL2, MongoDB on
                # the Windows host is unreachable via WSL2's loopback. Fail
                # immediately with an actionable hint instead of waiting
                # ``serverSelectionTimeoutMS`` for the inevitable
                # ``ServerSelectionTimeoutError``.
                if (
                    client_kwargs["host"] == _host
                    and _host.lower() in self._LOOPBACK_HOSTS
                    and self._is_wsl2()
                ):
                    raise DatabaseConnectionError(
                        f"Could not reach MongoDB at {_host}:{_port} from WSL2. "
                        "WSL2 cannot reach services bound to 'localhost' / "
                        "127.0.0.1 on the Windows host. Use the Windows host "
                        "IP from /etc/resolv.conf (the 'nameserver' line, "
                        "e.g. 172.x.x.1) or 'host.docker.internal' in your "
                        "MongoDB URI instead of 'localhost'. "
                        "See: https://learn.microsoft.com/windows/wsl/networking"
                    )

                log_kwargs = {
                    k: ("***" if k == "password" else v)
                    for k, v in client_kwargs.items()
                }
                logger.info("  [4/5] MongoClient    : kwargs = %s", log_kwargs)
                client = MongoClient(**client_kwargs)  # type: ignore[possibly-undefined]
            else:
                # mongodb+srv:// and multi-host URIs require the URI string form;
                # SRV hostnames are resolved internally by pymongo's DNS SRV
                # lookup so a pre-probe would target the wrong host.
                logger.info("  [2/5] parsed host    : (SRV/multi-host — no pre-probe)")
                logger.info("  [3/5] TCP probe      : skipped (SRV/multi-host)")
                logger.info(
                    "  [4/5] MongoClient    : URI string (%s)",
                    "SRV" if resolved_uri.startswith("mongodb+srv") else "multi-host",
                )
                client = MongoClient(  # type: ignore[possibly-undefined]
                    resolved_uri,
                    serverSelectionTimeoutMS=config.connect_timeout_ms,
                )

            # Step 5 — verify with ping
            logger.info("  [5/5] ping           : issuing admin.ping …")
            client.admin.command("ping")  # type: ignore[union-attr]
            logger.info(
                "  [5/5] ping           : OK ✓ — connected to %s",
                self._safe_location(config),
            )
            logger.info("── MongoDB connect END (SUCCESS) ──────────────────────────")

        except ServerSelectionTimeoutError as exc:  # type: ignore[possibly-undefined]
            logger.error(
                "  FAIL ServerSelectionTimeoutError: %s", exc,
            )
            # Close the client so its background monitor thread does not linger
            # — zombie threads exhaust MongoDB's connection pool and cause
            # subsequent attempts to time out with rtt: None.
            if client is not None:
                try:
                    client.close()  # type: ignore[union-attr]
                except Exception:  # noqa: BLE001
                    pass
            raise DatabaseConnectionError(
                f"Could not connect to MongoDB at {self._safe_location(config)} - {exc}"
            ) from exc
        except Exception as exc:  # noqa: BLE001
            logger.error("  FAIL %s: %s", type(exc).__name__, exc)
            if client is not None:
                try:
                    client.close()  # type: ignore[union-attr]
                except Exception:  # noqa: BLE001
                    pass
            raise DatabaseConnectionError(
                f"Could not connect to MongoDB at {self._safe_location(config)} - {exc}"
            ) from exc

        logger.debug(
            "Connected to MongoDB at %s as %s",
            self._safe_location(config),
            config.username or "(no auth)",
        )
        return client

    def list_databases(self, client: object) -> list[str]:
        """Return all non-system database names available to this client.

        Args:
            client: A connected ``pymongo.MongoClient``.

        Returns:
            Sorted list of database names with system databases excluded.

        Raises:
            DatabaseConnectionError: If the driver call fails.
        """
        try:
            all_dbs: list[str] = client.list_database_names()  # type: ignore[union-attr]
        except Exception as exc:  # noqa: BLE001
            raise DatabaseConnectionError(
                f"Failed to list MongoDB databases: {exc}"
            ) from exc

        filtered = sorted(db for db in all_dbs if db not in _SYSTEM_DATABASES)
        logger.debug("MongoDB databases (filtered): %s", filtered)
        return filtered

    def get_database(self, client: object, name: str) -> object:
        """Return a pymongo Database object for the given database name.

        Args:
            client: A connected ``pymongo.MongoClient``.
            name: Name of the database to retrieve.

        Returns:
            A ``pymongo.database.Database`` object.
        """
        return client[name]  # type: ignore[index]
