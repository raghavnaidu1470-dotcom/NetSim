"""Network failure and resilience simulation (Member 2).

Provides node/link failure toggles, resilience recovery time calculations,
and before-and-after failure rerouting impact analysis.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, TypedDict

from network.distance_vector import simulate_distance_vector_reconvergence

if TYPE_CHECKING:
    from network.devices import RouteResult
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


ASSUMED_TRAFFIC_RATE_PPS: float = 35.0
"""Assumed offered load (packets per second) used to estimate packets lost while the network is
re-converging. At 35 pps a 350 ms outage loses about 12 packets, the figure used in the specification."""


def _route(topology: Topology, source: str, destination: str, algorithm: str, profile: str) -> RouteResult:
    return topology.find_route(source, destination, algorithm, profile=profile)


def _reconvergence_rounds(
    topology: Topology, failed_node: Optional[str] = None, failed_link: Optional[Tuple[str, str]] = None
) -> int:
    """Distance-vector rounds needed to settle after the failure, measured on a copy of the topology."""
    probe = copy.deepcopy(topology)  # simulate_distance_vector_reconvergence mutates the topology it is given
    result = simulate_distance_vector_reconvergence(probe, failed_node=failed_node, failed_link=failed_link, metric="hop")
    return max(1, int(result["reconvergence_rounds"]))


def _summarise(
    target: str, target_type: str, on_flow: bool, before: RouteResult, after: RouteResult,
    rounds: int, detection_delay_ms: float, per_round_delay_ms: float,
) -> RecoveryMetrics:
    recovery = calculate_recovery_time(detection_delay_ms, rounds, per_round_delay_ms)
    ok_before = before.get("status") == "success"
    ok_after = after.get("status") == "success"
    both = ok_before and ok_after
    return {
        "failure_target": target,
        "target_type": target_type,
        "detection_delay_ms": float(detection_delay_ms),
        "recomputation_rounds": rounds,
        "per_round_delay_ms": float(per_round_delay_ms),
        "total_recovery_time_ms": recovery,
        "original_path": list(before["path"]) if ok_before else [],
        "rerouted_path": list(after["path"]) if ok_after else [],
        "extra_hops": int(after["hop_count"] - before["hop_count"]) if both else 0,
        "latency_delta_ms": round(after["latency"] - before["latency"], 2) if both else 0.0,
        # Packets are only lost if the flow actually crossed the failed element.
        "packets_dropped": int(round(recovery / 1000.0 * ASSUMED_TRAFFIC_RATE_PPS)) if on_flow else 0,
    }

def trigger_node_failure(
    topology: Topology,
    node_id: str,
    source: str,
    destination: str,
    algorithm: str = "xar",
    detection_delay_ms: float = 150.0,
    per_round_delay_ms: float = 50.0,
    profile: str = "standard",
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
        profile: Traffic profile used when algorithm is 'xar'.

    Returns:
        RecoveryMetrics capturing recovery duration, path shift, and packet drop estimates.

    Note:
        The failure is applied to the topology that is passed in (the router is deactivated). Pass a
        copy for a what-if analysis. The rounds in the recovery formula are measured with the
        distance-vector reconvergence simulation. Raises ValueError for an unknown node.
    """
    if topology.get_node(node_id) is None:
        raise ValueError(f"Unknown node '{node_id}'")
    topology.set_node_active(node_id, True)  # evaluate the 'before' state with the device up
    before = _route(topology, source, destination, algorithm, profile)
    rounds = _reconvergence_rounds(topology, failed_node=node_id)
    topology.set_node_active(node_id, False)  # the failure is applied to the topology that was passed in
    after = _route(topology, source, destination, algorithm, profile)
    on_flow = node_id in before.get("path", [])
    return _summarise(node_id, "node", on_flow, before, after, rounds, detection_delay_ms, per_round_delay_ms)


def trigger_link_failure(
    topology: Topology,
    u: str,
    v: str,
    source: str,
    destination: str,
    algorithm: str = "xar",
    detection_delay_ms: float = 150.0,
    per_round_delay_ms: float = 50.0,
    profile: str = "standard",
) -> RecoveryMetrics:
    """Simulate a link cut between nodes u and v and reroute active flows.

    Like trigger_node_failure, the cut is applied to the topology that is passed in. Raises ValueError
    when the link does not exist.
    """
    if topology.get_link(u, v) is None:
        raise ValueError(f"No link found between {u} and {v}")
    topology.set_link_active(u, v, True)  # evaluate the 'before' state with the link up
    before = _route(topology, source, destination, algorithm, profile)
    rounds = _reconvergence_rounds(topology, failed_link=(u, v))
    topology.set_link_active(u, v, False)  # the failure is applied to the topology that was passed in
    after = _route(topology, source, destination, algorithm, profile)
    path = before.get("path", [])
    on_flow = any({a, b} == {u, v} for a, b in zip(path, path[1:]))
    return _summarise(f"{u}-{v}", "link", on_flow, before, after, rounds, detection_delay_ms, per_round_delay_ms)
