"""Adapter for Explainable Adaptive Routing (XAR) and explanation integration (Member 3).

Provides a clean decoupling layer between the UI and Member 2's adaptive engine:
1. Calls adaptive.xar.xar_find_route if implemented.
2. If unimplemented (raises NotImplementedError or ImportError), falls back to a
   clearly labeled reference preview scoring paths using Member 1's enumerate_paths
   and the formula from docs/spec.md and adaptive/traffic_profiles.py.
3. Automatically drops the preview badge when Member 2's real implementation is available.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from adaptive.traffic_profiles import ProfileName, get_profile_weights
from network.devices import RouteResult

if TYPE_CHECKING:
    from network.topology import Topology

FALLBACK_BADGE_TEXT = "Reference preview"
FALLBACK_ALGO_LABEL = "XAR (reference preview, not Member 2's implementation)"
REAL_ALGO_LABEL = "XAR"

MAX_HOPS_CEILING = 10.0
MAX_LATENCY_CEILING = 200.0


def score_path_by_spec(
    topology: Topology,
    path: List[str],
    profile: str = "standard",
) -> Tuple[float, Dict[str, float]]:
    """Score a single candidate path according to the formal NetSim-X specification.

    Formula:
        Score(P) = w_h*H + w_l*L + w_c*C + w_p*P + w_r*(1 - R)

    Args:
        topology: Active Topology instance.
        path: Ordered list of node IDs.
        profile: Active traffic profile ('standard', 'real_time', 'reliable_data_transfer').

    Returns:
        Tuple of (scalar_score, raw_metrics_dict).
    """
    metrics = topology.get_path_metrics(path)
    weights = get_profile_weights(profile)

    h_norm = min(1.0, metrics["hop_count"] / MAX_HOPS_CEILING)
    l_norm = min(1.0, metrics["latency"] / MAX_LATENCY_CEILING)
    c_norm = metrics["congestion"]
    p_norm = metrics["packet_loss"]
    r_penalty = 1.0 - metrics["reliability"]

    score = (
        weights.w_h * h_norm
        + weights.w_l * l_norm
        + weights.w_c * c_norm
        + weights.w_p * p_norm
        + weights.w_r * r_penalty
    )

    return float(round(score, 4)), metrics


def resolve_xar_route(
    topology: Topology,
    source: str,
    destination: str,
    profile: str = "standard",
    max_hops: int = 8,
) -> Tuple[RouteResult, Dict[str, float], float, bool]:
    """Resolve optimal route using XAR, with automatic reference preview fallback.

    Args:
        topology: Active Topology instance.
        source: Source node ID.
        destination: Destination node ID.
        profile: Traffic profile ('standard', 'real_time', 'reliable_data_transfer').
        max_hops: Simple path hop cutoff limit.

    Returns:
        Tuple of (RouteResult, path_metrics_dict, score, is_fallback_flag).
    """
    # Validate endpoints
    if source not in topology.nodes or destination not in topology.nodes:
        missing = [n for n in (source, destination) if n not in topology.nodes]
        return (
            {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "invalid",
                "message": f"Node does not exist: {', '.join(missing)}",
                "algorithm": "xar",
            },
            {},
            1.0,
            False,
        )

    if not topology.nodes[source].active or not topology.nodes[destination].active:
        inactive = [n for n in (source, destination) if not topology.nodes[n].active]
        return (
            {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "no_route",
                "message": f"Node is inactive/down: {', '.join(inactive)}",
                "algorithm": "xar",
            },
            {},
            1.0,
            False,
        )

    if source == destination:
        return (
            {
                "path": [source],
                "hop_count": 0,
                "latency": 0.0,
                "status": "success",
                "message": "Source and destination are identical",
                "algorithm": "xar",
            },
            {"latency": 0.0, "packet_loss": 0.0, "reliability": 1.0, "congestion": 0.0, "hop_count": 0},
            0.0,
            False,
        )

    # 1. Attempt Member 2's implementation
    try:
        from adaptive.xar import xar_find_route

        route_res = xar_find_route(
            topology, source=source, destination=destination, profile=profile, max_hops=max_hops
        )
        if route_res.get("status") == "success" and route_res.get("path"):
            path = route_res["path"]
            score, metrics = score_path_by_spec(topology, path, profile=profile)
            return route_res, metrics, score, False
        return route_res, {}, 1.0, False
    except (ImportError, NotImplementedError):
        pass

    # 2. Reference preview fallback: score candidates enumerated by Member 1
    candidate_paths = topology.enumerate_paths(source, destination, max_hops=max_hops)
    if not candidate_paths:
        return (
            {
                "path": [],
                "hop_count": 0,
                "latency": 0.0,
                "status": "no_route",
                "message": "No path available between endpoints",
                "algorithm": "xar",
            },
            {},
            1.0,
            True,
        )

    evaluations = []
    for p in candidate_paths:
        score, metrics = score_path_by_spec(topology, p, profile=profile)
        evaluations.append((score, metrics["hop_count"], metrics["latency"], p, metrics))

    # Sort ascending: lowest score first, tie-break by fewest hops, then latency
    evaluations.sort(key=lambda item: (item[0], item[1], item[2], item[3]))
    best_score, _, _, best_path, best_metrics = evaluations[0]

    fallback_route: RouteResult = {
        "path": best_path,
        "hop_count": best_metrics["hop_count"],
        "latency": best_metrics["latency"],
        "status": "success",
        "message": f"Resolved via {FALLBACK_ALGO_LABEL}",
        "algorithm": "xar",
    }

    return fallback_route, best_metrics, best_score, True


def generate_xar_explanation(
    topology: Topology,
    selected_path: List[str],
    alternative_path: List[str],
    profile: str = "standard",
) -> Tuple[str, bool]:
    """Generate human-readable justification for why XAR chose selected_path over alternative_path.

    Returns:
        Tuple of (explanation_text, is_fallback_flag).
    """
    # 1. Attempt Member 2's explanation module
    try:
        from adaptive.explanation import compare_routes

        comp = compare_routes(topology, selected_path, alternative_path, profile=profile)
        if comp and "explanation_text" in comp:
            return comp["explanation_text"], False
    except (ImportError, NotImplementedError):
        pass

    # 2. Fallback metric-difference justification
    if not selected_path:
        return "No valid path selected by XAR.", True
    if not alternative_path:
        return f"XAR selected {' ➔ '.join(selected_path)} as the sole available route.", True
    if selected_path == alternative_path:
        return (
            f"Both algorithms converged on identical path {' ➔ '.join(selected_path)}, "
            f"which achieves the optimal balance under profile '{profile}'.",
            True,
        )

    sel_score, sel_m = score_path_by_spec(topology, selected_path, profile=profile)
    alt_score, alt_m = score_path_by_spec(topology, alternative_path, profile=profile)

    lat_diff = alt_m["latency"] - sel_m["latency"]
    cong_diff = (alt_m["congestion"] - sel_m["congestion"]) * 100.0
    loss_diff = (alt_m["packet_loss"] - sel_m["packet_loss"]) * 100.0
    hop_diff = sel_m["hop_count"] - alt_m["hop_count"]

    reasons = []
    if lat_diff > 0:
        reasons.append(f"latency is {lat_diff:.1f} ms lower")
    elif lat_diff < 0:
        reasons.append(f"latency is {abs(lat_diff):.1f} ms higher")

    if cong_diff > 0:
        reasons.append(f"bottleneck congestion is {cong_diff:.0f}% lower")
    elif cong_diff < 0:
        reasons.append(f"bottleneck congestion is {abs(cong_diff):.0f}% higher")

    if loss_diff > 0:
        reasons.append(f"expected packet drop rate is {loss_diff:.1f}% lower")
    elif loss_diff < 0:
        reasons.append(f"packet drop rate is {abs(loss_diff):.1f}% higher")

    reasons_str = ", ".join(reasons) if reasons else "metrics were closely matched"

    tradeoff = ""
    if hop_diff > 0:
        tradeoff = f" Despite requiring {hop_diff} additional hop(s), "
    elif hop_diff < 0:
        tradeoff = f" Along with saving {abs(hop_diff)} hop(s), "

    explanation = (
        f"XAR selected {' ➔ '.join(selected_path)} over alternative {' ➔ '.join(alternative_path)} "
        f"because {reasons_str}.{tradeoff}under the '{profile}' traffic profile, "
        f"XAR achieved a superior penalty score of {sel_score:.4f} vs {alt_score:.4f}."
    )

    return explanation, True
