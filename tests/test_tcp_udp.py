"""Tests for TCP and UDP protocol stream simulation (Member 3)."""

from __future__ import annotations

import pytest

from protocols.tcp_udp import (
    simulate_tcp,
    simulate_tcp_stream,
    simulate_udp,
    simulate_udp_stream,
)


def test_tcp_stream_simulation() -> None:
    res = simulate_tcp_stream(payload_size_kb=10, rtt_ms=40.0, packet_loss_rate=0.05)
    assert res["protocol"] == "TCP"
    assert res["handshake_latency_ms"] > 0
    assert res["retransmissions"] >= 0
    assert res["data_delivered_bytes"] == 10 * 1024
    assert len(res["timeline"]) > 0


def test_udp_stream_simulation() -> None:
    res = simulate_udp_stream(payload_size_kb=10, rtt_ms=40.0, packet_loss_rate=0.05)
    assert res["protocol"] == "UDP"
    assert res["datagrams_sent"] == 10
    assert res["datagrams_dropped"] >= 0
    assert res["datagrams_received"] + res["datagrams_dropped"] == 10


def test_determinism_with_same_seed() -> None:
    """Simulations with identical seed must produce identical results."""
    tcp_run1 = simulate_tcp(num_packets=15, loss_probability=0.20, seed=1234)
    tcp_run2 = simulate_tcp(num_packets=15, loss_probability=0.20, seed=1234)
    assert tcp_run1["delivered"] == tcp_run2["delivered"]
    assert tcp_run1["retransmitted"] == tcp_run2["retransmitted"]
    assert tcp_run1["total_time_ms"] == tcp_run2["total_time_ms"]

    udp_run1 = simulate_udp(num_packets=20, loss_probability=0.15, seed=5678)
    udp_run2 = simulate_udp(num_packets=20, loss_probability=0.15, seed=5678)
    assert udp_run1["delivered"] == udp_run2["delivered"]
    assert udp_run1["lost"] == udp_run2["lost"]


def test_zero_loss_delivers_all_without_retransmission() -> None:
    """Under 0% loss, all packets must be delivered with 0 retransmissions."""
    tcp_res = simulate_tcp(num_packets=12, loss_probability=0.0, seed=42)
    assert tcp_res["delivered"] == 12
    assert tcp_res["retransmitted"] == 0
    assert tcp_res["failed"] == 0

    udp_res = simulate_udp(num_packets=12, loss_probability=0.0, seed=42)
    assert udp_res["delivered"] == 12
    assert udp_res["lost"] == 0
    assert udp_res["delivery_ratio"] == 1.0


def test_one_hundred_percent_loss_with_retry_cap_terminates() -> None:
    """Under 100% loss, TCP must cap retries and terminate without infinite looping."""
    tcp_res = simulate_tcp(num_packets=3, loss_probability=1.0, seed=42, max_retries=3)
    assert tcp_res["delivered"] == 0
    assert tcp_res["failed"] == 3
    assert tcp_res["retransmitted"] == 3 * 3  # 3 attempts per packet
    assert any(e["event_type"] == "FAIL" for e in tcp_res["events"])

    udp_res = simulate_udp(num_packets=10, loss_probability=1.0, seed=42)
    assert udp_res["delivered"] == 0
    assert udp_res["lost"] == 10
    assert udp_res["delivery_ratio"] == 0.0


def test_udp_never_retransmits() -> None:
    """UDP is fire-and-forget; total events must equal num_packets without retries."""
    udp_res = simulate_udp(num_packets=25, loss_probability=0.30, seed=42)
    assert udp_res["sent"] == 25
    assert len(udp_res["events"]) == 25
    # Every event must be either DELIVERED or LOST
    assert all(e["event_type"] in ("DELIVERED", "LOST") for e in udp_res["events"])


def test_event_ordering_handshake_first_then_teardown() -> None:
    """TCP must begin with 3-way handshake (SYN, SYN-ACK, ACK) and end with FIN teardown."""
    tcp_res = simulate_tcp(num_packets=5, loss_probability=0.0, seed=42)
    event_types = [e["event_type"] for e in tcp_res["events"]]

    # First three events must be handshake
    assert event_types[0] == "SYN"
    assert event_types[1] == "SYN-ACK"
    assert event_types[2] == "ACK"

    # Last three events must be teardown
    assert event_types[-3] == "FIN"
    assert event_types[-2] == "FIN-ACK"
    assert event_types[-1] == "ACK"


def test_invalid_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        simulate_tcp(num_packets=-1)

    with pytest.raises(ValueError, match="within"):
        simulate_tcp(num_packets=5, loss_probability=1.5)

    with pytest.raises(ValueError, match="cannot be negative"):
        simulate_udp(num_packets=-5)

    with pytest.raises(ValueError, match="within"):
        simulate_udp(num_packets=5, loss_probability=-0.1)
