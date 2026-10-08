"""Unit tests for round-by-round Distance Vector routing (Member 1 - Ragghav Kamaraj)."""

from network.devices import Link, Node
from network.distance_vector import distance_vector_routing, simulate_distance_vector_convergence
from network.topology import Topology


def test_distance_vector_convergence_rounds() -> None:
    topo = Topology("dv_chain")
    topo.add_node(Node(id="A", ip="10.0.0.1", type="router"))
    topo.add_node(Node(id="B", ip="10.0.0.2", type="router"))
    topo.add_node(Node(id="C", ip="10.0.0.3", type="router"))
    topo.add_node(Node(id="D", ip="10.0.0.4", type="router"))

    topo.add_link(Link(source="A", destination="B", latency=5.0))
    topo.add_link(Link(source="B", destination="C", latency=5.0))
    topo.add_link(Link(source="C", destination="D", latency=5.0))

    tables, rounds, converged = simulate_distance_vector_convergence(topo, metric="hop")
    assert converged is True
    assert rounds >= 2  # Takes multiple rounds to propagate across 3 hops
    assert tables["A"]["D"]["cost"] == 3.0
    assert tables["A"]["D"]["next_hop"] == "B"


def test_distance_vector_find_route() -> None:
    topo = Topology("dv_test")
    topo.add_node(Node(id="A", ip="10.0.0.1", type="router"))
    topo.add_node(Node(id="B", ip="10.0.0.2", type="router"))
    topo.add_node(Node(id="C", ip="10.0.0.3", type="router"))

    topo.add_link(Link(source="A", destination="B", latency=5.0))
    topo.add_link(Link(source="B", destination="C", latency=5.0))

    res = distance_vector_routing(topo, "A", "C")
    assert res["converged"] is True
    assert res["route"]["status"] == "success"
    assert res["route"]["path"] == ["A", "B", "C"]
    assert res["route"]["hop_count"] == 2
    assert res["convergence_rounds"] >= 1


def test_distance_vector_disconnected() -> None:
    topo = Topology("dv_disconn")
    topo.add_node(Node(id="A", ip="10.0.0.1", type="router"))
    topo.add_node(Node(id="B", ip="10.0.0.2", type="router"))
    # No link between A and B
    res = distance_vector_routing(topo, "A", "B")
    assert res["route"]["status"] == "no_route"
    assert res["route"]["path"] == []
