"""Protocols demonstration package for NetSim-X (Member 3).

Includes transport-layer TCP/UDP comparisons and CRC error detection demos.
"""

from protocols.crc import (
    CRC_3,
    CRC_4,
    CRC_8,
    CRC_POLYNOMIALS,
    CRCDemoResult,
    CRCDivisionStep,
    compute_crc,
    corrupt_bits,
    crc_check,
    crc_encode,
    crc_remainder,
    run_crc_demo,
    validate_bitstring,
    validate_generator,
    verify_crc,
)
from protocols.tcp_udp import (
    TCPEvent,
    TCPSimulationResult,
    TCPSimulationSummary,
    UDPEvent,
    UDPSimulationResult,
    UDPSimulationSummary,
    simulate_tcp,
    simulate_tcp_stream,
    simulate_udp,
    simulate_udp_stream,
)

__all__ = [
    "CRC_3",
    "CRC_4",
    "CRC_8",
    "CRC_POLYNOMIALS",
    "CRCDemoResult",
    "CRCDivisionStep",
    "compute_crc",
    "corrupt_bits",
    "crc_check",
    "crc_encode",
    "crc_remainder",
    "run_crc_demo",
    "validate_bitstring",
    "validate_generator",
    "verify_crc",
    "TCPEvent",
    "TCPSimulationResult",
    "TCPSimulationSummary",
    "UDPEvent",
    "UDPSimulationResult",
    "UDPSimulationSummary",
    "simulate_tcp",
    "simulate_tcp_stream",
    "simulate_udp",
    "simulate_udp_stream",
]
