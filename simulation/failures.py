"""Network failure and resilience simulation (Member 2).

Provides node/link failure toggles, resilience recovery time calculations,
and before-and-after failure rerouting impact analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from network.topology import Topology


class RecoveryMetrics(TypedDict):
    """Metrics tracking recovery and resilience after a network failure."""
    failure_target: str
    target_type: str  # 'node' or 'link'
    detection_delay_ms: float
    recomputation_rounds: int
    per_round_delay_ms: float
    total_recovery_time_ms: float
    original_path: List[str]
    rerouted_path: List[str]
    extra_hops: int
    latency_delta_ms: float
    packets_dropped: int


def calculate_recovery_time(
    detection_delay_ms: float,
    recomputation_rounds: int,
    per_round_delay_ms: float = 50.0,
) -> float:
    """Calculate explicit recovery time according to the NetSim-X specification.

    Formula:
        Recovery Time = detection_delay + (recomputation_rounds * per_round_delay)

    Args:
        detection_delay_ms: Time required for keepalive/heartbeat timeout (ms).
        recomputation_rounds: Routing protocol convergence iterations.
        per_round_delay_ms: Network propagation and processing delay per round (ms).

    Returns:
        Total recovery time in milliseconds.
    """
    return float(detection_delay_ms + (recomputation_rounds * per_round_delay_ms))


def trigger_node_failure(
    topology: Topology,
    node_id: str,
    source: str,
    destination: str,
    algorithm: str = "xar",
    detection_delay_ms: float = 150.0,
    per_round_delay_ms: float = 50.0,
) -> RecoveryMetrics:
    """Simulate a router crash, calculate recovery time, and determine the rerouted path.

    Depends on:
        Member 1's Topology.set_node_active(node_id, False)
        Member 1's Topology.find_route(source, destination, algorithm)

    Args:
        topology: Topology instance before failure.
        node_id: Router or host ID to fail.
        source: Traffic flow source ID.
        destination: Traffic flow destination ID.
        algorithm: Routing engine to invoke for rerouting.
        detection_delay_ms: Heartbeat failure detection time in ms.
        per_round_delay_ms: Propagation round delay in ms.

    Returns:
        RecoveryMetrics capturing recovery duration, path shift, and packet drop estimates.

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Compute pre-failure route via topology.find_route.
    # TODO(Member 2 - Step 2): Deactivate node via topology.set_node_active(node_id, False).
    # TODO(Member 2 - Step 3): Recompute route via topology.find_route.
    # TODO(Member 2 - Step 4): Calculate recovery time using calculate_recovery_time.
    # TODO(Member 2 - Step 5): Return RecoveryMetrics dictionary.
    raise NotImplementedError("Member 2 to implement trigger_node_failure in simulation/failures.py")


def trigger_link_failure(
    topology: Topology,
    u: str,
    v: str,
    source: str,
    destination: str,
    algorithm: str = "xar",
) -> RecoveryMetrics:
    """Simulate a link cut between nodes u and v and reroute active flows.

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Record pre-failure route.
    # TODO(Member 2 - Step 2): Deactivate link via topology.set_link_active(u, v, False).
    # TODO(Member 2 - Step 3): Recompute route and return RecoveryMetrics.
    raise NotImplementedError("Member 2 to implement trigger_link_failure in simulation/failures.py")
