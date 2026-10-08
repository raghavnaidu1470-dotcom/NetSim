"""Tests for UI drawing and dashboard rendering logic (Member 3)."""

import matplotlib.pyplot as plt

from network.topology import Topology
from ui.topology_view import draw_topology_graph


def test_draw_topology_graph_returns_figure(linear_topology: Topology) -> None:
    fig = draw_topology_graph(linear_topology, highlighted_path=["PC1", "R1", "PC2"])
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
