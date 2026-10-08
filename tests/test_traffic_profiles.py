"""Tests for XAR traffic profile weights and retrieval (Member 2)."""

import pytest

from adaptive.traffic_profiles import TRAFFIC_PROFILES, get_profile_weights


def test_traffic_profiles_weights_sum_to_one() -> None:
    for name, p in TRAFFIC_PROFILES.items():
        total = p.w_h + p.w_l + p.w_c + p.w_p + p.w_r
        assert abs(total - 1.0) < 1e-4, f"Profile {name} weights do not sum to 1.0"


def test_real_time_profile_prioritizes_latency() -> None:
    rt = get_profile_weights("real_time")
    assert rt.w_l > rt.w_p
    assert rt.w_p > rt.w_c
    assert rt.w_c > rt.w_h


def test_reliable_profile_prioritizes_loss_and_reliability() -> None:
    rel = get_profile_weights("reliable_data_transfer")
    assert rel.w_p > rel.w_l
    assert rel.w_r > rel.w_l
    assert rel.w_l > rel.w_h


def test_get_profile_weights_fallback() -> None:
    weights = get_profile_weights("unknown_custom_profile")
    assert weights == TRAFFIC_PROFILES["standard"]
