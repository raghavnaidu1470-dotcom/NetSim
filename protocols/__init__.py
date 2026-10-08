"""Protocols demonstration package for NetSim-X (Member 3).

Includes transport-layer TCP/UDP comparisons and CRC error detection demos.
"""

from protocols.crc import CRCDemoResult, compute_crc, run_crc_demo, verify_crc
from protocols.tcp_udp import (
    TCPSimulationSummary,
    UDPSimulationSummary,
    simulate_tcp_stream,
    simulate_udp_stream,
)

__all__ = [
    "TCPSimulationSummary",
    "UDPSimulationSummary",
    "simulate_tcp_stream",
    "simulate_udp_stream",
    "CRCDemoResult",
    "compute_crc",
    "verify_crc",
    "run_crc_demo",
]
