"""Packet loss and transport statistical simulation (Member 2).

Simulates stochastic packet transmission along a path, calculating packets delivered,
packets dropped, and retransmissions.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any, Dict, List, TypedDict

if TYPE_CHECKING:
    from network.topology import Topology


class PacketSimulationResult(TypedDict):
    """Statistical summary of simulated packet transmissions."""
    packets_sent: int
    packets_delivered: int
    packets_dropped: int
    retransmissions: int
    effective_throughput_mbps: float
    delivery_ratio: float


def simulate_packet_transmission(
    topology: Topology,
    path: List[str],
    num_packets: int = 100,
    seed: int = 42,
) -> PacketSimulationResult:
    """Simulate transmission of packets along a network path considering link loss probabilities.

    Depends on:
        Member 1's Topology.get_path_metrics(path)

    Args:
        topology: Active Topology instance.
        path: Ordered list of nodes along the path.
        num_packets: Total number of discrete packets sent.
        seed: Random seed for reproducible simulation runs.

    Returns:
        PacketSimulationResult containing delivery, loss, and retransmission stats.
    """
    if num_packets < 0:
        raise ValueError("num_packets must be non-negative")
    if num_packets == 0:
        return {"packets_sent": 0, "packets_delivered": 0, "packets_dropped": 0, "retransmissions": 0, "effective_throughput_mbps": 0.0, "delivery_ratio": 1.0}
    if not path:
        return {"packets_sent": num_packets, "packets_delivered": 0, "packets_dropped": num_packets, "retransmissions": 0, "effective_throughput_mbps": 0.0, "delivery_ratio": 0.0}
    if len(path) == 1:  # source == destination: nothing crosses a link
        return {"packets_sent": num_packets, "packets_delivered": num_packets, "packets_dropped": 0, "retransmissions": 0, "effective_throughput_mbps": 0.0, "delivery_ratio": 1.0}

    rng = random.Random(seed)
    link_losses: List[float] = []
    usable_bandwidth = float("inf")
    for u, v in zip(path, path[1:]):
        link = topology.get_link(u, v)
        if link is None:
            raise ValueError(f"No link found between {u} and {v}")
        link_losses.append(link.packet_loss)
        usable_bandwidth = min(usable_bandwidth, link.bandwidth * (1.0 - link.congestion))  # congestion eats bandwidth

    delivered = 0
    for _ in range(num_packets):
        if all(rng.random() >= p for p in link_losses):  # the packet must survive every hop
            delivered += 1
    dropped = num_packets - delivered
    ratio = delivered / num_packets
    return {
        "packets_sent": num_packets,
        "packets_delivered": delivered,
        "packets_dropped": dropped,
        "retransmissions": dropped,  # a TCP-style sender resends each lost packet at least once
        "effective_throughput_mbps": round(max(0.0, usable_bandwidth) * ratio, 2),
        "delivery_ratio": round(ratio, 4),
    }
