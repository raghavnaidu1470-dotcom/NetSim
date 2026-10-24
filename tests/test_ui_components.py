"""Tests for UI drawing, pure-logic components, and dashboard benchmarks (Member 3)."""

from __future__ import annotations

import copy
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from network.topology import Topology
from ui.controls import compute_recovery_time_fallback
from ui.dashboard import build_comparison_benchmark
from ui.topology_view import draw_topology_graph
from ui.xar_adapter import (
    FALLBACK_ALGO_LABEL,
    FALLBACK_BADGE_TEXT,
    generate_xar_explanation,
    resolve_xar_route,
    score_path_by_spec,
)

TOPOLOGIES_DIR = Path(__file__).resolve().parent.parent / "data" / "topologies"


def test_draw_topology_graph_returns_figure(linear_topology: Topology) -> None:
    """Verifies draw_topology_graph produces a valid Matplotlib Figure."""
    fig = draw_topology_graph(linear_topology, highlighted_path=["PC1", "R1", "PC2"])
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_draw_topology_graph_with_inactive_elements(triangle_topology: Topology) -> None:
    """Verifies graph rendering handles inactive nodes and links gracefully."""
    triangle_topology.set_node_active("R2", False)
    triangle_topology.set_link_active("R1", "R3", False)
    fig = draw_topology_graph(triangle_topology, highlighted_path=None, title="Test Inactive")
    assert isinstance(fig, plt.Figure)
    plt.close(fig)


def test_xar_adapter_uses_real_engine() -> None:
    """With Member 2's engine merged, the adapter returns its result and no reference-preview badge is needed."""
    topo = Topology.load_json(TOPOLOGIES_DIR / "why_shortest_is_not_best.json")
    route, metrics, score, is_fallback = resolve_xar_route(topo, "PC1", "PC2", profile="standard")

    assert is_fallback is False
    assert route["status"] == "success"
    assert route["algorithm"] == "xar"
    # In Demo 1, XAR must select Route B (PC1 -> R1 -> R3 -> R4 -> R5 -> PC2)
    assert route["path"] == ["PC1", "R1", "R3", "R4", "R5", "PC2"]
    assert route["hop_count"] == 5
    assert route["latency"] == 36.0
    assert 0.17 <= score <= 0.19


def test_xar_adapter_fallback_and_badge(monkeypatch) -> None:
    """If the engine is unavailable the adapter falls back to spec scoring and flags the reference preview."""
    import adaptive.xar

    def unavailable(*args, **kwargs):
        raise NotImplementedError("engine not available")

    monkeypatch.setattr(adaptive.xar, "xar_find_route", unavailable)
    topo = Topology.load_json(TOPOLOGIES_DIR / "why_shortest_is_not_best.json")
    route, metrics, score, is_fallback = resolve_xar_route(topo, "PC1", "PC2", profile="standard")

    assert is_fallback is True
    assert route["status"] == "success"
    assert route["path"] == ["PC1", "R1", "R3", "R4", "R5", "PC2"]
    assert route["hop_count"] == 5
    assert route["latency"] == 36.0
    assert 0.17 <= score <= 0.19
    assert FALLBACK_BADGE_TEXT == "Reference preview"


def test_xar_adapter_explanation_generation() -> None:
    """The real explanation engine states the metric deltas and the hop trade-off."""
    topo = Topology.load_json(TOPOLOGIES_DIR / "why_shortest_is_not_best.json")
    sel_path = ["PC1", "R1", "R3", "R4", "R5", "PC2"]
    alt_path = ["PC1", "R1", "R2", "R5", "PC2"]

    explanation, is_fallback = generate_xar_explanation(topo, sel_path, alt_path, profile="standard")
    assert is_fallback is False
    assert "latency was 43.0 ms lower" in explanation
    assert "congestion was 70.0% lower" in explanation
    assert "expected packet loss was 16.0% lower" in explanation
    assert "1 fewer hop" in explanation


def test_xar_adapter_explanation_fallback(monkeypatch) -> None:
    """If the explanation engine is unavailable the adapter still produces a delta justification."""
    import adaptive.explanation

    def unavailable(*args, **kwargs):
        raise NotImplementedError("engine not available")

    monkeypatch.setattr(adaptive.explanation, "compare_routes", unavailable)
    topo = Topology.load_json(TOPOLOGIES_DIR / "why_shortest_is_not_best.json")
    explanation, is_fallback = generate_xar_explanation(
        topo, ["PC1", "R1", "R3", "R4", "R5", "PC2"], ["PC1", "R1", "R2", "R5", "PC2"], profile="standard"
    )
    assert is_fallback is True
    assert "latency is 43.0 ms lower" in explanation
    assert "bottleneck congestion is 70% lower" in explanation
    assert "superior penalty score" in explanation


