"""Extended unit tests for utils/network.py — US-068.

Covers previously uncovered line:
- Line 77: `continue` in the duplicate-address deduplication guard of probe_reachable_host()
"""
from __future__ import annotations

import socket
from unittest.mock import patch

from utils.network import probe_reachable_host


class _StubSocket:
    """Context-manager stub that simulates a successful TCP connection."""

    def __enter__(self) -> _StubSocket:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


class TestProbeReachableHostDeduplication:
    """Cover line 77: duplicate-address skip in probe_reachable_host."""

    def test_duplicate_address_is_tried_only_once(self) -> None:
        """Line 77: when getaddrinfo returns the same addr twice, only the first attempt runs.

        The `continue` guard (line 77) prevents re-trying an address that is
        already in the `tried` list. We verify this by counting the number of
        create_connection calls — it must be 1 (first attempt fails), not 2.
        """
        # Two entries with the SAME IP address — the second should be skipped
        infos = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 27017)),
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 27017)),  # duplicate
        ]
        with patch("utils.network.socket.getaddrinfo", return_value=infos):
            with patch(
                "utils.network.socket.create_connection",
                side_effect=OSError("connection refused"),
            ) as mock_connect:
                result = probe_reachable_host("localhost", 27017)

        # Only ONE connect attempt, not two — the duplicate was skipped (line 77 `continue`)
        assert mock_connect.call_count == 1
        # No address was reachable, so original host is returned
        assert result == "localhost"

    def test_duplicate_address_skipped_after_successful_first(self) -> None:
        """Line 77: duplicate entry after a successful connection is not attempted."""
        infos = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("192.168.1.1", 3306)),
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("192.168.1.1", 3306)),  # duplicate
        ]
        with patch("utils.network.socket.getaddrinfo", return_value=infos):
            with patch(
                "utils.network.socket.create_connection",
                return_value=_StubSocket(),
            ) as mock_connect:
                result = probe_reachable_host("mydb", 3306)

        # Connection succeeds on first attempt; duplicate is never tried
        assert mock_connect.call_count == 1
        assert result == "192.168.1.1"

    def test_three_entries_two_duplicates_only_two_attempts(self) -> None:
        """Line 77: three entries where two are duplicates — only two distinct addresses tried."""
        infos = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.1", 5432)),
            (socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("::1", 5432, 0, 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.1", 5432)),  # duplicate of first
        ]
        with patch("utils.network.socket.getaddrinfo", return_value=infos):
            with patch(
                "utils.network.socket.create_connection",
                side_effect=[OSError, _StubSocket()],
            ) as mock_connect:
                result = probe_reachable_host("pghost", 5432)

        # Exactly 2 attempts: "10.0.0.1" (fails), "::1" (succeeds); third skipped
        assert mock_connect.call_count == 2
        assert result == "::1"
