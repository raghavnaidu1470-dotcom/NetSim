"""Tests for Cyclic Redundancy Check (CRC) error detection (Member 3)."""

import pytest

from protocols.crc import compute_crc, run_crc_demo, verify_crc


@pytest.mark.skip(reason="Member 3 to implement compute_crc")
def test_compute_crc_modulo2() -> None:
    data = "11010011101100"
    poly = "1011"
    checksum = compute_crc(data, poly)
    assert len(checksum) == len(poly) - 1
    assert verify_crc(data + checksum, poly) is True


@pytest.mark.skip(reason="Member 3 to implement verify_crc with error")
def test_verify_crc_corrupted_frame() -> None:
    data = "1101"
    poly = "1011"
    checksum = compute_crc(data, poly)
    corrupted_frame = "0" + (data + checksum)[1:]  # Flip first bit
    assert verify_crc(corrupted_frame, poly) is False


@pytest.mark.skip(reason="Member 3 to implement run_crc_demo")
def test_run_crc_demo() -> None:
    demo = run_crc_demo(data_bits="110101", polynomial="1101", corrupt_bit_index=-1)
    assert demo["is_valid"] is True
    assert demo["error_injected"] is False
