"""Explainable Routing Engine (Member 2).

Generates human-readable explanations and quantitative delta comparisons explaining
why XAR chose one route over an alternative (such as the shortest hop-count Dijkstra route).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypedDict

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

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Compute metrics for both selected_path and alternative_path.
    # TODO(Member 2 - Step 2): Calculate deltas: alternative_metric - selected_metric.
    # TODO(Member 2 - Step 3): Compute adaptive scores for both paths using active profile weights.
    # TODO(Member 2 - Step 4): Format comparative sentence explaining why the selected path won,
    #                          highlighting trade-offs (e.g. higher hops offset by superior latency/loss).
    # TODO(Member 2 - Step 5): Return populated RouteComparison dict.
    raise NotImplementedError("Member 2 to implement compare_routes in adaptive/explanation.py")
