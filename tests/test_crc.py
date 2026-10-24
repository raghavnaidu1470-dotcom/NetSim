"""Tests for Cyclic Redundancy Check (CRC) error detection (Member 3)."""

from __future__ import annotations

import pytest

from protocols.crc import (
    CRC_4,
    CRC_8,
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


def test_compute_crc_modulo2() -> None:
    data = "11010011101100"
    poly = "1011"
    checksum = compute_crc(data, poly)
    assert checksum == "100"
    assert len(checksum) == len(poly) - 1
    assert verify_crc(data + checksum, poly) is True


def test_crc_known_vector_spec_example() -> None:
    """Worked example from docs/spec.md section 5 / UI Protocol Lab: data=1101011011, poly=10011 -> 1110."""
    data = "1101011011"
    poly = CRC_4  # 10011
    rem, steps = crc_remainder(data, poly)
    assert rem == "1110"
    assert len(steps) > 0

    frame = crc_encode(data, poly)
    assert frame == "11010110111110"
    assert crc_check(frame, poly) is True


def test_crc_8_polynomial_vector() -> None:
    data = "1101011011"
    poly = CRC_8  # 100000111
    rem, _ = crc_remainder(data, poly)
    assert len(rem) == len(poly) - 1
    encoded = crc_encode(data, poly)
    assert crc_check(encoded, poly) is True


def test_verify_crc_corrupted_frame() -> None:
    data = "1101"
    poly = "1011"
    checksum = compute_crc(data, poly)
    corrupted_frame = "0" + (data + checksum)[1:]  # Flip first bit
    assert verify_crc(corrupted_frame, poly) is False


def test_corrupt_bits_helper() -> None:
    original = "110100"
    flipped_0 = corrupt_bits(original, 0)
    assert flipped_0 == "010100"

    flipped_multi = corrupt_bits(original, [0, 5])
    assert flipped_multi == "010101"

    # Out of range raises IndexError
    with pytest.raises(IndexError):
        corrupt_bits(original, 10)
    with pytest.raises(IndexError):
        corrupt_bits(original, -1)


def test_corrupt_bits_detected_by_crc() -> None:
    data = "1101011011"
    poly = CRC_4
    encoded = crc_encode(data, poly)
    assert crc_check(encoded, poly) is True

    # Corrupt every single bit position individually and assert CRC detects each
    for pos in range(len(encoded)):
        corrupted = corrupt_bits(encoded, pos)
        assert crc_check(corrupted, poly) is False


def test_invalid_generator_and_bits_rejected() -> None:
    # Non-binary strings
    with pytest.raises(ValueError, match="only binary digits"):
        validate_bitstring("110201")
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_bitstring("")
    with pytest.raises(TypeError):
        validate_bitstring(12345)  # type: ignore

    # Generator validation
    with pytest.raises(ValueError, match="longer than 1 bit"):
        validate_generator("1")
    with pytest.raises(ValueError, match="must start with '1'"):
        validate_generator("01011")


def test_run_crc_demo() -> None:
    demo = run_crc_demo(data_bits="110101", polynomial="1101", corrupt_bit_index=-1)
    assert demo["is_valid"] is True
    assert demo["error_injected"] is False
    assert len(demo["division_steps"]) > 0

    demo_corrupt = run_crc_demo(data_bits="110101", polynomial="1101", corrupt_bit_index=2)
    assert demo_corrupt["is_valid"] is False
    assert demo_corrupt["error_injected"] is True
