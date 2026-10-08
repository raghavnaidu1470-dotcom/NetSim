"""TCP and UDP protocol simulation demonstration (Member 3).

Models transport-layer behaviors: TCP connection establishment (3-way handshake),
sliding window flow control, retransmissions, and UDP fire-and-forget datagrams.
"""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class TCPSimulationSummary(TypedDict):
    """Summary metrics of a simulated TCP transmission."""
    protocol: str
    handshake_latency_ms: float
    total_segments_sent: int
    retransmissions: int
    data_delivered_bytes: int
    effective_throughput_mbps: float
    total_time_ms: float
    timeline: List[str]


class UDPSimulationSummary(TypedDict):
    """Summary metrics of a simulated UDP transmission."""
    protocol: str
    datagrams_sent: int
    datagrams_received: int
    datagrams_dropped: int
    packet_loss_ratio: float
    total_time_ms: float
    timeline: List[str]


def simulate_tcp_stream(
    payload_size_kb: int = 10,
    rtt_ms: float = 40.0,
    packet_loss_rate: float = 0.05,
    window_size_segments: int = 4,
) -> TCPSimulationSummary:
    """Simulate TCP connection setup, windowed data transfer, and retransmission.

    Args:
        payload_size_kb: Total volume of data to transmit in KB.
        rtt_ms: Round-trip time in milliseconds.
        packet_loss_rate: Drop probability per segment.
        window_size_segments: Sliding window size (segments).

    Returns:
        TCPSimulationSummary with timeline and metrics.

    Raises:
        NotImplementedError: If not yet implemented by Member 3.
    """
    # TODO(Member 3 - Step 1): Simulate 3-way handshake (SYN, SYN-ACK, ACK) costing 1.5 RTT.
    # TODO(Member 3 - Step 2): Partition payload into 1 KB MSS segments.
    # TODO(Member 3 - Step 3): Iterate transmission in window bursts; test drops against packet_loss_rate.
    # TODO(Member 3 - Step 4): Add retransmissions for dropped segments.
    # TODO(Member 3 - Step 5): Return populated TCPSimulationSummary.
    raise NotImplementedError("Member 3 to implement simulate_tcp_stream in protocols/tcp_udp.py")


def simulate_udp_stream(
    payload_size_kb: int = 10,
    rtt_ms: float = 40.0,
    packet_loss_rate: float = 0.05,
) -> UDPSimulationSummary:
    """Simulate UDP connectionless datagram burst.

    Args:
        payload_size_kb: Total volume of data to transmit in KB.
        rtt_ms: Round-trip time in milliseconds.
        packet_loss_rate: Drop probability per datagram.

    Returns:
        UDPSimulationSummary with timeline and metrics.

    Raises:
        NotImplementedError: If not yet implemented by Member 3.
    """
    # TODO(Member 3 - Step 1): Partition payload into datagrams (no handshake overhead).
    # TODO(Member 3 - Step 2): Transmit all datagrams with 0.5 RTT one-way propagation.
    # TODO(Member 3 - Step 3): Drop datagrams probabilistically without retransmissions.
    # TODO(Member 3 - Step 4): Return populated UDPSimulationSummary.
    raise NotImplementedError("Member 3 to implement simulate_udp_stream in protocols/tcp_udp.py")
