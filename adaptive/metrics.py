"""Path metric aggregation, normalization, and XAR scoring math (Member 2).

Defines normalization rules (fixed ceilings) and aggregation functions converting
raw path properties into unit-interval [0.0, 1.0] components for XAR evaluation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, TypedDict

from adaptive.traffic_profiles import ProfileWeights

if TYPE_CHECKING:
    from network.topology import Topology

# Normalization constants (documented in docs/spec.md)
MAX_LATENCY_CEILING: float = 200.0  # Latencies >= 200ms normalized to 1.0
MAX_HOPS_CEILING: float = 10.0     # Hops >= 10 normalized to 1.0


class RawPathMetrics(TypedDict):
    """Raw aggregated metrics across all links along a path."""
    latency: float       # Cumulative delay in ms
    packet_loss: float   # End-to-end drop probability 1 - prod(1 - p_i)
    reliability: float   # End-to-end reliability prod(r_i)
    congestion: float    # Bottleneck max congestion max(c_i)
    hop_count: int       # Number of traversed links (len(path) - 1)


class NormalizedMetrics(TypedDict):
    """Unit-interval normalized metrics in [0.0, 1.0], where 0 is ideal and 1 is worst."""
    H: float  # Normalized hop count = min(1.0, hop_count / MAX_HOPS_CEILING)
    L: float  # Normalized latency = min(1.0, latency / MAX_LATENCY_CEILING)
    C: float  # Congestion (bottleneck link congestion)
    P: float  # Packet loss probability
    R_penalty: float  # Reliability penalty = 1.0 - reliability


def aggregate_path_metrics(topology: Topology, path: List[str]) -> RawPathMetrics:
    """Aggregate raw performance metrics across all links along a given path.

    Depends on:
        Member 1's Topology.get_link(u, v)

    Args:
        topology: Active Topology instance.
        path: Ordered list of node IDs forming a path (e.g. ['PC1', 'R1', 'R2', 'PC2']).

    Returns:
        RawPathMetrics dictionary containing latency, packet_loss, reliability,
        congestion, and hop_count.

    Example:
        >>> metrics = aggregate_path_metrics(topo, ['PC1', 'R1', 'PC2'])
        >>> print(metrics['latency'])
        14.0

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Verify path length >= 2; return zeros for single node/empty.
    # TODO(Member 2 - Step 2): Iterate consecutive pairs (path[i], path[i+1]).
    # TODO(Member 2 - Step 3): Sum latency, compute success_prob = prod(1 - loss),
    #                          compute reliability_prod = prod(rel), record link congestion.
    # TODO(Member 2 - Step 4): Return RawPathMetrics with aggregated values.
    raise NotImplementedError("Member 2 to implement aggregate_path_metrics in adaptive/metrics.py")


def normalize_metrics(raw: RawPathMetrics) -> NormalizedMetrics:
    """Normalize raw path metrics into unit interval [0.0, 1.0].

    Formula:
        H = min(1.0, raw['hop_count'] / MAX_HOPS_CEILING)
        L = min(1.0, raw['latency'] / MAX_LATENCY_CEILING)
        C = min(1.0, max(0.0, raw['congestion']))
        P = min(1.0, max(0.0, raw['packet_loss']))
        R_penalty = min(1.0, max(0.0, 1.0 - raw['reliability']))

    Args:
        raw: RawPathMetrics dictionary.

    Returns:
        NormalizedMetrics with all fields in [0.0, 1.0].

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Apply ceilings MAX_HOPS_CEILING and MAX_LATENCY_CEILING.
    # TODO(Member 2 - Step 2): Calculate R_penalty as (1.0 - raw['reliability']).
    # TODO(Member 2 - Step 3): Clamp all values strictly to [0.0, 1.0] to prevent rounding overflow.
    raise NotImplementedError("Member 2 to implement normalize_metrics in adaptive/metrics.py")


def compute_path_score(norm: NormalizedMetrics, weights: ProfileWeights) -> float:
    """Calculate composite XAR score for a normalized path under given profile weights.

    Formula:
        Score(P) = w_h*H + w_l*L + w_c*C + w_p*P + w_r*(1 - R)
        Lower score is better.

    Args:
        norm: NormalizedMetrics dictionary.
        weights: ProfileWeights for the selected traffic profile.

    Returns:
        Calculated scalar score (float between 0.0 and 1.0).

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Multiply each normalized component by its corresponding weight.
    # TODO(Member 2 - Step 2): Sum the products and round to 4 decimal places.
    raise NotImplementedError("Member 2 to implement compute_path_score in adaptive/metrics.py")
