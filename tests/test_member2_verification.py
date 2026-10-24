"""Verification of Member 2's XAR, explanation and simulation modules against the specification.

Covers the worked example in docs/spec.md, the three traffic profiles, the demonstration
scenarios, failure and recovery behaviour, congestion and packet-loss simulation, and the
edge cases listed in docs/plan.md.
"""

from pathlib import Path

import pytest

from adaptive.explanation import compare_routes
from adaptive.metrics import aggregate_path_metrics, compute_path_score, normalize_metrics
from adaptive.traffic_profiles import TRAFFIC_PROFILES, get_profile_weights
from adaptive.xar import evaluate_all_candidate_paths, xar_find_route
from network.devices import Link, Node
from network.topology import Topology
from simulation.congestion import apply_burst_congestion, set_link_congestion
from simulation.failures import calculate_recovery_time, trigger_link_failure, trigger_node_failure
from simulation.packet_loss import simulate_packet_transmission

TOPOLOGY_DIR = Path(__file__).resolve().parent.parent / "data" / "topologies"
S1_SHORT = ["PC1", "R1", "R2", "R5", "PC2"]
S1_CLEAN = ["PC1", "R1", "R3", "R4", "R5", "PC2"]
S3_FAST = ["PC1", "R1", "R3", "R4", "PC2"]
S3_SAFE = ["PC1", "R1", "R2", "R4", "PC2"]


def load(name: str) -> Topology:
    return Topology.load_json(TOPOLOGY_DIR / f"{name}.json")


def build(links, hosts=("PC1", "PC2")) -> Topology:
    """Small helper: links is a list of (u, v, kwargs)."""
    topo = Topology("custom")
    names = {n for u, v, _ in links for n in (u, v)}
    for i, n in enumerate(sorted(names)):
        topo.add_node(Node(id=n, ip=f"10.0.0.{i + 1}", type="host" if n in hosts else "router"))
    for u, v, kw in links:
        topo.add_link(Link(source=u, destination=v, **kw))
    return topo


# ------------------------------------------------------------------ metrics: worked example
def test_worked_example_raw_normalised_and_scores() -> None:
    topo = load("why_shortest_is_not_best")
    weights = get_profile_weights("standard")

    raw_a = aggregate_path_metrics(topo, S1_SHORT)
    assert raw_a == {"latency": 79.0, "packet_loss": 0.1917, "reliability": 0.6547, "congestion": 0.82, "hop_count": 4}
    norm_a = normalize_metrics(raw_a)
    assert norm_a["H"] == pytest.approx(0.4) and norm_a["L"] == pytest.approx(0.395)
    assert norm_a["R_penalty"] == pytest.approx(0.3453)
    assert compute_path_score(norm_a, weights) == pytest.approx(0.4329, abs=1e-4)

    raw_b = aggregate_path_metrics(topo, S1_CLEAN)
    assert raw_b["latency"] == 36.0 and raw_b["congestion"] == 0.12 and raw_b["hop_count"] == 5
    assert compute_path_score(normalize_metrics(raw_b), weights) == pytest.approx(0.1801, abs=1e-4)


@pytest.mark.parametrize("name", ["why_shortest_is_not_best", "router_failure", "traffic_profile_change"])
def test_aggregate_matches_topology_path_metrics(name: str) -> None:
    topo = load(name)
    for path in topo.enumerate_paths("PC1", "PC2", 8):
        assert dict(aggregate_path_metrics(topo, path)) == topo.get_path_metrics(path)


def test_aggregate_edge_cases(linear_topology: Topology) -> None:
    assert aggregate_path_metrics(linear_topology, ["PC1"])["hop_count"] == 0
    assert aggregate_path_metrics(linear_topology, [])["reliability"] == 1.0
    with pytest.raises(ValueError):
        aggregate_path_metrics(linear_topology, ["PC1", "PC2"])  # no direct link


def test_normalisation_clamps_extremes() -> None:
    norm = normalize_metrics({"latency": 9999.0, "hop_count": 99, "congestion": 1.0, "packet_loss": 1.0, "reliability": 0.0})
    assert all(v == 1.0 for v in norm.values())
    best = normalize_metrics({"latency": 0.0, "hop_count": 0, "congestion": 0.0, "packet_loss": 0.0, "reliability": 1.0})
    assert all(v == 0.0 for v in best.values())


