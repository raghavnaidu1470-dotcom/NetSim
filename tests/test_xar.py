"""Tests for Explainable Adaptive Routing (XAR) path scoring (Member 2)."""

from pathlib import Path

import pytest

from adaptive.xar import evaluate_all_candidate_paths, xar_find_route
from network.topology import Topology

TOPOLOGY_DIR = Path(__file__).resolve().parent.parent / "data" / "topologies"


def test_evaluate_all_candidate_paths_demo1() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    evals = evaluate_all_candidate_paths(topo, "PC1", "PC2", profile="standard")
    assert len(evals) == 2
    # XAR optimal path should have the lowest score and be first
    assert evals[0]["path"] == ["PC1", "R1", "R3", "R4", "R5", "PC2"]
    assert evals[0]["score"] < evals[1]["score"]


def test_xar_find_route_selects_clean_path() -> None:
    topo = Topology.load_json(TOPOLOGY_DIR / "why_shortest_is_not_best.json")
    route = xar_find_route(topo, "PC1", "PC2", profile="standard")
    assert route["status"] == "success"
    # Although longer in hops (5 vs 4), XAR chooses R3->R4 because of lower latency and loss
    assert route["path"] == ["PC1", "R1", "R3", "R4", "R5", "PC2"]
