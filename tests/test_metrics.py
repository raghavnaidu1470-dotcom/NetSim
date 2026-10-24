"""Tests for metric aggregation, normalization, and scoring math (Member 2)."""

import pytest

from adaptive.metrics import (
    MAX_HOPS_CEILING,
    MAX_LATENCY_CEILING,
    aggregate_path_metrics,
    compute_path_score,
    normalize_metrics,
)
from adaptive.traffic_profiles import get_profile_weights
from network.topology import Topology


def test_aggregate_path_metrics_calculation(linear_topology: Topology) -> None:
    metrics = aggregate_path_metrics(linear_topology, ["PC1", "R1", "PC2"])
    assert metrics["latency"] == 15.0
    assert metrics["hop_count"] == 2
    assert metrics["congestion"] == 0.2


def test_normalize_metrics_bounds() -> None:
    raw = {
        "latency": 50.0,
        "hop_count": 3,
        "congestion": 0.4,
        "packet_loss": 0.05,
        "reliability": 0.95,
    }
    norm = normalize_metrics(raw)
    assert norm["L"] == pytest.approx(50.0 / MAX_LATENCY_CEILING)
    assert norm["H"] == pytest.approx(3.0 / MAX_HOPS_CEILING)
    assert norm["C"] == pytest.approx(0.4)
    assert norm["P"] == pytest.approx(0.05)
    assert norm["R_penalty"] == pytest.approx(0.05)


def test_compute_path_score() -> None:
    norm = {
        "H": 0.3,
        "L": 0.25,
        "C": 0.1,
        "P": 0.05,
        "R_penalty": 0.05,
    }
    weights = get_profile_weights("standard")
    score = compute_path_score(norm, weights)
    assert 0.0 <= score <= 1.0
