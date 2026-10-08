"""Explainable Adaptive Routing (XAR) Engine (Member 2).

Evaluates all simple candidate paths using multi-metric traffic-profile scoring
and selects the globally optimal path balancing latency, loss, congestion, and hops.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

from adaptive.traffic_profiles import ProfileName, get_profile_weights
from network.devices import RouteResult

if TYPE_CHECKING:
    from network.topology import Topology


class PathEvaluation(TypedDict):
    """Evaluation summary of a candidate path."""
    path: List[str]
    score: float
    raw_metrics: Dict[str, float]
    normalized_metrics: Dict[str, float]


def evaluate_all_candidate_paths(
    topology: Topology,
    source: str,
    destination: str,
    profile: str = "standard",
    max_hops: int = 8,
) -> List[PathEvaluation]:
    """Enumerate and score all candidate simple paths between source and destination.

    Depends on:
        Member 1's Topology.enumerate_paths(source, destination, max_hops)
        Member 2's adaptive.metrics.aggregate_path_metrics
        Member 2's adaptive.metrics.normalize_metrics
        Member 2's adaptive.metrics.compute_path_score

    Args:
        topology: Active Topology instance.
        source: Source node ID.
        destination: Destination node ID.
        profile: Traffic profile ('standard', 'real_time', 'reliable_data_transfer').
        max_hops: Hop cutoff limit.

    Returns:
        Sorted list of PathEvaluation dicts ordered by score ascending (lowest/best first).

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Call topology.enumerate_paths(source, destination, max_hops).
    # TODO(Member 2 - Step 2): If no paths found, return empty list.
    # TODO(Member 2 - Step 3): Retrieve weights via get_profile_weights(profile).
    # TODO(Member 2 - Step 4): For each path, compute raw metrics, normalized metrics, and score.
    # TODO(Member 2 - Step 5): Sort evaluations by score ascending and return.
    raise NotImplementedError("Member 2 to implement evaluate_all_candidate_paths in adaptive/xar.py")


def xar_find_route(
    topology: Topology,
    source: str,
    destination: str,
    profile: str = "standard",
    max_hops: int = 8,
) -> RouteResult:
    """Find the optimal route using the Explainable Adaptive Routing (XAR) engine.

    Args:
        topology: Active Topology instance.
        source: Source node ID.
        destination: Destination node ID.
        profile: Traffic profile ('standard', 'real_time', 'reliable_data_transfer').
        max_hops: Hop cutoff limit.

    Returns:
        RouteResult dictionary with 'path', 'hop_count', 'latency', 'status'.

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Validate source and destination.
    # TODO(Member 2 - Step 2): Call evaluate_all_candidate_paths.
    # TODO(Member 2 - Step 3): If evaluations exist, pick the first (lowest score).
    # TODO(Member 2 - Step 4): Return RouteResult with status 'success'.
    # TODO(Member 2 - Step 5): If no path exists, return status 'no_route'.
    raise NotImplementedError("Member 2 to implement xar_find_route in adaptive/xar.py")
