"""Tests for link congestion simulation (Member 2)."""

import pytest

from network.topology import Topology
from simulation.congestion import apply_burst_congestion, set_link_congestion


def test_set_link_congestion(linear_topology: Topology) -> None:
    res = set_link_congestion(linear_topology, "PC1", "R1", 0.75)
    assert res is True
    link = linear_topology.get_link("PC1", "R1")
    assert link is not None
    assert link.congestion == 0.75


def test_apply_burst_congestion(linear_topology: Topology) -> None:
    new_cong = apply_burst_congestion(linear_topology, "PC1", "R1", multiplier=2.0)
    assert new_cong > 0.1
