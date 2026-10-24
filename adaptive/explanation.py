"""Explainable Routing Engine (Member 2).

Generates human-readable explanations and quantitative delta comparisons explaining
why XAR chose one route over an alternative (such as the shortest hop-count Dijkstra route).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

from adaptive.metrics import MAX_LATENCY_CEILING, RawPathMetrics, aggregate_path_metrics, compute_path_score, normalize_metrics
from adaptive.traffic_profiles import ProfileName, get_profile_weights

if TYPE_CHECKING:
    from network.topology import Topology


class RouteComparison(TypedDict):
    """Detailed quantitative and textual comparison between two candidate routes."""
    selected_path: List[str]
    alternative_path: List[str]
    selected_metrics: Dict[str, float]
    alternative_metrics: Dict[str, float]
    deltas: Dict[str, float]
    selected_score: float
    alternative_score: float
    explanation_text: str


def compare_routes(
    topology: Topology,
    selected_path: List[str],
    alternative_path: List[str],
    profile: str = "standard",
) -> RouteComparison:
    """Compare two routes and produce a human-readable explanation justifying the selection.

    Example output explanation:
        "XAR selected PC1 -> R1 -> R3 -> R4 -> R5 -> PC2 because latency was 43.0 ms lower,
         congestion was 70.0% lower, and expected packet loss was 16.0% lower. Although the
         alternative had 1 fewer hop, its adaptive score was 0.68 vs 0.29 under the standard profile."

    Args:
        topology: Active Topology instance.
        selected_path: Path chosen by XAR.
        alternative_path: Path chosen by shortest path or alternative.
        profile: Active traffic profile.

    Returns:
        RouteComparison dictionary with metrics, deltas, scores, and explanation_text.
    """
    weights = get_profile_weights(profile)
    sel = _metrics_or_worst(topology, selected_path)
    alt = _metrics_or_worst(topology, alternative_path)
    sel_score = compute_path_score(normalize_metrics(sel), weights)
    alt_score = compute_path_score(normalize_metrics(alt), weights)

    # Sign convention: a positive delta means the selected path is better on that metric.
    deltas: Dict[str, float] = {
        "latency": round(alt["latency"] - sel["latency"], 2),
        "congestion": round(alt["congestion"] - sel["congestion"], 4),
        "packet_loss": round(alt["packet_loss"] - sel["packet_loss"], 4),
        "reliability": round(sel["reliability"] - alt["reliability"], 4),
        "hop_count": alt["hop_count"] - sel["hop_count"],
        "score": round(alt_score - sel_score, 4),
    }
    text = _build_explanation_text(selected_path, alternative_path, deltas, sel_score, alt_score, _profile_label(profile))
    return {
        "selected_path": list(selected_path),
        "alternative_path": list(alternative_path),
        "selected_metrics": dict(sel),
        "alternative_metrics": dict(alt),
        "deltas": deltas,
        "selected_score": sel_score,
        "alternative_score": alt_score,
        "explanation_text": text,
    }


def _metrics_or_worst(topology: Topology, path: List[str]) -> RawPathMetrics:
    """Aggregate a path's metrics; a hypothetical path with a missing link is scored as worst case."""
    if len(path) < 2:
        return aggregate_path_metrics(topology, path)
    try:
        return aggregate_path_metrics(topology, path)
    except ValueError:
        return {"latency": MAX_LATENCY_CEILING, "packet_loss": 1.0, "reliability": 0.0, "congestion": 1.0, "hop_count": len(path) - 1}


_PROFILE_LABELS = {"standard": "standard", "real_time": "real-time", "reliable_data_transfer": "reliable data transfer"}


def _profile_label(profile: str) -> str:
    key = profile.lower().strip().replace("-", "_").replace(" ", "_")
    return _PROFILE_LABELS.get(key, "standard")  # unknown names fall back to standard, like get_profile_weights


def _join(parts: List[str]) -> str:
    if len(parts) <= 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def _build_explanation_text(selected: List[str], alternative: List[str], d: Dict[str, float], sel_score: float, alt_score: float, label: str) -> str:
    sel_str = " -> ".join(selected)
    if selected == alternative:
        return f"XAR selected {sel_str}; it is also the alternative route, so no trade-off was needed (adaptive score {sel_score:.2f} under the {label} profile)."

    wins: List[str] = []
    losses: List[str] = []

    def note(delta: float, name: str, scale: float, unit: str) -> None:
        if abs(delta) < 1e-9:
            return
        amount = abs(delta) * scale
        (wins if delta > 0 else losses).append(f"{name} was {amount:.1f}{unit} {'lower' if delta > 0 else 'higher'}")

    note(d["latency"], "latency", 1.0, " ms")
    note(d["congestion"], "congestion", 100.0, "%")
    note(d["packet_loss"], "expected packet loss", 100.0, "%")

    text = f"XAR selected {sel_str} because {_join(wins)}." if wins else f"XAR selected {sel_str} because it had the lowest adaptive score."
    hop_gap = int(d["hop_count"])  # alternative hops minus selected hops
    if hop_gap < 0:
        n = -hop_gap
        text += f" Although the alternative had {n} fewer hop{'s' if n != 1 else ''}, its adaptive score was {alt_score:.2f} vs {sel_score:.2f} under the {label} profile."
    elif hop_gap > 0:
        text += f" The selected route also has {hop_gap} fewer hop{'s' if hop_gap != 1 else ''}; its adaptive score was {sel_score:.2f} vs {alt_score:.2f} under the {label} profile."
    else:
        text += f" Both routes have the same number of hops; the adaptive score was {sel_score:.2f} vs {alt_score:.2f} under the {label} profile."
    if losses:
        text += " Trade-off: " + _join(losses) + "."
    return text
