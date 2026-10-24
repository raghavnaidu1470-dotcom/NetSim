"""Tests for network failure and resilience calculations (Member 2)."""

import pytest

from network.topology import Topology
from simulation.failures import calculate_recovery_time, trigger_node_failure


def test_calculate_recovery_time_formula() -> None:
    # Recovery Time = detection_delay + (recomputation_rounds * per_round_delay)
    # 150 + (4 * 50) = 350 ms
    rec_time = calculate_recovery_time(
        detection_delay_ms=150.0,
        recomputation_rounds=4,
        per_round_delay_ms=50.0,
    )
    assert rec_time == 350.0


def test_trigger_node_failure_rerouting(linear_topology: Topology) -> None:
    metrics = trigger_node_failure(
        linear_topology,
        node_id="R1",
        source="PC1",
        destination="PC2",
    )
    assert metrics["failure_target"] == "R1"
    assert metrics["total_recovery_time_ms"] > 0
    assert metrics["rerouted_path"] == []  # Since R1 was the only intermediate router
