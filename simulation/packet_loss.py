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

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Get path loss probability via topology.get_path_metrics(path)['packet_loss'].
    # TODO(Member 2 - Step 2): Seed random generator.
    # TODO(Member 2 - Step 3): For each packet, simulate success/drop across each link hop.
    # TODO(Member 2 - Step 4): Calculate retransmissions if transport is reliable (TCP-style).
    # TODO(Member 2 - Step 5): Return populated PacketSimulationResult.
    raise NotImplementedError("Member 2 to implement simulate_packet_transmission in simulation/packet_loss.py")
