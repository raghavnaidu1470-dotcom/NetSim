"""Unit tests for routing table generation and failure updates (Member 1)."""

from network.devices import Link, Node
from network.routing_table import RoutingTable, build_routing_table
from network.topology import Topology


def test_build_routing_table() -> None:
    topo = Topology("rt_test")
    topo.add_node(Node(id="R1", ip="10.0.1.1", type="router"))
    topo.add_node(Node(id="R2", ip="10.0.2.1", type="router"))
    topo.add_node(Node(id="PC1", ip="10.0.3.10", type="host"))

    topo.add_link(Link(source="R1", destination="R2", latency=10.0))
    topo.add_link(Link(source="R2", destination="PC1", latency=5.0))

    rt = build_routing_table(topo, "R1", algorithm="dijkstra")
    assert rt.node_id == "R1"
    assert rt.get_next_hop("PC1") == "R2"
    assert rt.get_next_hop("R2") == "R2"


def test_invalidate_routes_via_node() -> None:
    topo = Topology("rt_fail")
    topo.add_node(Node(id="R1", ip="10.0.1.1", type="router"))
    topo.add_node(Node(id="R2", ip="10.0.2.1", type="router"))
    topo.add_node(Node(id="PC1", ip="10.0.3.10", type="host"))

    topo.add_link(Link(source="R1", destination="R2", latency=10.0))
    topo.add_link(Link(source="R2", destination="PC1", latency=5.0))

    rt = build_routing_table(topo, "R1")
    assert rt.get_next_hop("PC1") == "R2"

    invalidated = rt.invalidate_routes_via_node("R2")
    assert invalidated == 2  # Both R2 and PC1 routed via R2
    assert rt.get_next_hop("PC1") is None
