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
    """
    if not path or len(path) < 2:
        return {"latency": 0.0, "packet_loss": 0.0, "reliability": 1.0, "congestion": 0.0, "hop_count": 0}

    total_latency = 0.0
    success_prob = 1.0
    reliability_prod = 1.0
    bottleneck = 0.0
    for u, v in zip(path, path[1:]):
        link = topology.get_link(u, v)
        if link is None:
            raise ValueError(f"No link found between {u} and {v}")
        total_latency += link.latency
        success_prob *= 1.0 - link.packet_loss
        reliability_prod *= link.reliability
        bottleneck = max(bottleneck, link.congestion)

    return {
        "latency": round(total_latency, 2),
        "packet_loss": round(1.0 - success_prob, 4),
        "reliability": round(reliability_prod, 4),
        "congestion": round(bottleneck, 4),
        "hop_count": len(path) - 1,
    }


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
    """
    def clamp(x: float) -> float:
        return min(1.0, max(0.0, float(x)))

    return {
        "H": clamp(raw["hop_count"] / MAX_HOPS_CEILING),
        "L": clamp(raw["latency"] / MAX_LATENCY_CEILING),
        "C": clamp(raw["congestion"]),
        "P": clamp(raw["packet_loss"]),
        "R_penalty": clamp(1.0 - raw["reliability"]),
    }


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
    """
    score = (
        weights.w_h * norm["H"]
        + weights.w_l * norm["L"]
        + weights.w_c * norm["C"]
        + weights.w_p * norm["P"]
        + weights.w_r * norm["R_penalty"]
    )
    return round(score, 4)