def test_profile_weights_sum_to_one_and_score_is_monotonic() -> None:
    for weights in TRAFFIC_PROFILES.values():
        assert weights.w_h + weights.w_l + weights.w_c + weights.w_p + weights.w_r == pytest.approx(1.0)
    base = {"H": 0.2, "L": 0.2, "C": 0.2, "P": 0.2, "R_penalty": 0.2}
    for key in base:
        worse = dict(base, **{key: 0.9})
        for weights in TRAFFIC_PROFILES.values():
            assert compute_path_score(worse, weights) > compute_path_score(base, weights)


# ------------------------------------------------------------------ XAR routing
def test_xar_beats_hop_count_dijkstra_on_demo_1_under_every_profile() -> None:
    topo = load("why_shortest_is_not_best")
    assert topo.find_route("PC1", "PC2", "dijkstra", "hop")["path"] == S1_SHORT
    for profile in TRAFFIC_PROFILES:
        assert xar_find_route(topo, "PC1", "PC2", profile=profile)["path"] == S1_CLEAN


def test_traffic_profile_steers_the_route_on_demo_3() -> None:
    topo = load("traffic_profile_change")
    assert xar_find_route(topo, "PC1", "PC2", profile="real_time")["path"] == S3_FAST
    assert xar_find_route(topo, "PC1", "PC2", profile="reliable_data_transfer")["path"] == S3_SAFE
    # The profile also reaches XAR through Topology.find_route
    assert topo.find_route("PC1", "PC2", "xar", profile="real_time")["path"] == S3_FAST
    assert topo.find_route("PC1", "PC2", "xar", profile="reliable_data_transfer")["path"] == S3_SAFE


def test_spec_scores_for_profile_demo() -> None:
    topo = load("traffic_profile_change")
    by_path = {tuple(e["path"]): e["score"] for e in evaluate_all_candidate_paths(topo, "PC1", "PC2", "real_time")}
    assert by_path[tuple(S3_FAST)] == pytest.approx(0.1458, abs=1e-4) and by_path[tuple(S3_SAFE)] == pytest.approx(0.2085, abs=1e-4)
    by_path = {tuple(e["path"]): e["score"] for e in evaluate_all_candidate_paths(topo, "PC1", "PC2", "reliable_data_transfer")}
    assert by_path[tuple(S3_SAFE)] == pytest.approx(0.0826, abs=1e-4) and by_path[tuple(S3_FAST)] == pytest.approx(0.1654, abs=1e-4)


def test_xar_does_not_artificially_win_when_routes_tie() -> None:
    """Scenario 2: the primary route is best on every criterion, so XAR must agree with Dijkstra."""
    topo = load("router_failure")
    assert xar_find_route(topo, "PC1", "PC2")["path"] == topo.find_route("PC1", "PC2", "dijkstra")["path"]


def test_evaluations_are_sorted_and_deterministic() -> None:
    topo = load("why_shortest_is_not_best")
    evals = evaluate_all_candidate_paths(topo, "PC1", "PC2")
    assert [e["score"] for e in evals] == sorted(e["score"] for e in evals)
    assert evals == evaluate_all_candidate_paths(topo, "PC1", "PC2")


def test_equal_score_ties_break_by_hops_then_latency() -> None:
    topo = build([("PC1", "R1", {}), ("R1", "PC2", {}), ("PC1", "R2", {}), ("R2", "PC2", {})])
    evals = evaluate_all_candidate_paths(topo, "PC1", "PC2")
    assert evals[0]["score"] == evals[1]["score"]
    assert evals[0]["path"] == ["PC1", "R1", "PC2"]  # lexicographic order decides a perfect tie


