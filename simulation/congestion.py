"""Congestion and bottleneck simulation (Member 2).

Provides runtime link congestion modifications and traffic volume simulation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from network.topology import Topology


def set_link_congestion(topology: Topology, u: str, v: str, congestion_level: float) -> bool:
    """Inject a specific congestion level into a communication link.

    Depends on:
        Member 1's Topology.update_link_metrics(u, v, congestion=...)

    Args:
        topology: Active Topology instance.
        u: Link endpoint node ID.
        v: Link endpoint node ID.
        congestion_level: Congestion factor in [0.0, 1.0].

    Returns:
        True if successfully applied, False if link not found.
    """
    if not (0.0 <= congestion_level <= 1.0):
        raise ValueError(f"Congestion level must be within [0.0, 1.0]: {congestion_level}")
    return bool(topology.update_link_metrics(u, v, congestion=congestion_level))


def apply_burst_congestion(topology: Topology, u: str, v: str, multiplier: float = 1.5) -> float:
    """Increase link congestion by a multiplier up to maximum 1.0.
    """
    if multiplier < 0:
        raise ValueError("Burst multiplier must be non-negative")
    link = topology.get_link(u, v)
    if link is None:
        raise ValueError(f"No link found between {u} and {v}")
    # A fully idle link would stay at 0 under pure multiplication, so a burst starts from a 10% floor.
    base = link.congestion if link.congestion > 0 else 0.1
    new_level = min(1.0, base * multiplier)
    topology.update_link_metrics(u, v, congestion=new_level)
    return new_level
