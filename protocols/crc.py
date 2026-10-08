"""Cyclic Redundancy Check (CRC) error detection demonstration (Member 3).

Demonstrates bitwise polynomial division, checksum generation, transmission corruption,
and receiver-side syndrome verification.
"""

from __future__ import annotations

import random
from typing import List, Tuple, TypedDict


class CRCDemoResult(TypedDict):
    """Result of CRC generation, error injection, and verification."""
    data_bits: str
    polynomial: str
    crc_checksum: str
    transmitted_frame: str
    received_frame: str
    error_injected: bool
    syndrome: str
    is_valid: bool
    division_steps: List[str]


def compute_crc(data_bits: str, polynomial: str = "1101") -> str:
    """Compute CRC checksum bits using modulo-2 polynomial division (XOR).

    Args:
        data_bits: Binary string message (e.g. '11010011101100').
        polynomial: Divisor polynomial bitstring (e.g. '1101' for CRC-3).

    Returns:
        Remainder checksum bitstring of length len(polynomial) - 1.

    Raises:
        NotImplementedError: If not yet implemented by Member 3.
    """
    # TODO(Member 3 - Step 1): Validate binary strings (only '0' and '1').
    # TODO(Member 3 - Step 2): Append len(poly)-1 zeros to data_bits.
    # TODO(Member 3 - Step 3): Perform bitwise XOR long division.
    # TODO(Member 3 - Step 4): Return remainder string.
    raise NotImplementedError("Member 3 to implement compute_crc in protocols/crc.py")


def verify_crc(received_bits: str, polynomial: str = "1101") -> bool:
    """Verify whether a received frame contains transmission errors using CRC.

    Args:
        received_bits: Data bits concatenated with checksum.
        polynomial: Divisor polynomial bitstring.

    Returns:
        True if remainder is all zeros (valid frame), False if corrupted.

    Raises:
        NotImplementedError: If not yet implemented by Member 3.
    """
    # TODO(Member 3 - Step 1): Run polynomial division over received_bits.
    # TODO(Member 3 - Step 2): Return True if remainder is '0' * (len(poly)-1), else False.
    raise NotImplementedError("Member 3 to implement verify_crc in protocols/crc.py")


def run_crc_demo(
    data_bits: str = "1101011011",
    polynomial: str = "10011",  # CRC-4
    corrupt_bit_index: int = -1,
) -> CRCDemoResult:
    """Execute complete end-to-end CRC sender/receiver flow.

    Raises:
        NotImplementedError: If not yet implemented by Member 3.
    """
    # TODO(Member 3 - Step 1): Generate checksum via compute_crc.
    # TODO(Member 3 - Step 2): Construct transmitted_frame = data_bits + checksum.
    # TODO(Member 3 - Step 3): Inject error if corrupt_bit_index >= 0.
    # TODO(Member 3 - Step 4): Verify at receiver via verify_crc.
    # TODO(Member 3 - Step 5): Return CRCDemoResult.
    raise NotImplementedError("Member 3 to implement run_crc_demo in protocols/crc.py")
