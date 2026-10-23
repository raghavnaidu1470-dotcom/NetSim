"""TCP and UDP protocol simulation demonstration (Member 3).

Models transport-layer behaviors: TCP connection establishment (3-way handshake),
sliding window flow control, timeouts, retransmissions, connection teardown (FIN),
and UDP connectionless datagram transmission.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, TypedDict


class TCPEvent(TypedDict):
    """Single event in a TCP transmission trace."""
    time_ms: float
    event_type: str  # SYN, SYN-ACK, ACK, DATA, TIMEOUT, RETRANSMIT, FIN, FIN-ACK, FAIL
    seq: int
    ack: int
    description: str


class UDPEvent(TypedDict):
    """Single event in a UDP transmission trace."""
    time_ms: float
    event_type: str  # DELIVERED, LOST
    packet_id: int
    description: str


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


class TCPSimulationResult(TypedDict):
    """Detailed result of simulate_tcp."""
    protocol: str
    sent: int
    retransmitted: int
    delivered: int
    failed: int
    total_time_ms: float
    handshake_latency_ms: float
    data_delivered_bytes: int
    effective_throughput_mbps: float
    events: List[TCPEvent]
    timeline: List[str]


class UDPSimulationResult(TypedDict):
    """Detailed result of simulate_udp."""
    protocol: str
    sent: int
    delivered: int
    lost: int
    delivered_percentage: float
    delivery_ratio: float
    total_time_ms: float
    events: List[UDPEvent]
    timeline: List[str]


def simulate_tcp(
    num_packets: int = 10,
    loss_probability: float = 0.05,
    timeout_ms: float = 80.0,
    seed: Optional[int] = 42,
    window_size: int = 1,
    rtt_ms: float = 40.0,
    max_retries: int = 3,
) -> TCPSimulationResult:
    """Simulate complete TCP lifecycle: 3-way handshake, windowed data transfer, timeouts, and teardown.

    Args:
        num_packets: Total data segments to transmit (>= 0).
        loss_probability: Packet drop probability per transmission in [0.0, 1.0].
        timeout_ms: Retransmission timer timeout duration in milliseconds.
        seed: Random seed for deterministic simulation.
        window_size: Sliding window size in segments (1 to 4).
        rtt_ms: Round-trip time in milliseconds (default 40.0 ms).
        max_retries: Maximum retransmission attempts per packet before reporting failure.

    Returns:
        TCPSimulationResult containing statistics, event list, and human-readable timeline.

    Example:
        >>> res = simulate_tcp(num_packets=5, loss_probability=0.0, seed=42)
        >>> res["delivered"]
        5
        >>> res["retransmitted"]
        0
    """
    if num_packets < 0:
        raise ValueError(f"num_packets cannot be negative, got {num_packets}")
    if not (0.0 <= loss_probability <= 1.0):
        raise ValueError(f"loss_probability must be within [0.0, 1.0], got {loss_probability}")

    effective_window = max(1, min(4, window_size))
    rng = random.Random(seed) if seed is not None else random.Random(42)

    events: List[TCPEvent] = []
    timeline: List[str] = []
    current_time_ms = 0.0

    # 1. Three-Way Handshake
    # Client -> Server: SYN
    current_time_ms += 0.5 * rtt_ms
    events.append({
        "time_ms": round(current_time_ms, 2),
        "event_type": "SYN",
        "seq": 0,
        "ack": 0,
        "description": "Client -> Server: SYN (seq=0)",
    })
    timeline.append(f"[{current_time_ms:.1f} ms] [SYN] Client -> Server: SYN (seq=0)")

    # Server -> Client: SYN-ACK
    current_time_ms += 0.5 * rtt_ms
    events.append({
        "time_ms": round(current_time_ms, 2),
        "event_type": "SYN-ACK",
        "seq": 0,
        "ack": 1,
        "description": "Server -> Client: SYN-ACK (seq=0, ack=1)",
    })
    timeline.append(f"[{current_time_ms:.1f} ms] [SYN-ACK] Server -> Client: SYN-ACK (seq=0, ack=1)")

    # Client -> Server: ACK
    current_time_ms += 0.5 * rtt_ms
    events.append({
        "time_ms": round(current_time_ms, 2),
        "event_type": "ACK",
        "seq": 1,
        "ack": 1,
        "description": "Client -> Server: ACK (seq=1, ack=1) - Connection Established",
    })
    timeline.append(f"[{current_time_ms:.1f} ms] [ACK] Client -> Server: ACK (seq=1, ack=1) [ESTABLISHED]")

    handshake_latency_ms = round(current_time_ms, 2)

    # 2. Windowed Data Transfer
    total_segments_sent = 0
    retransmissions_count = 0
    delivered_count = 0
    failed_count = 0

    packet_seq = 1
    while packet_seq <= num_packets:
        # Determine packets in current window burst
        burst_size = min(effective_window, num_packets - packet_seq + 1)
        for offset in range(burst_size):
            p_id = packet_seq + offset
            retries = 0
            delivered = False

            while retries <= max_retries:
                total_segments_sent += 1
                if retries > 0:
                    retransmissions_count += 1
                    events.append({
                        "time_ms": round(current_time_ms, 2),
                        "event_type": "RETRANSMIT",
                        "seq": p_id,
                        "ack": p_id,
                        "description": f"Client -> Server: Retransmit Segment {p_id} (Seq={p_id}, Attempt={retries})",
                    })
                    timeline.append(f"[{current_time_ms:.1f} ms] [RETRANSMIT] Segment {p_id} (Attempt {retries})")
                else:
                    events.append({
                        "time_ms": round(current_time_ms, 2),
                        "event_type": "DATA",
                        "seq": p_id,
                        "ack": p_id,
                        "description": f"Client -> Server: DATA Segment {p_id} (Seq={p_id})",
                    })
                    timeline.append(f"[{current_time_ms:.1f} ms] [DATA] Client -> Server: Segment {p_id}")

                # Check if dropped
                is_dropped = rng.random() < loss_probability
                if is_dropped:
                    # Timeout fires
                    current_time_ms += timeout_ms
                    events.append({
                        "time_ms": round(current_time_ms, 2),
                        "event_type": "TIMEOUT",
                        "seq": p_id,
                        "ack": 0,
                        "description": f"Timer Expired: Timeout waiting for ACK on Segment {p_id} (+{timeout_ms} ms)",
                    })
                    timeline.append(f"[{current_time_ms:.1f} ms] [TIMEOUT] Segment {p_id} timed out")
                    retries += 1
                    if retries > max_retries:
                        failed_count += 1
                        events.append({
                            "time_ms": round(current_time_ms, 2),
                            "event_type": "FAIL",
                            "seq": p_id,
                            "ack": 0,
                            "description": f"Segment {p_id} failed after reaching max retries ({max_retries})",
                        })
                        timeline.append(f"[{current_time_ms:.1f} ms] [FAIL] Segment {p_id} abandoned after {max_retries} retries")
                        break
                else:
                    # Successfully delivered: 1 RTT for data arrival and ACK return
                    # Concurrency adjustment based on window size
                    window_factor = 1.0 / effective_window
                    current_time_ms += (0.5 * rtt_ms) * window_factor
                    current_time_ms += (0.5 * rtt_ms) * window_factor
                    delivered_count += 1
                    events.append({
                        "time_ms": round(current_time_ms, 2),
                        "event_type": "ACK",
                        "seq": p_id,
                        "ack": p_id + 1,
                        "description": f"Server -> Client: ACK Segment {p_id} (Ack={p_id + 1})",
                    })
                    timeline.append(f"[{current_time_ms:.1f} ms] [ACK] Server -> Client: ACK (Ack={p_id + 1})")
                    delivered = True
                    break

        packet_seq += burst_size

    # 3. Connection Teardown (FIN handshake)
    # Client -> Server: FIN
    current_time_ms += 0.5 * rtt_ms
    events.append({
        "time_ms": round(current_time_ms, 2),
        "event_type": "FIN",
        "seq": num_packets + 1,
        "ack": num_packets + 1,
        "description": "Client -> Server: FIN (Connection Teardown)",
    })
    timeline.append(f"[{current_time_ms:.1f} ms] [FIN] Client -> Server: FIN")

    # Server -> Client: FIN-ACK
    current_time_ms += 0.5 * rtt_ms
    events.append({
        "time_ms": round(current_time_ms, 2),
        "event_type": "FIN-ACK",
        "seq": num_packets + 1,
        "ack": num_packets + 2,
        "description": "Server -> Client: FIN-ACK",
    })
    timeline.append(f"[{current_time_ms:.1f} ms] [FIN-ACK] Server -> Client: FIN-ACK")

    # Client -> Server: ACK
    current_time_ms += 0.5 * rtt_ms
    events.append({
        "time_ms": round(current_time_ms, 2),
        "event_type": "ACK",
        "seq": num_packets + 2,
        "ack": num_packets + 2,
        "description": "Client -> Server: ACK - Connection Closed [CLOSED]",
    })
    timeline.append(f"[{current_time_ms:.1f} ms] [ACK] Client -> Server: ACK [CLOSED]")

    total_time_ms = round(current_time_ms, 2)
    bytes_delivered = delivered_count * 1024  # Assuming 1 KB standard MSS
    throughput_mbps = (
        round((bytes_delivered * 8.0) / (total_time_ms * 1000.0), 4)
        if total_time_ms > 0
        else 0.0
    )

    return {
        "protocol": "TCP",
        "sent": total_segments_sent,
        "retransmitted": retransmissions_count,
        "delivered": delivered_count,
        "failed": failed_count,
        "total_time_ms": total_time_ms,
        "handshake_latency_ms": handshake_latency_ms,
        "data_delivered_bytes": bytes_delivered,
        "effective_throughput_mbps": throughput_mbps,
        "events": events,
        "timeline": timeline,
    }


def simulate_udp(
    num_packets: int = 10,
    loss_probability: float = 0.05,
    seed: Optional[int] = 42,
    rtt_ms: float = 40.0,
) -> UDPSimulationResult:
    """Simulate UDP connectionless datagram transmission (fire-and-forget).

    Args:
        num_packets: Total datagrams to transmit (>= 0).
        loss_probability: Packet drop probability per datagram in [0.0, 1.0].
        seed: Random seed for deterministic simulation.
        rtt_ms: Round-trip time in milliseconds (one-way propagation is 0.5 * rtt_ms).

    Returns:
        UDPSimulationResult containing delivery statistics, events, and timeline.

    Example:
        >>> res = simulate_udp(num_packets=10, loss_probability=0.0, seed=42)
        >>> res["delivered"]
        10
        >>> res["lost"]
        0
    """
    if num_packets < 0:
        raise ValueError(f"num_packets cannot be negative, got {num_packets}")
    if not (0.0 <= loss_probability <= 1.0):
        raise ValueError(f"loss_probability must be within [0.0, 1.0], got {loss_probability}")

    rng = random.Random(seed) if seed is not None else random.Random(42)
    events: List[UDPEvent] = []
    timeline: List[str] = []
    current_time_ms = 0.0
    one_way_delay = 0.5 * rtt_ms

    delivered_count = 0
    lost_count = 0

    for p_id in range(1, num_packets + 1):
        current_time_ms += one_way_delay
        is_dropped = rng.random() < loss_probability

        if is_dropped:
            lost_count += 1
            events.append({
                "time_ms": round(current_time_ms, 2),
                "event_type": "LOST",
                "packet_id": p_id,
                "description": f"Datagram {p_id} lost in transit (channel drop)",
            })
            timeline.append(f"[{current_time_ms:.1f} ms] [LOST] Datagram {p_id} dropped in channel")
        else:
            delivered_count += 1
            events.append({
                "time_ms": round(current_time_ms, 2),
                "event_type": "DELIVERED",
                "packet_id": p_id,
                "description": f"Datagram {p_id} delivered successfully",
            })
            timeline.append(f"[{current_time_ms:.1f} ms] [DELIVERED] Datagram {p_id} received")

    total_time_ms = round(current_time_ms, 2)
    delivery_ratio = round(delivered_count / num_packets, 4) if num_packets > 0 else 1.0
    delivered_pct = round(delivery_ratio * 100.0, 2)

    return {
        "protocol": "UDP",
        "sent": num_packets,
        "delivered": delivered_count,
        "lost": lost_count,
        "delivery_ratio": delivery_ratio,
        "delivered_percentage": delivered_pct,
        "total_time_ms": total_time_ms,
        "events": events,
        "timeline": timeline,
    }


def simulate_tcp_stream(
    payload_size_kb: int = 10,
    rtt_ms: float = 40.0,
    packet_loss_rate: float = 0.05,
    window_size_segments: int = 4,
    seed: int = 42,
) -> TCPSimulationSummary:
    """Simulate TCP connection setup, windowed data transfer, and retransmission.

    Args:
        payload_size_kb: Total volume of data to transmit in KB.
        rtt_ms: Round-trip time in milliseconds.
        packet_loss_rate: Drop probability per segment.
        window_size_segments: Sliding window size (segments).
        seed: Random seed for repeatability.

    Returns:
        TCPSimulationSummary matching the scaffolded TypedDict interface.
    """
    res = simulate_tcp(
        num_packets=payload_size_kb,
        loss_probability=packet_loss_rate,
        timeout_ms=rtt_ms * 2.0,
        seed=seed,
        window_size=window_size_segments,
        rtt_ms=rtt_ms,
    )
    return {
        "protocol": "TCP",
        "handshake_latency_ms": res["handshake_latency_ms"],
        "total_segments_sent": res["sent"],
        "retransmissions": res["retransmitted"],
        "data_delivered_bytes": res["data_delivered_bytes"],
        "effective_throughput_mbps": res["effective_throughput_mbps"],
        "total_time_ms": res["total_time_ms"],
        "timeline": res["timeline"],
    }


def simulate_udp_stream(
    payload_size_kb: int = 10,
    rtt_ms: float = 40.0,
    packet_loss_rate: float = 0.05,
    seed: int = 42,
) -> UDPSimulationSummary:
    """Simulate UDP connectionless datagram burst.

    Args:
        payload_size_kb: Total volume of data to transmit in KB.
        rtt_ms: Round-trip time in milliseconds.
        packet_loss_rate: Drop probability per datagram.
        seed: Random seed for repeatability.

    Returns:
        UDPSimulationSummary matching the scaffolded TypedDict interface.
    """
    res = simulate_udp(
        num_packets=payload_size_kb,
        loss_probability=packet_loss_rate,
        seed=seed,
        rtt_ms=rtt_ms,
    )
    return {
        "protocol": "UDP",
        "datagrams_sent": res["sent"],
        "datagrams_received": res["delivered"],
        "datagrams_dropped": res["lost"],
        "packet_loss_ratio": round(1.0 - res["delivery_ratio"], 4),
        "total_time_ms": res["total_time_ms"],
        "timeline": res["timeline"],
    }
