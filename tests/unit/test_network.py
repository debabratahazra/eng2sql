"""Unit tests for ``src/utils/network.py`` (US-050)."""

from __future__ import annotations

import socket
from unittest.mock import patch

import pytest

from utils.network import LOOPBACK_HOSTS, is_wsl2, probe_reachable_host


class TestLoopbackHosts:
    """Exercise the ``LOOPBACK_HOSTS`` constant."""

    def test_contains_expected_hosts(self) -> None:
        assert "localhost" in LOOPBACK_HOSTS
        assert "127.0.0.1" in LOOPBACK_HOSTS
        assert "::1" in LOOPBACK_HOSTS
        assert "0.0.0.0" in LOOPBACK_HOSTS

    def test_is_frozen(self) -> None:
        assert isinstance(LOOPBACK_HOSTS, frozenset)


class TestIsWsl2:
    """Exercise ``is_wsl2`` cached behaviour."""

    def setup_method(self) -> None:
        is_wsl2.cache_clear()

    def teardown_method(self) -> None:
        is_wsl2.cache_clear()

    def test_returns_true_when_proc_version_contains_microsoft(self) -> None:
        with patch(
            "utils.network.pathlib.Path.read_text",
            return_value="Linux 5.15 microsoft-standard-WSL2",
        ):
            assert is_wsl2() is True

    def test_returns_false_when_proc_version_missing(self) -> None:
        with patch("utils.network.pathlib.Path.read_text", side_effect=OSError):
            assert is_wsl2() is False

    def test_result_is_cached(self) -> None:
        with patch(
            "utils.network.pathlib.Path.read_text",
            return_value="microsoft",
        ) as mock_read:
            is_wsl2()
            is_wsl2()
            is_wsl2()
            assert mock_read.call_count == 1


class TestProbeReachableHost:
    """Exercise ``probe_reachable_host``."""

    def test_returns_first_reachable_address(self) -> None:
        # Two addresses; second one connects successfully.
        infos = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 9999)),
            (socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("::1", 9999, 0, 0)),
        ]
        with patch("utils.network.socket.getaddrinfo", return_value=infos):
            with patch(
                "utils.network.socket.create_connection",
                side_effect=[OSError, _StubSocket()],
            ):
                result = probe_reachable_host("localhost", 9999)
        assert result == "::1"

    def test_returns_host_when_dns_fails(self) -> None:
        with patch("utils.network.socket.getaddrinfo", side_effect=OSError):
            assert probe_reachable_host("nonexistent.host.invalid", 1234) == (
                "nonexistent.host.invalid"
            )

    def test_returns_host_when_no_address_reachable(self) -> None:
        infos = [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 65000)),
        ]
        with patch("utils.network.socket.getaddrinfo", return_value=infos):
            with patch(
                "utils.network.socket.create_connection", side_effect=OSError
            ):
                result = probe_reachable_host("localhost", 65000)
        assert result == "localhost"


class _StubSocket:
    """Context-manager stub for a successful ``create_connection`` call."""

    def __enter__(self) -> _StubSocket:
        return self

    def __exit__(self, *_args: object) -> None:
        return None


@pytest.mark.parametrize("host", ["localhost", "127.0.0.1", "::1", "0.0.0.0"])
def test_loopback_hosts_membership(host: str) -> None:
    assert host in LOOPBACK_HOSTS
