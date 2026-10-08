"""Unit tests for Link State / Dijkstra routing algorithm (Member 1 - Ragghav Kamaraj)."""

from network.devices import Link, Node
from network.link_state import compute_all_shortest_paths_from_source, link_state_dijkstra
from network.topology import Topology


def test_link_state_basic_triangle() -> None:
    topo = Topology("triangle")
    topo.add_node(Node(id="A", ip="10.0.0.1", type="router"))
    topo.add_node(Node(id="B", ip="10.0.0.2", type="router"))
    topo.add_node(Node(id="C", ip="10.0.0.3", type="router"))

    topo.add_link(Link(source="A", destination="B", latency=5.0))
    topo.add_link(Link(source="B", destination="C", latency=5.0))
    topo.add_link(Link(source="A", destination="C", latency=20.0))

    # Metric = hop: A -> C directly is 1 hop vs 2 hops
    res_hop = link_state_dijkstra(topo, "A", "C", metric="hop")
    assert res_hop["status"] == "success"
    assert res_hop["path"] == ["A", "C"]
    assert res_hop["hop_count"] == 1

    # Metric = latency: A -> B -> C is 10ms vs 20ms
    res_lat = link_state_dijkstra(topo, "A", "C", metric="latency")
    assert res_lat["status"] == "success"
    assert res_lat["path"] == ["A", "B", "C"]
    assert res_lat["latency"] == 10.0


def test_link_state_source_is_destination() -> None:
    topo = Topology("single")
    topo.add_node(Node(id="A", ip="10.0.0.1", type="router"))
    res = link_state_dijkstra(topo, "A", "A")
    assert res["status"] == "success"
    assert res["path"] == ["A"]
    assert res["hop_count"] == 0


def test_compute_all_shortest_paths_from_source() -> None:
    topo = Topology("tree")
    topo.add_node(Node(id="R1", ip="10.0.1.1", type="router"))
    topo.add_node(Node(id="R2", ip="10.0.2.1", type="router"))
    topo.add_node(Node(id="R3", ip="10.0.3.1", type="router"))

    topo.add_link(Link(source="R1", destination="R2", latency=10.0))
    topo.add_link(Link(source="R2", destination="R3", latency=10.0))

    all_paths = compute_all_shortest_paths_from_source(topo, "R1")
    assert all_paths["R1"] == ["R1"]
    assert all_paths["R2"] == ["R1", "R2"]
    assert all_paths["R3"] == ["R1", "R2", "R3"]


def test_dijkstra_why_shortest_is_not_best_hop_vs_latency() -> None:
    """Asserts Dijkstra behavior and aggregated metrics on why_shortest_is_not_best.json.

    Hop-metric Dijkstra must select the 4-hop R2 route despite high congestion & loss.
    Latency-metric Dijkstra selects the clean 5-hop R3-R4 route.
    Aggregated metrics for both candidate paths must match values documented in README.
    """
    from pathlib import Path

    topo_path = Path(__file__).parent.parent / "data" / "topologies" / "why_shortest_is_not_best.json"
    topo = Topology.load_json(str(topo_path))

    # Hop-metric Dijkstra returns the R2 route
    res_hop = link_state_dijkstra(topo, "PC1", "PC2", metric="hop")
    assert res_hop["status"] == "success"
    assert res_hop["path"] == ["PC1", "R1", "R2", "R5", "PC2"]
    assert res_hop["hop_count"] == 4

    # Latency-metric Dijkstra returns the cleaner R3-R4 route
    res_lat = link_state_dijkstra(topo, "PC1", "PC2", metric="latency")
    assert res_lat["status"] == "success"
    assert res_lat["path"] == ["PC1", "R1", "R3", "R4", "R5", "PC2"]
    assert res_lat["hop_count"] == 5

    # Aggregated metrics for R2 route (README: 79.0 ms, 82% congestion, 19.17% loss)
    m_r2 = topo.get_path_metrics(res_hop["path"])
    assert m_r2["latency"] == 79.0
    assert m_r2["congestion"] == 0.82
    assert m_r2["packet_loss"] == 0.1917
    assert m_r2["hop_count"] == 4

    # Aggregated metrics for R3-R4 route (README: 36.0 ms, 12% congestion, 3.16% loss)
    m_r3 = topo.get_path_metrics(res_lat["path"])
    assert m_r3["latency"] == 36.0
    assert m_r3["congestion"] == 0.12
    assert m_r3["packet_loss"] == 0.0316
    assert m_r3["hop_count"] == 5
