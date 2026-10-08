"""Simulation package for NetSim-X (Member 2).

Includes network disruptions, failure recovery calculations, congestion injections,
and packet loss simulations.
"""

from simulation.congestion import apply_burst_congestion, set_link_congestion
from simulation.failures import (
    RecoveryMetrics,
    calculate_recovery_time,
    trigger_link_failure,
    trigger_node_failure,
)
from simulation.packet_loss import PacketSimulationResult, simulate_packet_transmission

__all__ = [
    "RecoveryMetrics",
    "calculate_recovery_time",
    "trigger_node_failure",
    "trigger_link_failure",
    "set_link_congestion",
    "apply_burst_congestion",
    "PacketSimulationResult",
    "simulate_packet_transmission",
]
