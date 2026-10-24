"""Pytest asserting that scripts/verify_demos.py calculations match README.md."""

from __future__ import annotations

from pathlib import Path

from scripts.verify_demos import compute_demo_verifications

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_verify_demos_numbers_match_readme() -> None:
    """Assert that the numbers computed by verify_demos.py match README demo section."""
    data = compute_demo_verifications()
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    # 1. why_shortest_is_not_best
    d1 = data["why_shortest_is_not_best"]
    hop_m = d1["dijkstra_hop"]["metrics"]
    lat_m = d1["dijkstra_latency"]["metrics"]

    assert d1["dijkstra_hop"]["path"] == ["PC1", "R1", "R2", "R5", "PC2"]
    assert hop_m["hop_count"] == 4
    assert hop_m["latency"] == 79.0
    assert round(hop_m["congestion"] * 100, 1) == 82.0
    assert round(hop_m["packet_loss"] * 100, 2) == 19.17
    assert round(hop_m["reliability"] * 100, 2) == 65.47

    assert d1["dijkstra_latency"]["path"] == ["PC1", "R1", "R3", "R4", "R5", "PC2"]
    assert lat_m["hop_count"] == 5
    assert lat_m["latency"] == 36.0
    assert round(lat_m["congestion"] * 100, 1) == 12.0
    assert round(lat_m["packet_loss"] * 100, 2) == 3.16
    assert round(lat_m["reliability"] * 100, 2) == 96.84

    # Assert strings appear in README
    assert "79.0 ms latency, 82.0% congestion, 19.17% packet loss, 65.47% reliability" in readme_text
    assert "36.0 ms latency, 12.0% congestion, 3.16% packet loss, 96.84% reliability" in readme_text

    # 2. router_failure
    d2 = data["router_failure"]
    pre_m = d2["pre_failure"]["dijkstra_hop"]["metrics"]
    post_m = d2["post_failure"]["dijkstra_hop"]["metrics"]

    assert d2["pre_failure"]["dijkstra_hop"]["path"] == ["PC1", "R1", "R2", "PC2"]
    assert pre_m["hop_count"] == 3
    assert pre_m["latency"] == 14.0
    assert round(pre_m["congestion"] * 100, 1) == 10.0
    assert round(pre_m["packet_loss"] * 100, 2) == 0.70
    assert round(pre_m["reliability"] * 100, 2) == 98.80

    assert d2["post_failure"]["dijkstra_hop"]["path"] == ["PC1", "R1", "R3", "R4", "PC2"]
    assert post_m["hop_count"] == 4
    assert post_m["latency"] == 44.0
    assert round(post_m["congestion"] * 100, 1) == 15.0
    assert round(post_m["packet_loss"] * 100, 2) == 2.58
    assert round(post_m["reliability"] * 100, 2) == 94.98

    assert "14.0 ms latency, 10.0% congestion, 0.70% packet loss, 98.80% reliability" in readme_text
    assert "44.0 ms latency, 15.0% congestion, 2.58% packet loss, 94.98% reliability" in readme_text

    # 3. traffic_profile_change
    d3 = data["traffic_profile_change"]
    cand_a_m = d3["dijkstra_latency"]["metrics"]
    cand_b_m = d3["dijkstra_hop"]["metrics"]

    assert d3["dijkstra_latency"]["path"] == ["PC1", "R1", "R3", "R4", "PC2"]
    assert cand_a_m["hop_count"] == 4
    assert cand_a_m["latency"] == 17.0
    assert round(cand_a_m["congestion"] * 100, 1) == 14.0
    assert round(cand_a_m["packet_loss"] * 100, 2) == 14.61
    assert round(cand_a_m["reliability"] * 100, 2) == 79.94

    assert d3["dijkstra_hop"]["path"] == ["PC1", "R1", "R2", "R4", "PC2"]
    assert cand_b_m["hop_count"] == 4
    assert cand_b_m["latency"] == 69.0
    assert round(cand_b_m["congestion"] * 100, 1) == 8.0
    assert round(cand_b_m["packet_loss"] * 100, 2) == 0.40
    assert round(cand_b_m["reliability"] * 100, 2) == 99.60

    assert "17.0 ms latency, 14.0% congestion, 14.61% packet loss, 79.94% reliability" in readme_text
    assert "69.0 ms latency, 8.0% congestion, 0.40% packet loss, 99.60% reliability" in readme_text