def test_xar_route_status_edge_cases(linear_topology: Topology) -> None:
    assert xar_find_route(linear_topology, "PC1", "NOPE")["status"] == "invalid"
    same = xar_find_route(linear_topology, "PC1", "PC1")
    assert same["path"] == ["PC1"] and same["hop_count"] == 0 and same["status"] == "success"
    linear_topology.set_node_active("R1", False)
    cut = xar_find_route(linear_topology, "PC1", "PC2")
    assert cut["status"] == "no_route" and cut["path"] == []
    assert evaluate_all_candidate_paths(linear_topology, "PC1", "PC2") == []
    linear_topology.set_node_active("R1", True)
    linear_topology.set_node_active("PC2", False)
    assert xar_find_route(linear_topology, "PC1", "PC2")["status"] == "no_route"
    ok = xar_find_route(Topology.load_json(TOPOLOGY_DIR / "router_failure.json"), "PC1", "PC2")
    assert ok["algorithm"] == "xar" and ok["message"] and ok["status"] == "success"


def test_single_valid_path_is_chosen_even_if_poor() -> None:
    topo = build([("PC1", "R1", {"latency": 190.0, "congestion": 0.99, "packet_loss": 0.4, "reliability": 0.5}), ("R1", "PC2", {"latency": 150.0})])
    route = xar_find_route(topo, "PC1", "PC2")
    assert route["status"] == "success" and route["path"] == ["PC1", "R1", "PC2"]


def test_xar_avoids_total_loss_and_saturated_links() -> None:
    bad_loss = build([("PC1", "R1", {}), ("R1", "PC2", {"packet_loss": 1.0}), ("PC1", "R2", {}), ("R2", "R3", {}), ("R3", "PC2", {})])
    assert xar_find_route(bad_loss, "PC1", "PC2")["path"] == ["PC1", "R2", "R3", "PC2"]
    saturated = build([("PC1", "R1", {}), ("R1", "PC2", {"congestion": 1.0}), ("PC1", "R2", {}), ("R2", "R3", {}), ("R3", "PC2", {})])
    assert xar_find_route(saturated, "PC1", "PC2")["path"] == ["PC1", "R2", "R3", "PC2"]


# ------------------------------------------------------------------ explanation
def test_explanation_matches_the_specified_format() -> None:
    topo = load("why_shortest_is_not_best")
    comp = compare_routes(topo, S1_CLEAN, S1_SHORT, profile="standard")
    assert comp["explanation_text"] == (
        "XAR selected PC1 -> R1 -> R3 -> R4 -> R5 -> PC2 because latency was 43.0 ms lower, "
        "congestion was 70.0% lower, and expected packet loss was 16.0% lower. Although the "
        "alternative had 1 fewer hop, its adaptive score was 0.43 vs 0.18 under the standard profile."
    )
    assert comp["selected_score"] == pytest.approx(0.1801, abs=1e-4) and comp["alternative_score"] == pytest.approx(0.4329, abs=1e-4)
    d = comp["deltas"]
    assert d["latency"] == 43.0 and d["congestion"] == pytest.approx(0.70) and d["packet_loss"] == pytest.approx(0.1601, abs=1e-4)
    assert d["hop_count"] == -1 and d["score"] == pytest.approx(0.2528, abs=1e-4)


def test_explanation_reports_trade_offs_and_profile_names() -> None:
    topo = load("traffic_profile_change")
    comp = compare_routes(topo, S3_FAST, S3_SAFE, profile="real_time")
    text = comp["explanation_text"]
    assert "latency was 52.0 ms lower" in text and "Trade-off:" in text and "expected packet loss was 14.2% higher" in text
    assert "real-time profile" in text
    assert "reliable data transfer profile" in compare_routes(topo, S3_SAFE, S3_FAST, "reliable_data_transfer")["explanation_text"]


def test_explanation_edge_cases(linear_topology: Topology) -> None:
    same = compare_routes(linear_topology, ["PC1", "R1", "PC2"], ["PC1", "R1", "PC2"])
    assert "no trade-off was needed" in same["explanation_text"]
    hypothetical = compare_routes(linear_topology, ["PC1", "R1", "PC2"], ["PC1", "PC2"])  # missing link: worst case
    assert hypothetical["deltas"]["latency"] > 0 and hypothetical["explanation_text"]
    shorter = compare_routes(load("why_shortest_is_not_best"), S1_SHORT, S1_CLEAN)
    assert "also has 1 fewer hop" in shorter["explanation_text"] and "Trade-off:" in shorter["explanation_text"]