def test_disruption_recovery_time_formula() -> None:
    """Formula: Recovery Time = detection_delay + (recomputation_rounds * per_round_delay)."""
    # 150 + (4 * 50) = 350.0 ms
    rec_time, origin = compute_recovery_time_fallback(
        detection_delay_ms=150.0,
        recomputation_rounds=4,
        per_round_delay_ms=50.0,
    )
    assert rec_time == 350.0
    assert "spec formula" in origin or "failures" in origin

    # 100 + (2 * 25) = 150.0 ms
    rec_time2, _ = compute_recovery_time_fallback(
        detection_delay_ms=100.0,
        recomputation_rounds=2,
        per_round_delay_ms=25.0,
    )
    assert rec_time2 == 150.0


def test_disruption_before_after_comparison() -> None:
    """Verify before-and-after failure rerouting behavior on router_failure.json."""
    topo = Topology.load_json(TOPOLOGIES_DIR / "router_failure.json")
    original_topo = copy.deepcopy(topo)

    # Baseline route
    prev_route = original_topo.find_route("PC1", "PC2", algorithm="dijkstra", metric="hop")
    assert prev_route["status"] == "success"
    assert prev_route["path"] == ["PC1", "R1", "R2", "PC2"]

    # Deactivate R2
    topo.set_node_active("R2", False)
    new_route = topo.find_route("PC1", "PC2", algorithm="dijkstra", metric="hop")
    assert new_route["status"] == "success"
    # Detour must bypass R2 via R3 -> R4
    assert new_route["path"] == ["PC1", "R1", "R3", "R4", "PC2"]
    assert new_route["hop_count"] == prev_route["hop_count"] + 1


def test_comparison_table_builder_on_all_demo_topologies() -> None:
    """Benchmark builder must execute and populate valid rows across all 3 demo scenarios."""
    demo_files = [
        "why_shortest_is_not_best.json",
        "router_failure.json",
        "traffic_profile_change.json",
    ]

    for filename in demo_files:
        filepath = TOPOLOGIES_DIR / filename
        assert filepath.is_file(), f"Missing required scenario: {filename}"
        topo = Topology.load_json(filepath)

        rows, meta = build_comparison_benchmark(topo, "PC1", "PC2", traffic_profile="standard")
        assert len(rows) == 4  # Dijkstra Hop, Dijkstra Latency, Distance Vector, XAR
        algo_names = [r["Algorithm"] for r in rows]

        assert any("Dijkstra (Hop Count)" in a for a in algo_names)
        assert any("Dijkstra (Latency)" in a for a in algo_names)
        assert any("Distance Vector" in a for a in algo_names)
        assert any("XAR" in a for a in algo_names)

        for r in rows:
            assert r["Hop Count"] > 0
            assert r["Latency (ms)"] > 0.0
            assert 0.0 <= r["Adaptive Score"] <= 1.0


def test_streamlit_app_smoke_test_with_apptest() -> None:
    """Smoke test that ui/app.py initializes and executes without unhandled exceptions across scenarios."""
    from streamlit.testing.v1 import AppTest

    demo_scenarios = [
        "why_shortest_is_not_best",
        "router_failure",
        "traffic_profile_change",
    ]

    app_file = str(Path(__file__).resolve().parent.parent / "ui" / "app.py")

    for scenario_name in demo_scenarios:
        at = AppTest.from_file(app_file, default_timeout=15)
        at.run()
        assert not at.exception, f"AppTest raised an unhandled exception on initial run: {at.exception}"
        # Select scenario in sidebar and rerun
        if at.sidebar.selectbox:
            at.sidebar.selectbox[0].select(scenario_name)
            at.run()
            assert not at.exception, f"AppTest raised an unhandled exception on {scenario_name}: {at.exception}"

    # Custom uploaded JSON scenario test
    custom_data = {
        "name": "custom_mesh",
        "nodes": [
            {"id": "PC1", "ip": "10.0.0.1", "type": "host", "active": True},
            {"id": "R1", "ip": "10.0.0.2", "type": "router", "active": True},
            {"id": "PC2", "ip": "10.0.0.3", "type": "host", "active": True},
        ],
        "links": [
            {"source": "PC1", "destination": "R1", "latency": 5.0, "congestion": 0.1, "packet_loss": 0.01, "reliability": 0.99, "bandwidth": 100.0, "active": True},
            {"source": "R1", "destination": "PC2", "latency": 10.0, "congestion": 0.1, "packet_loss": 0.01, "reliability": 0.99, "bandwidth": 100.0, "active": True},
        ],
    }
    custom_topo = Topology.from_dict(custom_data)
    at_custom = AppTest.from_file(app_file, default_timeout=15)
    at_custom.run()
    at_custom.session_state["authoritative_topology"] = custom_topo
    at_custom.session_state["original_baseline_topology"] = custom_topo
    at_custom.session_state["selected_scenario_name"] = "custom_upload"
    at_custom.run()
    assert not at_custom.exception, f"AppTest raised an exception on custom upload: {at_custom.exception}"
