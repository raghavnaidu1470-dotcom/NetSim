"""Cyclic Redundancy Check (CRC) error detection demonstration (Member 3).

Demonstrates bitwise polynomial division, checksum generation, transmission corruption,
and receiver-side syndrome verification using modulo-2 division.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

CRC_4 = "10011"       # x^4 + x + 1
CRC_8 = "100000111"   # x^8 + x^2 + x + 1
CRC_3 = "1011"        # x^3 + x + 1

CRC_POLYNOMIALS: Dict[str, str] = {
    "CRC-4": CRC_4,
    "CRC-8": CRC_8,
    "CRC-3": CRC_3,
}


class CRCDivisionStep(TypedDict):
    """Step in modulo-2 polynomial long division."""
    step_index: int
    bit_index: int
    current_dividend: str
    divisor: str
    intermediate_remainder: str


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


def validate_bitstring(bits: str, name: str = "bits") -> None:
    """Validate that input is a non-empty string consisting only of '0' and '1'.

    Args:
        bits: String to validate.
        name: Parameter name for error message.

    Raises:
        TypeError: If bits is not a string.
        ValueError: If bits is empty or contains characters other than '0' and '1'.
    """
    if not isinstance(bits, str):
        raise TypeError(f"{name} must be a string, got {type(bits).__name__}")
    if not bits:
        raise ValueError(f"{name} cannot be empty")
    if not all(c in "01" for c in bits):
        raise ValueError(f"{name} must contain only binary digits ('0' or '1'), got: '{bits}'")


def validate_generator(generator: str) -> None:
    """Validate generator polynomial string.

    Args:
        generator: Divisor polynomial bitstring.

    Raises:
        TypeError: If generator is not a string.
        ValueError: If generator is invalid (length <= 1, non-binary, or doesn't start with '1').
    """
    validate_bitstring(generator, name="generator polynomial")
    if len(generator) <= 1:
        raise ValueError(f"Generator polynomial must be longer than 1 bit, got length {len(generator)}")
    if not generator.startswith("1"):
        raise ValueError(f"Generator polynomial must start with '1', got: '{generator}'")


def crc_remainder(
    data_bits: str, generator_bits: str
) -> Tuple[str, List[CRCDivisionStep]]:
    """Compute CRC checksum remainder using modulo-2 polynomial division (XOR).

    Appends (len(generator_bits) - 1) zeros to data_bits, then performs bitwise
    XOR long division, returning the final remainder and a step-by-step trace.

    Args:
        data_bits: Binary message string (e.g. '1101011011').
        generator_bits: Binary divisor polynomial (e.g. '10011' for CRC-4).

    Returns:
        Tuple of (remainder_bitstring, list_of_division_steps).

    Example:
        >>> rem, steps = crc_remainder("1101011011", "10011")
        >>> rem
        '1110'
    """
    validate_bitstring(data_bits, name="data_bits")
    validate_generator(generator_bits)

    k = len(generator_bits) - 1
    padded_bits = data_bits + ("0" * k)
    dividend = list(padded_bits)
    gen_len = len(generator_bits)

    steps: List[CRCDivisionStep] = []

    for i in range(len(data_bits)):
        if dividend[i] == "1":
            step_record: CRCDivisionStep = {
                "step_index": len(steps) + 1,
                "bit_index": i,
                "current_dividend": "".join(dividend),
                "divisor": generator_bits,
                "intermediate_remainder": "",
            }
            for j in range(gen_len):
                dividend[i + j] = str(int(dividend[i + j]) ^ int(generator_bits[j]))
            step_record["intermediate_remainder"] = "".join(dividend)
            steps.append(step_record)

    remainder = "".join(dividend[-k:]) if k > 0 else ""
    return remainder, steps


def crc_encode(data_bits: str, generator: str) -> str:
    """Encode message by appending the calculated CRC remainder to data bits.

    Args:
        data_bits: Binary message string.
        generator: Divisor polynomial bitstring.

    Returns:
        Transmitted frame bitstring = data_bits + remainder.

    Example:
        >>> crc_encode("1101011011", "10011")
        '11010110111110'
    """
    remainder, _ = crc_remainder(data_bits, generator)
    return data_bits + remainder


def crc_check(received_bits: str, generator: str) -> bool:
    """Check received frame integrity by performing modulo-2 division over entire frame.

    If remainder (syndrome) is all zeros, the frame is valid. Otherwise, corrupted.

    Args:
        received_bits: Data bits concatenated with CRC checksum.
        generator: Divisor polynomial bitstring.

    Returns:
        True if remainder is all zeros (valid frame), False if corrupted.

    Example:
        >>> crc_check("11010110111110", "10011")
        True
        >>> crc_check("01010110111110", "10011")
        False
    """
    validate_bitstring(received_bits, name="received_bits")
    validate_generator(generator)

    k = len(generator) - 1
    if len(received_bits) < len(generator):
        return False

    dividend = list(received_bits)
    gen_len = len(generator)

    for i in range(len(received_bits) - k):
        if dividend[i] == "1":
            for j in range(gen_len):
                dividend[i + j] = str(int(dividend[i + j]) ^ int(generator[j]))

    syndrome = "".join(dividend[-k:]) if k > 0 else ""
    return syndrome == ("0" * k)


def corrupt_bits(bits: str, positions: Union[int, List[int]]) -> str:
    """Invert bit value (0->1, 1->0) at specified index positions (0-indexed).

    Args:
        bits: Binary bitstring to corrupt.
        positions: Single index or list of index positions to invert.

    Returns:
        Corrupted bitstring.

    Raises:
        IndexError: If any position is out of bounds [0, len(bits)-1].
    """
    validate_bitstring(bits, name="bits")
    bit_list = list(bits)
    idx_list = [positions] if isinstance(positions, int) else positions

    for pos in idx_list:
        if pos < 0 or pos >= len(bits):
            raise IndexError(f"Bit position {pos} out of range [0, {len(bits) - 1}]")
        bit_list[pos] = "1" if bit_list[pos] == "0" else "0"

    return "".join(bit_list)


def compute_crc(data_bits: str, polynomial: str = "1101") -> str:
    """Compute CRC checksum bits using modulo-2 polynomial division (XOR).

    Args:
        data_bits: Binary message string.
        polynomial: Divisor polynomial bitstring (default '1101' for CRC-3).

    Returns:
        Remainder checksum bitstring of length len(polynomial) - 1.
    """
    remainder, _ = crc_remainder(data_bits, polynomial)
    return remainder


def verify_crc(received_bits: str, polynomial: str = "1101") -> bool:
    """Verify whether a received frame contains transmission errors using CRC.

    Args:
        received_bits: Data bits concatenated with checksum.
        polynomial: Divisor polynomial bitstring.

    Returns:
        True if remainder is all zeros (valid frame), False if corrupted.
    """
    return crc_check(received_bits, polynomial)


def run_crc_demo(
    data_bits: str = "1101011011",
    polynomial: str = "10011",  # CRC-4
    corrupt_bit_index: int = -1,
) -> CRCDemoResult:
    """Execute complete end-to-end CRC sender/receiver flow.

    Args:
        data_bits: Message bits to encode.
        polynomial: Divisor polynomial bitstring (default '10011' for CRC-4).
        corrupt_bit_index: Position to corrupt (-1 for no corruption).

    Returns:
        CRCDemoResult dictionary detailing sender and receiver state and division steps.
    """
    remainder, steps = crc_remainder(data_bits, polynomial)
    transmitted_frame = data_bits + remainder

    error_injected = False
    if corrupt_bit_index >= 0:
        received_frame = corrupt_bits(transmitted_frame, corrupt_bit_index)
        error_injected = True
    else:
        received_frame = transmitted_frame

    # Receiver division
    k = len(polynomial) - 1
    dividend = list(received_frame)
    gen_len = len(polynomial)
    for i in range(len(received_frame) - k):
        if dividend[i] == "1":
            for j in range(gen_len):
                dividend[i + j] = str(int(dividend[i + j]) ^ int(polynomial[j]))
    syndrome = "".join(dividend[-k:]) if k > 0 else ""
    is_valid = syndrome == ("0" * k)

    formatted_steps = [
        f"Step {s['step_index']}: Bit {s['bit_index']} is 1 -> XOR with {s['divisor']}"
        for s in steps
    ]

    return {
        "data_bits": data_bits,
        "polynomial": polynomial,
        "crc_checksum": remainder,
        "transmitted_frame": transmitted_frame,
        "received_frame": received_frame,
        "error_injected": error_injected,
        "syndrome": syndrome,
        "is_valid": is_valid,
        "division_steps": formatted_steps,
    }
