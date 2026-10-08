"""Adaptive Routing package for NetSim-X (Member 2).

Includes Explainable Adaptive Routing (XAR), normalization, traffic profiles,
and decision explanations.
"""

from adaptive.explanation import RouteComparison, compare_routes
from adaptive.metrics import (
    MAX_HOPS_CEILING,
    MAX_LATENCY_CEILING,
    NormalizedMetrics,
    RawPathMetrics,
    aggregate_path_metrics,
    compute_path_score,
    normalize_metrics,
)
from adaptive.mock_data import MOCK_ROUTE_RESULTS
from adaptive.traffic_profiles import (
    TRAFFIC_PROFILES,
    ProfileName,
    ProfileWeights,
    get_profile_weights,
)
from adaptive.xar import PathEvaluation, evaluate_all_candidate_paths, xar_find_route

__all__ = [
    "TRAFFIC_PROFILES",
    "ProfileName",
    "ProfileWeights",
    "get_profile_weights",
    "MAX_LATENCY_CEILING",
    "MAX_HOPS_CEILING",
    "RawPathMetrics",
    "NormalizedMetrics",
    "aggregate_path_metrics",
    "normalize_metrics",
    "compute_path_score",
    "PathEvaluation",
    "evaluate_all_candidate_paths",
    "xar_find_route",
    "RouteComparison",
    "compare_routes",
    "MOCK_ROUTE_RESULTS",
]
