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

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Validate congestion_level is in [0.0, 1.0].
    # TODO(Member 2 - Step 2): Call topology.update_link_metrics(u, v, congestion=congestion_level).
    # TODO(Member 2 - Step 3): Return success boolean.
    raise NotImplementedError("Member 2 to implement set_link_congestion in simulation/congestion.py")


def apply_burst_congestion(topology: Topology, u: str, v: str, multiplier: float = 1.5) -> float:
    """Increase link congestion by a multiplier up to maximum 1.0.

    Raises:
        NotImplementedError: If not yet implemented by Member 2.
    """
    # TODO(Member 2 - Step 1): Retrieve existing link congestion.
    # TODO(Member 2 - Step 2): Multiply, clamp to 1.0, update link, and return new level.
    raise NotImplementedError("Member 2 to implement apply_burst_congestion in simulation/congestion.py")
