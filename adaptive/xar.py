"""Explainable Adaptive Routing (XAR) Engine (Member 2).

Evaluates all simple candidate paths using multi-metric traffic-profile scoring
and selects the globally optimal path balancing latency, loss, congestion, and hops.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

from adaptive.metrics import aggregate_path_metrics, compute_path_score, normalize_metrics
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
    """
    paths = topology.enumerate_paths(source, destination, max_hops)
    if not paths:
        return []

    weights = get_profile_weights(profile)
    evaluations: List[PathEvaluation] = []
    for path in paths:
        raw = aggregate_path_metrics(topology, path)
        norm = normalize_metrics(raw)
        evaluations.append({
            "path": path,
            "score": compute_path_score(norm, weights),
            "raw_metrics": dict(raw),
            "normalized_metrics": dict(norm),
        })

    # Lowest score first; ties are broken deterministically by fewer hops, lower latency, then path order.
    evaluations.sort(key=lambda e: (e["score"], e["raw_metrics"]["hop_count"], e["raw_metrics"]["latency"], e["path"]))
    return evaluations


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
    """
    def result(path: List[str], hops: int, latency: float, status: str, message: str) -> RouteResult:
        return {"path": path, "hop_count": hops, "latency": latency, "status": status, "message": message, "algorithm": "xar"}  # type: ignore[return-value]

    if source not in topology.nodes or destination not in topology.nodes:
        missing = [n for n in (source, destination) if n not in topology.nodes]
        return result([], 0, 0.0, "invalid", f"Node does not exist in topology: {', '.join(missing)}")
    inactive = [n for n in (source, destination) if not topology.nodes[n].active]
    if inactive:
        return result([], 0, 0.0, "no_route", f"Node is inactive/down: {', '.join(inactive)}")
    if source == destination:
        return result([source], 0, 0.0, "success", "Source and destination are identical")

    evaluations = evaluate_all_candidate_paths(topology, source, destination, profile, max_hops)
    if not evaluations:
        return result([], 0, 0.0, "no_route", f"No active path found between '{source}' and '{destination}'")

    best = evaluations[0]
    return result(
        list(best["path"]),
        int(best["raw_metrics"]["hop_count"]),
        float(best["raw_metrics"]["latency"]),
        "success",
        f"XAR selected the lowest-score path ({best['score']:.4f}) under the '{profile}' profile",
    )
