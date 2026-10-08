"""Tests for packet transmission and drop simulation (Member 2)."""

import pytest

from network.topology import Topology
from simulation.packet_loss import simulate_packet_transmission


@pytest.mark.skip(reason="Member 2 to implement simulate_packet_transmission")
def test_simulate_packet_transmission_zero_loss(linear_topology: Topology) -> None:
    res = simulate_packet_transmission(linear_topology, ["PC1", "R1", "PC2"], num_packets=100)
    assert res["packets_sent"] == 100
    assert res["packets_delivered"] + res["packets_dropped"] == 100
    assert 0.0 <= res["delivery_ratio"] <= 1.0
