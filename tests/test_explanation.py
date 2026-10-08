"""Tests for route explanation and comparison engine (Member 2)."""

import pytest

from adaptive.explanation import compare_routes
from network.topology import Topology


@pytest.mark.skip(reason="Member 2 to implement compare_routes")
def test_compare_routes_explanation_text(linear_topology: Topology) -> None:
    path_a = ["PC1", "R1", "PC2"]
    path_b = ["PC1", "PC2"]  # hypothetical alternative
    comp = compare_routes(linear_topology, path_a, path_b, profile="standard")

    assert "explanation_text" in comp
    assert isinstance(comp["explanation_text"], str)
    assert len(comp["explanation_text"]) > 10
    assert "deltas" in comp
