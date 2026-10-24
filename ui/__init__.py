"""User Interface and visualization package for NetSim-X (Member 3).

Includes Streamlit components, controls, topology visualizers, dashboards,
protocol labs, and the Explainable Adaptive Routing (XAR) adapter.
"""

from ui.controls import render_disruption_tab, render_sidebar_controls
from ui.dashboard import build_comparison_benchmark, render_algorithm_comparison_tab, render_comparison_dashboard
from ui.packet_view import render_packet_simulation_tab, render_packet_simulation_view
from ui.protocol_lab import render_protocol_lab_tab
from ui.topology_view import draw_topology_graph, render_topology_view
from ui.xar_adapter import (
    FALLBACK_ALGO_LABEL,
    FALLBACK_BADGE_TEXT,
    REAL_ALGO_LABEL,
    generate_xar_explanation,
    resolve_xar_route,
    score_path_by_spec,
)

__all__ = [
    "draw_topology_graph",
    "render_topology_view",
    "render_sidebar_controls",
    "render_disruption_tab",
    "render_comparison_dashboard",
    "render_algorithm_comparison_tab",
    "render_packet_simulation_view",
    "render_packet_simulation_tab",
    "render_protocol_lab_tab",
    "resolve_xar_route",
    "score_path_by_spec",
    "generate_xar_explanation",
    "build_comparison_benchmark",
    "FALLBACK_BADGE_TEXT",
    "FALLBACK_ALGO_LABEL",
    "REAL_ALGO_LABEL",
]
