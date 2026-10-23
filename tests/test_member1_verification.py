"""Verification tests for Member 1 deliverables (Ragghav Kamaraj).

Validates:
- DV result equals Dijkstra (latency metric) on static networks.
- Edge cases: source == destination, unknown node, inactive router, inactive link,
  disconnected network, all paths failed, equal-cost routes (deterministic tie-break),
  single valid path, 100% packet loss link, invalid IPv4, duplicate IPs.
- find_route schema with message, algorithm, and XAR stub handling.
- Topology JSON save/load round trip.
- RoutingTable pretty-print and link failure invalidation.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from network.devices import Link, Node, validate_ipv4, validate_ipv4_address
from network.distance_vector import distance_vector_routing, simulate_distance_vector_convergence
from network.link_state import link_state_dijkstra
from network.routing_table import RoutingTable, RoutingTableEntry, build_routing_table
from network.topology import Topology, enumerate_paths, find_route, get_path_metrics

TOPOLOGY_DIR = Path(__file__).resolve().parent.parent / "data" / "topologies"


def test_dv_equals_dijkstra_latency_static_network() -> None:
    """Item 3i: DV result equals Dijkstra (latency metric) on a static network."""
    topo_files = [
        "why_shortest_is_not_best.json",
        "router_failure.json",
        "traffic_profile_change.json",
    ]

    for topo_name in topo_files:
        topo = Topology.load_json(TOPOLOGY_DIR / topo_name)
        active_nodes = [nid for nid, node in topo.nodes.items() if node.active]

        # Test across host endpoints
        hosts = [nid for nid in active_nodes if topo.nodes[nid].type == "host"]
        for src in hosts:
            for dst in hosts:
                if src == dst:
                    continue
                dijkstra_res = link_state_dijkstra(topo, src, dst, metric="latency")
                dv_res = distance_vector_routing(topo, src, dst, metric="latency")

                assert dijkstra_res["status"] == dv_res["route"]["status"]
                if dijkstra_res["status"] == "success":
                    assert dijkstra_res["path"] == dv_res["route"]["path"], (
                        f"Mismatch in {topo_name} for {src}->{dst}: "
                        f"Dijkstra={dijkstra_res['path']} vs DV={dv_res['route']['path']}"
                    )
                    assert dijkstra_res["latency"] == dv_res["route"]["latency"]
                    assert dijkstra_res["hop_count"] == dv_res["route"]["hop_count"]


def test_find_route_schema_and_xar_stub() -> None:
    """Item 3a: find_route schema and clear XAR not implemented message."""
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")

    # Dijkstra
    res_dijkstra = find_route(topo, "PC1", "PC2", algorithm="dijkstra")
    assert res_dijkstra["status"] == "success"
    assert res_dijkstra["algorithm"] == "dijkstra"
    assert "message" in res_dijkstra and res_dijkstra["message"]
    assert res_dijkstra["hop_count"] == 4

    # Distance Vector
    res_dv = find_route(topo, "PC1", "PC2", algorithm="distance_vector")
    assert res_dv["status"] == "success"
    assert res_dv["algorithm"] == "distance_vector"
    assert "message" in res_dv and res_dv["message"]
    assert res_dv["hop_count"] == 4

    # XAR stub delegation
    res_xar = find_route(topo, "PC1", "PC2", algorithm="xar")
    assert res_xar["status"] == "invalid"
    assert res_xar["algorithm"] == "xar"
    assert res_xar["message"] == "XAR not implemented yet"
    assert res_xar["path"] == []


def test_edge_case_source_equals_destination() -> None:
    """Edge-case: source == destination."""
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    for algo in ("dijkstra", "distance_vector"):
        res = find_route(topo, "PC1", "PC1", algorithm=algo)
        assert res["status"] == "success"
        assert res["path"] == ["PC1"]
        assert res["hop_count"] == 0
        assert res["latency"] == 0.0
        assert "identical" in res["message"].lower()


def test_edge_case_unknown_node() -> None:
    """Edge-case: unknown node."""
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    res = find_route(topo, "UNKNOWN_SRC", "PC2", algorithm="dijkstra")
    assert res["status"] == "invalid"
    assert res["path"] == []
    assert "UNKNOWN_SRC" in res["message"]

    res_dv = find_route(topo, "PC1", "UNKNOWN_DST", algorithm="distance_vector")
    assert res_dv["status"] == "invalid"
    assert res_dv["path"] == []
    assert "UNKNOWN_DST" in res_dv["message"]


def test_edge_case_inactive_router() -> None:
    """Edge-case: inactive router."""
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    topo.set_node_active("R1", False)

    res = find_route(topo, "PC1", "PC2", algorithm="dijkstra")
    assert res["status"] == "no_route"
    assert res["path"] == []


def test_edge_case_inactive_link_and_all_paths_failed() -> None:
    """Edge-case: inactive link, all paths failed, disconnected network."""
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")

    # Sever link PC1 -> R1
    topo.set_link_active("PC1", "R1", False)
    res = find_route(topo, "PC1", "PC2", algorithm="dijkstra")
    assert res["status"] == "no_route"
    assert res["path"] == []

    res_dv = find_route(topo, "PC1", "PC2", algorithm="distance_vector")
    assert res_dv["status"] == "no_route"
    assert res_dv["path"] == []


def test_edge_case_equal_cost_routes_deterministic_tie_break() -> None:
    """Edge-case: equal-cost routes with deterministic tie-break."""
    topo = Topology("equal_cost_diamond")
    topo.add_node(Node(id="SRC", ip="10.0.0.1", type="router"))
    topo.add_node(Node(id="B_NODE", ip="10.0.0.2", type="router"))
    topo.add_node(Node(id="C_NODE", ip="10.0.0.3", type="router"))
    topo.add_node(Node(id="DST", ip="10.0.0.4", type="router"))

    # Both paths have identical latency (10 ms) and hops (2)
    topo.add_link(Link(source="SRC", destination="B_NODE", latency=5.0))
    topo.add_link(Link(source="B_NODE", destination="DST", latency=5.0))
    topo.add_link(Link(source="SRC", destination="C_NODE", latency=5.0))
    topo.add_link(Link(source="C_NODE", destination="DST", latency=5.0))

    # Run Dijkstra 10 times to verify absolute determinism
    for _ in range(10):
        res = link_state_dijkstra(topo, "SRC", "DST", metric="latency")
        assert res["status"] == "success"
        # Deterministic tie-breaker picks 'B_NODE' lexicographically over 'C_NODE'
        assert res["path"] == ["SRC", "B_NODE", "DST"]


def test_edge_case_single_valid_path() -> None:
    """Edge-case: single valid path."""
    topo = Topology("single_path")
    topo.add_node(Node(id="N1", ip="10.0.0.1", type="router"))
    topo.add_node(Node(id="N2", ip="10.0.0.2", type="router"))
    topo.add_link(Link(source="N1", destination="N2", latency=12.0))

    paths = topo.enumerate_paths("N1", "N2", max_hops=4)
    assert paths == [["N1", "N2"]]

    res = topo.find_route("N1", "N2", algorithm="dijkstra")
    assert res["status"] == "success"
    assert res["path"] == ["N1", "N2"]


def test_edge_case_100_percent_loss_link() -> None:
    """Edge-case: 100% packet loss link."""
    topo = Topology("lossy")
    topo.add_node(Node(id="A", ip="10.0.0.1", type="router"))
    topo.add_node(Node(id="B", ip="10.0.0.2", type="router"))
    topo.add_link(Link(source="A", destination="B", latency=5.0, packet_loss=1.0, reliability=0.0))

    metrics = topo.get_path_metrics(["A", "B"])
    assert metrics["packet_loss"] == 1.0
    assert metrics["reliability"] == 0.0


def test_edge_case_ipv4_validation_and_duplicate_ips() -> None:
    """Edge-case: IPv4 validation with clear messages and duplicate IP detection."""
    valid, msg = validate_ipv4_address("192.168.1.1")
    assert valid is True
    assert "Valid" in msg

    invalid, msg = validate_ipv4_address("999.0.0.1")
    assert invalid is False
    assert "Invalid" in msg

    empty, msg = validate_ipv4_address("")
    assert empty is False

    # Duplicate IP check in Topology.add_node
    topo = Topology("dup_check")
    topo.add_node(Node(id="R1", ip="192.168.1.1"))
    with pytest.raises(ValueError, match="Duplicate IPv4 address"):
        topo.add_node(Node(id="R2", ip="192.168.1.1"))


def test_topology_json_save_load_round_trip(tmp_path: Path) -> None:
    """Item 3g: Topology JSON load/save round trip."""
    orig_topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    out_file = tmp_path / "round_trip.json"
    orig_topo.save_json(out_file)

    loaded_topo = Topology.load_json(out_file)
    assert loaded_topo.name == orig_topo.name
    assert len(loaded_topo.nodes) == len(orig_topo.nodes)
    assert len(loaded_topo.links) == len(orig_topo.links)
    for nid, node in orig_topo.nodes.items():
        assert loaded_topo.nodes[nid].ip == node.ip
        assert loaded_topo.nodes[nid].type == node.type


def test_routing_table_link_invalidation_and_pretty_print() -> None:
    """Item 3e: Routing table link failure invalidation and pretty-print."""
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    table = build_routing_table(topo, "R1", algorithm="dijkstra")

    assert table.get_next_hop("PC2") == "R2"
    invalidated = table.invalidate_routes_via_link("R1", "R2")
    assert invalidated >= 1
    assert table.get_next_hop("PC2") is None

    table_str = table.pretty_print()
    assert "Routing Table for Node: R1" in table_str
    assert "Destination ID" in table_str
    assert "unreachable" in table_str