# ------------------------------------------------------------------ failures and recovery
def test_router_failure_matches_the_specification_example() -> None:
    topo = load("router_failure")
    m = trigger_node_failure(topo, "R2", "PC1", "PC2")
    assert m["failure_target"] == "R2" and m["target_type"] == "node"
    assert m["original_path"] == ["PC1", "R1", "R2", "PC2"] and m["rerouted_path"] == ["PC1", "R1", "R3", "R4", "PC2"]
    assert m["extra_hops"] == 1 and m["latency_delta_ms"] == 30.0
    assert m["recomputation_rounds"] == 4 and m["total_recovery_time_ms"] == 350.0 and m["packets_dropped"] == 12
    assert topo.nodes["R2"].active is False  # the failure is applied to the topology passed in


def test_recovery_time_uses_the_given_timing_parameters() -> None:
    m = trigger_node_failure(load("router_failure"), "R2", "PC1", "PC2", detection_delay_ms=100.0, per_round_delay_ms=20.0)
    assert m["total_recovery_time_ms"] == calculate_recovery_time(100.0, m["recomputation_rounds"], 20.0)
    assert m["detection_delay_ms"] == 100.0 and m["per_round_delay_ms"] == 20.0


def test_link_failure_reroutes_and_names_the_link() -> None:
    topo = load("router_failure")
    m = trigger_link_failure(topo, "R1", "R2", "PC1", "PC2")
    assert m["failure_target"] == "R1-R2" and m["target_type"] == "link"
    assert m["rerouted_path"] == ["PC1", "R1", "R3", "R4", "PC2"] and m["extra_hops"] == 1
    assert topo.get_link("R1", "R2").active is False
    assert m["total_recovery_time_ms"] > 0


def test_failure_of_the_only_access_router_leaves_no_route() -> None:
    m = trigger_node_failure(load("router_failure"), "R1", "PC1", "PC2")
    assert m["original_path"] == ["PC1", "R1", "R2", "PC2"] and m["rerouted_path"] == []
    assert m["extra_hops"] == 0 and m["latency_delta_ms"] == 0.0 and m["packets_dropped"] > 0


def test_flow_that_never_used_the_failed_router_loses_nothing() -> None:
    """XAR's demo-1 route avoids R2, so failing R2 must not disturb it."""
    m = trigger_node_failure(load("why_shortest_is_not_best"), "R2", "PC1", "PC2", algorithm="xar")
    assert m["original_path"] == S1_CLEAN == m["rerouted_path"]
    assert m["packets_dropped"] == 0 and m["extra_hops"] == 0
    # ...whereas the hop-count route is forced onto the clean path
    h = trigger_node_failure(load("why_shortest_is_not_best"), "R2", "PC1", "PC2", algorithm="dijkstra")
    assert h["original_path"] == S1_SHORT and h["rerouted_path"] == S1_CLEAN and h["packets_dropped"] > 0


def test_failure_analysis_works_if_the_router_is_already_down() -> None:
    topo = load("router_failure")
    topo.set_node_active("R2", False)
    m = trigger_node_failure(topo, "R2", "PC1", "PC2")
    assert m["original_path"] == ["PC1", "R1", "R2", "PC2"] and m["rerouted_path"] == ["PC1", "R1", "R3", "R4", "PC2"]


@pytest.mark.parametrize("algorithm", ["xar", "dijkstra", "distance_vector"])
def test_failure_supports_every_routing_algorithm(algorithm: str) -> None:
    m = trigger_node_failure(load("router_failure"), "R2", "PC1", "PC2", algorithm=algorithm)
    assert m["rerouted_path"] == ["PC1", "R1", "R3", "R4", "PC2"]


def test_failure_rejects_unknown_targets(linear_topology: Topology) -> None:
    with pytest.raises(ValueError):
        trigger_node_failure(linear_topology, "NOPE", "PC1", "PC2")
    with pytest.raises(ValueError):
        trigger_link_failure(linear_topology, "PC1", "PC2", "PC1", "PC2")


