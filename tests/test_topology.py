"""Unit tests for Topology management, JSON loading, and path enumeration (Member 1 - Ragghav Kamaraj)."""

from pathlib import Path

import pytest

from network.devices import Link, Node
from network.topology import Topology

TOPOLOGY_DIR = Path(__file__).resolve().parent.parent / "data" / "topologies"


def test_load_why_shortest_is_not_best_topology() -> None:
    topo_path = TOPOLOGY_DIR / "why_shortest_is_not_best.json"
    assert topo_path.is_file()

    topo = Topology.load_json(topo_path)
    assert len(topo.nodes) == 7
    assert len(topo.links) == 7
    assert topo.get_node("PC1") is not None
    assert topo.get_node("PC2") is not None
    assert topo.get_node("R1").type == "router"


def test_load_all_demo_topologies() -> None:
    for name in ["why_shortest_is_not_best.json", "router_failure.json", "traffic_profile_change.json"]:
        p = TOPOLOGY_DIR / name
        assert p.is_file()
        topo = Topology.load_json(p)
        assert len(topo.nodes) >= 6
        assert len(topo.links) >= 5


def test_topology_to_networkx() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    G = topo.to_networkx(only_active=True)
    assert len(G.nodes) == 7
    assert len(G.edges) == 7

    # Deactivate one node and check NetworkX representation
    topo.set_node_active("R2", False)
    G_after = topo.to_networkx(only_active=True)
    assert "R2" not in G_after
    assert len(G_after.nodes) == 6


def test_enumerate_paths() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    paths = topo.enumerate_paths("PC1", "PC2", max_hops=8)
    assert len(paths) == 2

    path_4hop = ["PC1", "R1", "R2", "R5", "PC2"]
    path_5hop = ["PC1", "R1", "R3", "R4", "R5", "PC2"]

    assert path_4hop in paths
    assert path_5hop in paths


def test_enumerate_paths_source_equals_dest() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    paths = topo.enumerate_paths("PC1", "PC1")
    assert paths == [["PC1"]]


def test_enumerate_paths_disconnected_or_invalid() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    assert topo.enumerate_paths("INVALID_1", "PC2") == []
    assert topo.enumerate_paths("PC1", "INVALID_2") == []

    # Disconnect destination
    topo.set_node_active("PC2", False)
    assert topo.enumerate_paths("PC1", "PC2") == []


def test_path_metrics_aggregation() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    path = ["PC1", "R1", "R3", "R4", "R5", "PC2"]
    metrics = topo.get_path_metrics(path)

    # 2 + 10 + 12 + 10 + 2 = 36 ms
    assert metrics["latency"] == 36.0
    assert metrics["hop_count"] == 5
    assert metrics["congestion"] == 0.12
    assert 0.0 <= metrics["packet_loss"] <= 1.0
    assert 0.0 <= metrics["reliability"] <= 1.0


def test_find_route_dijkstra_baseline() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    res = topo.find_route("PC1", "PC2", algorithm="dijkstra")
    assert res["status"] == "success"
    # Dijkstra hop count picks the 4-hop path
    assert res["path"] == ["PC1", "R1", "R2", "R5", "PC2"]
    assert res["hop_count"] == 4
    assert res["latency"] == 79.0


def test_find_route_invalid_and_disconnected() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    res_inv = topo.find_route("NOT_EXIST", "PC2", algorithm="dijkstra")
    assert res_inv["status"] == "invalid"
    assert res_inv["path"] == []

    # Cut off PC2 by severing link
    topo.set_link_active("R5", "PC2", False)
    res_no = topo.find_route("PC1", "PC2", algorithm="dijkstra")
    assert res_no["status"] == "no_route"
    assert res_no["path"] == []
