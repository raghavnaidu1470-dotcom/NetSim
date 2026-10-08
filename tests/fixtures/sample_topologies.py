"""Shared pytest fixtures providing standard network topologies."""

import pytest

from network.devices import Link, Node
from network.topology import Topology


@pytest.fixture
def linear_topology() -> Topology:
    """A linear 3-node topology: PC1 <-> R1 <-> PC2."""
    topo = Topology(name="linear_test")
    topo.add_node(Node(id="PC1", ip="192.168.1.10", type="host"))
    topo.add_node(Node(id="R1", ip="192.168.1.1", type="router"))
    topo.add_node(Node(id="PC2", ip="192.168.2.10", type="host"))

    topo.add_link(Link(source="PC1", destination="R1", latency=5.0, congestion=0.1))
    topo.add_link(Link(source="R1", destination="PC2", latency=10.0, congestion=0.2))
    return topo


@pytest.fixture
def triangle_topology() -> Topology:
    """A 3-router triangle topology with equal and alternative paths:
    R1 <-> R2 (10ms)
    R2 <-> R3 (10ms)
    R1 <-> R3 (30ms)
    """
    topo = Topology(name="triangle_test")
    topo.add_node(Node(id="R1", ip="10.0.1.1", type="router"))
    topo.add_node(Node(id="R2", ip="10.0.2.1", type="router"))
    topo.add_node(Node(id="R3", ip="10.0.3.1", type="router"))

    topo.add_link(Link(source="R1", destination="R2", latency=10.0))
    topo.add_link(Link(source="R2", destination="R3", latency=10.0))
    topo.add_link(Link(source="R1", destination="R3", latency=30.0))
    return topo
