"""Shared networking helpers used by relational and document DB connectors.

Extracted from `mongo_connector.py` in Sprint 11 (US-050) so that
`db_connector.py` (and any future engine connectors) can apply the same
WSL2 fail-fast protection that fixed BUG-006.

Public API:
    - ``LOOPBACK_HOSTS`` — frozenset of host names that resolve to the local
      loopback interface.
    - ``is_wsl2()`` — best-effort WSL2 detection.
    - ``probe_reachable_host(host, port, timeout_s=1.0)`` — return the first
      reachable IP for ``host`` (or ``host`` unchanged when none accept a
      TCP handshake within ``timeout_s``).
"""

from __future__ import annotations

import functools
import pathlib
import socket

from utils.logger import get_logger

logger = get_logger(__name__)


LOOPBACK_HOSTS: frozenset[str] = frozenset(
    {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
)
"""Hosts that map to a local loopback interface."""


@functools.lru_cache(maxsize=1)
def is_wsl2() -> bool:
    """Return ``True`` when the current process is running inside WSL2.

    Detection reads ``/proc/version`` and looks for the ``microsoft`` marker
    that the WSL kernel includes in its version string. The check is fully
    best-effort: any I/O failure (Windows, container without ``/proc``)
    returns ``False``.

    The result is cached for the lifetime of the process — the WSL kernel
    string does not change at runtime.
    """
    try:
        return "microsoft" in pathlib.Path("/proc/version").read_text().lower()
    except OSError:
        return False


def probe_reachable_host(host: str, port: int, timeout_s: float = 1.0) -> str:
    """Return the first IP address for ``host`` that accepts a TCP connection.

    Resolves all addresses for the hostname using :func:`socket.getaddrinfo`
    and returns the first address that successfully completes a TCP
    handshake. Falls back to ``host`` unchanged when all addresses fail or
    when DNS resolution fails, allowing the caller to surface a meaningful
    error.

    This handles the Windows ``localhost`` ambiguity where ``localhost`` can
    resolve to either ``127.0.0.1`` (IPv4) or ``::1`` (IPv6) depending on
    the OS hosts file while the target service may be bound to only one of
    them.
    """
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        logger.warning(
            "TCP probe: DNS resolution of %s failed — %s", host, exc
        )
        return host

    tried: list[str] = []
    for _family, _type, _proto, _canon, sockaddr in infos:
        addr = sockaddr[0]
        if addr in tried:
            continue
        tried.append(addr)
        try:
            with socket.create_connection((addr, port), timeout=timeout_s) as _s:
                pass
            if addr != host:
                logger.info("TCP probe: %s → %s:%d ✓", host, addr, port)
            else:
                logger.info("TCP probe: %s:%d ✓", addr, port)
            return addr
        except OSError as _exc:
            logger.debug("TCP probe: %s:%d — %s", addr, port, _exc)

    logger.warning(
        "TCP probe: all addresses for %s:%d unreachable (tried: %s)",
        host,
        port,
        tried,
    )
    return host