# ------------------------------------------------------------------ congestion
def test_congestion_validation_and_clamping(linear_topology: Topology) -> None:
    with pytest.raises(ValueError):
        set_link_congestion(linear_topology, "PC1", "R1", 1.5)
    with pytest.raises(ValueError):
        set_link_congestion(linear_topology, "PC1", "R1", -0.1)
    assert set_link_congestion(linear_topology, "PC1", "NOPE", 0.5) is False
    assert apply_burst_congestion(linear_topology, "R1", "PC2", multiplier=10.0) == 1.0
    with pytest.raises(ValueError):
        apply_burst_congestion(linear_topology, "R1", "PC2", multiplier=-1.0)
    with pytest.raises(ValueError):
        apply_burst_congestion(linear_topology, "PC1", "PC2")


def test_burst_on_an_idle_link_starts_from_a_floor() -> None:
    topo = build([("PC1", "R1", {"congestion": 0.0}), ("R1", "PC2", {})])
    assert apply_burst_congestion(topo, "PC1", "R1", multiplier=2.0) == pytest.approx(0.2)
    assert topo.get_link("PC1", "R1").congestion == pytest.approx(0.2)


def test_congestion_raises_the_xar_score_of_a_path() -> None:
    topo = load("why_shortest_is_not_best")
    before = evaluate_all_candidate_paths(topo, "PC1", "PC2")[0]["score"]
    set_link_congestion(topo, "R3", "R4", 0.95)
    after = {tuple(e["path"]): e["score"] for e in evaluate_all_candidate_paths(topo, "PC1", "PC2")}[tuple(S1_CLEAN)]
    assert after > before


# ------------------------------------------------------------------ packet loss simulation
def test_packet_simulation_is_seeded_and_consistent() -> None:
    topo = load("why_shortest_is_not_best")
    a = simulate_packet_transmission(topo, S1_SHORT, 500, seed=1)
    assert a == simulate_packet_transmission(topo, S1_SHORT, 500, seed=1)
    assert a["packets_delivered"] + a["packets_dropped"] == a["packets_sent"] == 500
    assert a["retransmissions"] == a["packets_dropped"] > 0
    assert a["delivery_ratio"] == pytest.approx(a["packets_delivered"] / 500, abs=1e-4)


def test_packet_simulation_tracks_the_path_loss_probability() -> None:
    topo = load("why_shortest_is_not_best")
    res = simulate_packet_transmission(topo, S1_SHORT, 20000, seed=7)
    assert res["delivery_ratio"] == pytest.approx(1.0 - 0.1917, abs=0.02)
    clean = simulate_packet_transmission(topo, S1_CLEAN, 20000, seed=7)
    assert clean["delivery_ratio"] > res["delivery_ratio"]


def test_packet_simulation_edge_cases(linear_topology: Topology) -> None:
    zero = simulate_packet_transmission(linear_topology, ["PC1", "R1", "PC2"], 0)
    assert zero["packets_sent"] == 0 and zero["delivery_ratio"] == 1.0
    assert simulate_packet_transmission(linear_topology, ["PC1", "R1", "PC2"], 50)["packets_dropped"] == 0
    assert simulate_packet_transmission(linear_topology, [], 10)["packets_delivered"] == 0
    assert simulate_packet_transmission(linear_topology, ["PC1"], 10)["packets_delivered"] == 10
    with pytest.raises(ValueError):
        simulate_packet_transmission(linear_topology, ["PC1", "R1", "PC2"], -1)
    with pytest.raises(ValueError):
        simulate_packet_transmission(linear_topology, ["PC1", "PC2"], 10)
    dead = build([("PC1", "R1", {"packet_loss": 1.0}), ("R1", "PC2", {})])
    assert simulate_packet_transmission(dead, ["PC1", "R1", "PC2"], 100)["packets_delivered"] == 0


def test_throughput_falls_with_congestion() -> None:
    topo = build([("PC1", "R1", {"bandwidth": 100.0, "congestion": 0.0}), ("R1", "PC2", {"bandwidth": 100.0, "congestion": 0.0})])
    free = simulate_packet_transmission(topo, ["PC1", "R1", "PC2"], 100)["effective_throughput_mbps"]
    set_link_congestion(topo, "R1", "PC2", 0.75)
    busy = simulate_packet_transmission(topo, ["PC1", "R1", "PC2"], 100)["effective_throughput_mbps"]
    assert free == 100.0 and busy == 25.0
