"""Tests for TCP and UDP protocol stream simulation (Member 3)."""

import pytest

from protocols.tcp_udp import simulate_tcp_stream, simulate_udp_stream


@pytest.mark.skip(reason="Member 3 to implement simulate_tcp_stream")
def test_tcp_stream_simulation() -> None:
    res = simulate_tcp_stream(payload_size_kb=10, rtt_ms=40.0, packet_loss_rate=0.05)
    assert res["protocol"] == "TCP"
    assert res["handshake_latency_ms"] > 0
    assert res["retransmissions"] >= 0
    assert res["data_delivered_bytes"] == 10 * 1024


@pytest.mark.skip(reason="Member 3 to implement simulate_udp_stream")
def test_udp_stream_simulation() -> None:
    res = simulate_udp_stream(payload_size_kb=10, rtt_ms=40.0, packet_loss_rate=0.05)
    assert res["protocol"] == "UDP"
    assert res["datagrams_sent"] == 10
    assert res["datagrams_dropped"] >= 0
